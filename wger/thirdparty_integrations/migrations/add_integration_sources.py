# -*- coding: utf-8 -*-

from django.db import models, migrations

def create_sources(apps, schema_editor):
    IntegrationSource = apps.get_model(
        "thirdparty_integrations",
        "IntegrationSource"
    )

    IntegrationSource.objects.get_or_create(
        name="manual",
        display_name="Manual",
        order=1
    )

    IntegrationSource.objects.get_or_create(
        name="health_connect",
        display_name="Health Connect",
        order=2
    )

    IntegrationSource.objects.get_or_create(
        name="polar",
        display_name="Polar",
        order=3
    )

class Migration(migrations.Migration):
    dependencies = [
        ('thirdparty_integrations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_sources)
    ]
