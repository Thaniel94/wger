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

# Standard Library
import csv
import logging

# Django
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.utils.translation import gettext as _

# Third Party
from formtools.preview import FormPreview

# wger
from wger.weight import helpers
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)

class HealthConnectImportView(FormPreview):
    @login_required
    def post(self, request):
        from wger.thirdparty_integrations.services.health_connect import HealthConnectService

        HealthConnectService.import_health_connect_data(request.user, request.data)

        return Response({"status": "ok"})