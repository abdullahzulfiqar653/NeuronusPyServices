# Generated by Django 4.2 on 2024-12-23 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NeuroDrive', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='is_starred',
            field=models.BooleanField(default=False),
        ),
    ]
