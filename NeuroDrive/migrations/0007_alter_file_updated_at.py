# Generated by Django 4.2 on 2025-01-26 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("NeuroDrive", "0006_alter_file_metadata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="updated_at",
            field=models.TimeField(auto_now_add=True),
        ),
    ]
