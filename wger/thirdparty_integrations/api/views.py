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
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# Django
from django.contrib.auth.decorators import login_required

# wger
from wger.thirdparty_integrations.api.filtersets import IntegrationSourceFilterSet
from wger.thirdparty_integrations.api.serializers import IntegrationSourceSerializer, UserIntegrationSourceSerializer, HealthConnectImportSerializer, HealthConnectSyncTimeSerializer
from wger.thirdparty_integrations.models import IntegrationSource, UserIntegrationSource

# class IntegrationSourceViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for nutrition plan objects
#     """

#     serializer_class = IntegrationSourceSerializer

#     is_private = True
#     ordering_fields = '__all__'
#     filterset_class = IntegrationSourceFilterSet
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """
#         Only allow access to appropriate objects
#         """
#         # REST API generation
#         if getattr(self, 'swagger_fake_view', False):
#             return IntegrationSource.objects.none()

#         return IntegrationSource.objects.filter(priority=self.request.query_params.get('priority'))

#     def perform_update(self, serializer):
#         """
#         Set the owner
#         """
#         serializer.save(id=self.request.id)

class UserIntegrationSourceViewSet(viewsets.ModelViewSet):
    serializer_class = UserIntegrationSourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserIntegrationSource.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='get-last-health-connect-sync-time', serializer_class=HealthConnectSyncTimeSerializer)
    def get(self, request):
        serializer=HealthConnectSyncTimeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        from wger.thirdparty_integrations.services.health_connect import HealthConnectService

        service = HealthConnectService()

        healthConnectIntegrationSource = service.get_health_connect_source(user=self.request.user)

        UserIntegrationSource.get()

        return Response({"status": "ok", "last_sync_time":healthConnectIntegrationSource.last_sync_time})

    @action(detail=False, methods=['post'], url_path='import-health-connect', serializer_class=HealthConnectImportSerializer)
    def post(self, request):
        serializer=HealthConnectImportSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        from wger.thirdparty_integrations.services.health_connect import HealthConnectService

        service = HealthConnectService()

        service.import_health_connect_data(
            request.user, 
            serializer.validated_data
        )

        return Response({"status": "ok"})