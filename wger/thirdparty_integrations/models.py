#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) wger Team
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
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

class IntegrationSource(models.Model):
    """
    Model for each third party integration source
    """

    name = models.CharField(max_length=100, unique=True, verbose_name='Name', default="Source")

    display_name = models.CharField(max_length=100, verbose_name='Display Name', null=True)

    priority = models.IntegerField(null=False, verbose_name='Priority')
    """
    Priority in ascending order (1 = use first)
    """

    energy_burned_import_multiplier = models.DecimalField(null=False, 
                                                          default=1.0, 
                                                          verbose_name='Energy Burned Import Multiplier', 
                                                          decimal_places=2,
                                                          max_digits=10)

    class Meta:
        """
        Metaclass to set some other properties
        """

        verbose_name = 'Integration source'
        ordering = [
            'priority',
        ]
        get_latest_by = 'priority'

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return '{0} - {1}'.format(self.name, self.priority)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

class UserIntegrationSource(models.Model):
    """
    Pivot table for each third party integration source and user, storing config and overrides per source per user
    """

    integration_source = models.ForeignKey(
        IntegrationSource,
        verbose_name='Integration source',
        on_delete=models.CASCADE
    )
    """
    The integration source being configured (e.g. Health Connect).
    """

    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
    )
    """
    The user the integration source config belongs to.

    NOTE: this field is neither marked as editable false nor is it excluded in
    the form. This is done intentionally because otherwise it's *very* difficult
    and ugly to validate the uniqueness of unique_together fields and one field
    is excluded from the form. This does not pose any security risk because the
    value from the form is ignored and the request's user always used.
    """

    priority = models.IntegerField(null=True, verbose_name='Priority')
    """
    Priority in ascending order (1 = use first)
    """

    energy_burned_import_multiplier = models.DecimalField(null=True, 
                                                          verbose_name='Energy Burned Import Multiplier', 
                                                          decimal_places=2,
                                                          max_digits=10)
    """
    Multiplier to increase/decrease imported energy burn values to account for consistent under/over estimates
    """

    last_sync_time = models.DateTimeField(null=True,
        verbose_name='Last sync time')

    class Meta:
        """
        Metaclass to set some other properties
        """

        unique_together = ('user', 'integration_source')

        verbose_name = 'Integration source'
        ordering = [
            'priority',
        ]
        get_latest_by = 'priority'

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return '{0} - {1}'.format(self.name, self.priority)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self