# Generated by Django 4.2 on 2025-01-26 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("NeuroDrive", "0005_alter_file_metadata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="metadata",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
