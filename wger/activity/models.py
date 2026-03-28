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

# wger
from wger.thirdparty_integrations.models import IntegrationSource


class EnergyBurnedEntry(models.Model):
    """
    Model for energy burned
    """

    date = models.DateField(verbose_name='Date')

    energy_burned = models.DecimalField(
        verbose_name='Energy burned',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(500)), MaxValueValidator(Decimal(15000))],
    )

    imported = models.BooleanField(
        verbose_name='bImported',
        default=False,
        null=False
    )
    
    source = models.ForeignKey(
        IntegrationSource,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
    )
    """
    The user the energy burned entry belongs to.

    NOTE: this field is neither marked as editable false nor is it excluded in
    the form. This is done intentionally because otherwise it's *very* difficult
    and ugly to validate the uniqueness of unique_together fields and one field
    is excluded from the form. This does not pose any security risk because the
    value from the form is ignored and the request's user always used.
    """

    class Meta:
        """
        Metaclass to set some other properties
        """

        verbose_name = 'Energy burned entry'
        ordering = [
            'date',
        ]
        get_latest_by = 'date'

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return '{0}: {1:.2f} kcal'.format(self.date, self.energy_burned)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

class StepsEntry(models.Model):
    """
    Model for a walked step
    """

    date = models.DateField(verbose_name='Date')

    steps = models.IntegerField(
        verbose_name='Steps',
        validators=[MaxValueValidator(int(1000000))],
    )
    
    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
    )
    """
    The user the steps entry belongs to.

    NOTE: this field is neither marked as editable false nor is it excluded in
    the form. This is done intentionally because otherwise it's *very* difficult
    and ugly to validate the uniqueness of unique_together fields and one field
    is excluded from the form. This does not pose any security risk because the
    value from the form is ignored and the request's user always used.
    """

    class Meta:
        """
        Metaclass to set some other properties
        """

        verbose_name = 'Steps entry'
        ordering = [
            'date',
        ]
        get_latest_by = 'date'

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return '{0} steps'.format(self.steps)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self
