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

# Django
from django.utils import timezone
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.weight.models import WeightEntry


class HealthConnectImportTestCase(WgerTestCase):
    """
    Test health connect import endpoints
    """

    def test_import_health_data(self):
        """
        Test that the health connect import works
        """

        self.user_login('test')

        count_before = WeightEntry.objects.count()
        
        payload = {
            "data": {
                "weight" : [
                    {
                        "value": 80.5,
                        "date": "2026-03-20T10:00:00Z",
                        "source": "health_connect"
                    },
                    {
                        "value": 79.9,
                        "date": "2026-03-21T10:00:00Z",
                        "source": "health_connect"
                    },
                    {
                        "value": 81.3,
                        "date": "2026-03-22T10:00:00Z",
                        "source": "health_connect"
                    }],
                "energy_burned" : [{
                        "value": 2510,
                        "date": "2026-03-20T10:00:00Z",
                        "source": "health_connect"
                    },
                    {
                        "value": 3015,
                        "date": "2026-03-21T10:00:00Z",
                        "source": "health_connect"
                    },
                    {
                        "value": 3100,
                        "date": "2026-03-22T10:00:00Z",
                        "source": "health_connect"
                    }],
                "steps" : [
                    {
                        "value": 6000,
                        "date": "2026-03-20T10:00:00Z",
                        "source": "health_connect"
                    },
                    {
                        "value": 9010,
                        "date": "2026-03-21T10:00:00Z",
                        "source": "health_connect"
                    },
                    {
                        "value": 10000,
                        "date": "2026-03-22T10:00:00Z",
                        "source": "health_connect"
                    }]
            }
        }

        response = self.client.post(
            reverse('thirdparty-integrations:import-health-connect'),
            payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        count_after = WeightEntry.objects.count()

        self.assertGreater(count_after, count_before)
