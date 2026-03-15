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

    name = models.CharField(max_length=100, unique=True, verbose_name='Name'),
    display_name = models.CharField(max_length=100, unique=True, verbose_name='Display Name'),
    priority = models.IntegerField(null=False, verbose_name='Priority')

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
