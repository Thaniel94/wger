# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Third Party
from rest_framework import serializers

# wger
from wger.activity.models import EnergyBurnedEntry
from wger.activity.models import StepsEntry


class EnergyBurnedEntrySerializer(serializers.ModelSerializer):
    """
    EnergyBurned serializer
    """

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = EnergyBurnedEntry
        fields = (
            'id',
            'date',
            'energy_burned',
            'user',
        )


class StepsEntrySerializer(serializers.ModelSerializer):
    """
    Steps serializer
    """

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = StepsEntry
        fields = (
            'id',
            'date',
            'steps',
            'user',
        )

