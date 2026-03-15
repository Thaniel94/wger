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
from datetime import date
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
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)

# Health Connect settings from WGER_SETTINGS (defined in settings_global.py)
HEALTH_CONNECT_ENABLED = settings.WGER_SETTINGS['HEALTH_CONNECT_ENABLED']


class HealthConnectService:
    """
    Service class for importing health connect data

    This service handles:
    - Import of health connect data (steps, weight, calories, etc)
    """

    @classmethod
    def import_weights(cls, user: User, incoming_weights: List, max_batch: int) -> List[WeightEntry]:
        """
        Import weight entries for the user

        Imports a single weight entry per day.
        Only overwrites previously imported entries.
        Manual weight entries always take priority 
        Assigns 'bImported' flag in weight model:
        True - Imported entry, False - Manual entry.

        Args:
            user: The user to import the weight entry for
            date: The date of the weight entry
            incoming_weights: list of dictionary entries with keys "date", "value"
                "date": date of weight entry (year, month, day)
                "value": value of weight entry
            max_batch: maximum entries to save to the database per call

        Returns:
            List of imported weight entries
        """
        if cls.should_skip_user(user):
            return []

        dates = [w["date"] for w in incoming_weights]

        existing_weights = WeightEntry.objects.filter(user=user, date__in=dates)

        existing_dates = {date(w.date.year, w.date.month, w.date.day): w for w in existing_weights}

        to_create_or_update = []

        for incoming_w in incoming_weights:

            existing_w = existing_dates.get(incoming_w["date"])

            # Ignore any days with manual entries
            if existing_w and not existing_w.bImported:
                continue

            to_create_or_update.append(
                WeightEntry(
                    user=user,
                    date=incoming_w["date"],
                    weight=incoming_w["value"],
                    bImported=True
                )
            )

        if len(to_create_or_update) > 0:
            WeightEntry.objects.bulk_update(
                to_create_or_update,
                update_conflicts=True,
                update_fields=["weight"],
                unique_fields=["user","date"]
            )

