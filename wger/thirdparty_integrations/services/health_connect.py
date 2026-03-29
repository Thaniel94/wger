#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import logging
from datetime import timedelta
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import (
    Dict,
    List,
    Optional,
)

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

# wger
from wger.thirdparty_integrations.models import IntegrationSource, UserIntegrationSource
from wger.weight.models import WeightEntry
from wger.activity.models import StepsEntry
from wger.activity.models import EnergyBurnedEntry


logger = logging.getLogger(__name__)

# Health Connect settings from WGER_SETTINGS (defined in settings_global.py)
HEALTH_CONNECT_ENABLED = True#settings.WGER_SETTINGS['HEALTH_CONNECT_ENABLED']


class HealthConnectService:
    _maximum_entries = 1000
    """
    Service class for importing health connect data

    This service handles:
    - Import of health connect data (steps, weight, calories, etc)
    - _maximum_entries sets the limit on how much data can be imported per call.
    """

    def __init__(self):
        pass

    @classmethod
    def import_health_connect_data(cls, user: User, data: List):
        """
        Import all health connect data for the user

        Splits incoming data into weight, energy burned, and steps, 
        Calls the relevant functions to add the seperated data into the database

        Args:
            user: The user to import the weight entry for
            data: The incoming health connect data
                Expected structure:
                {
                    "weights": [
                        {
                            "date": ISO8601 datetime,
                            "value": float,
                            "source": string
                        }
                    ],
                    "energy_burned": [
                        {
                            "date": ISO8601 datetime,
                            "value": float,
                            "source": string
                        }
                    ],
                    "steps": [
                        {
                            "date": ISO8601 datetime,
                            "value": int,
                            "source": string
                        }
                    ]
                }
        Returns:
            -
        """

        if (cls._maximum_entries < len(data)
                or not HEALTH_CONNECT_ENABLED):
            return

        cls._set_health_connect_source(user)

        weight_data = data.get("weights", [])
        cls._import_weights(user, weight_data, 50)

        energy_burned_data = data.get("energy_burned", [])
        cls._import_energy_burned(user, energy_burned_data, 50)

        steps_data = data.get("steps", [])
        cls._import_steps_walked(user, steps_data, 50)

        # Update last health connect sync time for user
        cls.user_health_connect_source.last_sync_time = max([
            max(entry["date"] for entry in weight_data),
            max(entry["date"] for entry in energy_burned_data),
            max(entry["date"] for entry in steps_data)
        ])

        cls.user_health_connect_source.save()

    @classmethod
    def _import_weights(cls, user: User, incoming_weights: List, max_batch: int) -> List[WeightEntry]:
        """
        Import weight entries for the user

        Imports a single weight entry per day.
        Only overwrites previously imported entries.
        Manual weight entries always take priority 
        Assigns 'imported' flag in weight model:
        True - Imported entry, False - Manual entry.

        Args:
            user: The user to import the weight entry for
            date: The date of the weight entry
            incoming_weights: list of dictionary entries with keys "date", "value"
                "date": date of weight entry (year, month, day)
                "value": value of weight entry
            max_batch: maximum entries to save to the database per call

        Returns:
            -
        """
        if cls._should_skip_user(user):
            return []

        dates = [w["date"] for w in incoming_weights]

        existing_weights = WeightEntry.objects.filter(user=user, date__in=dates)

        existing_dates = {date(w.date.year, w.date.month, w.date.day): w for w in existing_weights}

        to_create_or_update = []

        for incoming_w in incoming_weights:

            existing_w = existing_dates.get(incoming_w["date"])

            # Ignore any days with manual entries
            if existing_w and not existing_w.imported:
                continue

            # Ignore objects from sources with a higher priority
            if existing_w and existing_w.source.priority < cls._get_health_connect_source_priority():
                continue

            to_create_or_update.append(
                WeightEntry(
                    user=user,
                    date=incoming_w["date"],
                    weight=incoming_w["value"],
                    imported=True
                )
            )

        if len(to_create_or_update) > 0:
            WeightEntry.objects.bulk_create(
                to_create_or_update,
                update_conflicts=True,
                update_fields=["weight"],
                unique_fields=["user","date"]
            )

    @classmethod
    def _import_energy_burned(cls, user: User, incoming_energy_burned: List, max_batch: int) -> List[EnergyBurnedEntry]:
        """
        Import energy burned entries for the user, in kcal

        Imports a single energy burned entry per day.
        Only overwrites previously imported entries.
        Manual energy burned entries always take priority 
        Assigns 'imported' flag in energy burned model:
        True - Imported entry, False - Manual entry.

        Args:
            user: The user to import the weight entry for
            date: The date of the weight entry
            incoming_energy_burned: list of dictionary entries with keys "date", "value"
                "date": date of weight entry (year, month, day)
                "value": value of energy burned entry (kcal)
            max_batch: maximum entries to save to the database per call

        Returns:
            -
        """
        if cls._should_skip_user(user):
            return []

        dates = [eb["date"] for eb in incoming_energy_burned]
        #EnergyBurnedEntry.objects.all().delete()

        existing_energy_burned = EnergyBurnedEntry.objects.filter(user=user, date__in=dates)

        for eb in existing_energy_burned:
            try:
                _ = eb.some_decimal_field
            except Exception as e:
                print("Bad row:", eb.id, e)

        existing_dates = {date(eb.date.year, eb.date.month, eb.date.day): eb for eb in existing_energy_burned}

        to_create_or_update = []

        for incoming_e_b in incoming_energy_burned:

            existing_e_b = existing_dates.get(incoming_e_b["date"])

            # Ignore any days with manual entries
            if existing_e_b and not existing_e_b.imported:
                continue

            # Ignore objects from sources with a higher priority
            if existing_e_b and existing_e_b.source.priority < cls._get_health_connect_source_priority():
                continue

            print(str(incoming_e_b["date"].date()))

            to_create_or_update.append(
                EnergyBurnedEntry(
                    user=user,
                    date=incoming_e_b["date"].date(),
                    energy_burned=int(cls._safe_decimal(incoming_e_b["value"]) * cls._safe_decimal(cls.health_connect_source.energy_burned_import_multiplier)),
                    imported=True
                )
            )

        if len(to_create_or_update) > 0:
            EnergyBurnedEntry.objects.bulk_create(
                to_create_or_update,
                update_conflicts=True,
                update_fields=["energy_burned"],
                unique_fields=["user","date"]
            )

    @classmethod
    def _import_steps_walked(cls, user: User, incoming_steps_walked: List, max_batch: int) -> List[StepsEntry]:
        """
        Import steps walked entries for the user

        Imports a single steps entry per day.
        Only overwrites previously imported entries.
        Manual steps entries always take priority 
        Assigns 'imported' flag in step model:
        True - Imported entry, False - Manual entry.

        Args:
            user: The user to import the steps entry for
            date: The date of the steps entry
            incoming_steps_walked: list of dictionary entries with keys "date", "value"
                "date": date of steps walked entry (year, month, day)
                "value": value of steps entry
            max_batch: maximum entries to save to the database per call

        Returns:
            -
        """
        if cls._should_skip_user(user):
            return []

        dates = [w["date"] for w in incoming_steps_walked]

        existing_steps_walked = WeightEntry.objects.filter(user=user, date__in=dates)

        existing_dates = {date(w.date.year, w.date.month, w.date.day): w for w in existing_steps_walked}

        to_create_or_update = []

        for incoming_s_w in incoming_steps_walked:

            existing_s_w = existing_dates.get(incoming_s_w["date"])

            # Ignore any days with manual entries
            if existing_s_w and not existing_s_w.imported:
                continue

            # Ignore objects from sources with a higher priority
            if existing_s_w and existing_s_w.source.priority < cls._get_health_connect_source_priority():
                continue

            to_create_or_update.append(
                StepsEntry(
                    user=user,
                    date=incoming_s_w["date"],
                    steps=incoming_s_w["value"],
                    imported=True
                )
            )

        if len(to_create_or_update) > 0:
            StepsEntry.objects.bulk_create(
                to_create_or_update,
                update_conflicts=True,
                update_fields=["steps"],
                unique_fields=["user","date"]
            )

    @classmethod 
    def _should_skip_user(cls, user):
        return False

    @classmethod 
    def _set_health_connect_source(cls, user):
        health_connect_source = IntegrationSource.objects.get(name='health_connect')

        cls.health_connect_source = health_connect_source

        user_health_connect_source = UserIntegrationSource.objects.get_or_create(
            user=user,
            integration_source=health_connect_source
        )[0]

        cls.user_health_connect_source = user_health_connect_source

    def get_health_connect_source(cls, user):
        health_connect_source = IntegrationSource.objects.filter(name='health_connect')

        user_health_connect_source = UserIntegrationSource.objects.get_or_create(
            user=user,
            integration_source=health_connect_source
        )

        return user_health_connect_source

    def _get_health_connect_source_priority(cls):
        return (
            cls.user_health_connect_source.priority
            if cls.user_health_connect_source.priority is not None
            else cls.health_connect_source.priority
        )

    def _get_health_connect_source_energy_burned_import_multiplier(cls):
        return (
            cls.user_health_connect_source.energy_burned_import_multiplier
            if cls.user_health_connect_source.energy_burned_import_multiplier is not None
            else cls.health_connect_source.energy_burned_import_multiplier
        )
    
    @classmethod
    def _safe_decimal(cls, value):
        try:
            if value in [None, "", "null"]:
                return None
            d = Decimal(str(value))
            if d.is_nan():
                return None
            return d.quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError):
            return None