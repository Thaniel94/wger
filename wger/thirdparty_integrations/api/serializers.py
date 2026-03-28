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
from wger.thirdparty_integrations.models import IntegrationSource, UserIntegrationSource

class IntegrationSourceSerializer(serializers.ModelSerializer):
    """
    Integration Source serializer
    """

    name = serializers.CharField()
    display_name = serializers.CharField()
    priority = serializers.IntegerField()
    energy_burned_import_multiplier = serializers.FloatField()

    # user = serializers.PrimaryKeyRelatedField(
    #     read_only=True, default=serializers.CurrentUserDefault()
    # )

    class Meta:
        model = IntegrationSource
        fields = (
            'name',
            'display_name',
            'priority',
            'energy_burned_import_multiplier'
        )

class UserIntegrationSourceSerializer(serializers.ModelSerializer):
    """
    User Integration Source serializer
    """

    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserIntegrationSource
        fields = (
            'integration_source',
            'user',
            'priority',
            'energy_burned_import_multiplier',
            'last_sync_time'
        )

class WeightEntrySerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    value = serializers.FloatField()
    source = serializers.CharField()

class StepsEntrySerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    value = serializers.FloatField()
    source = serializers.CharField()

class EnergyBurnedEntrySerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    value = serializers.FloatField()
    source = serializers.CharField()

class HealthConnectSyncTimeSerializer(serializers.Serializer):
    date = serializers.DateTimeField()

class HealthConnectImportSerializer(serializers.Serializer):
    """
    Health Connect serializer
    """
    weights = WeightEntrySerializer(many=True, required=False)
    steps = StepsEntrySerializer(many=True, required=False)
    energy_burned = EnergyBurnedEntrySerializer(many=True, required=False)

