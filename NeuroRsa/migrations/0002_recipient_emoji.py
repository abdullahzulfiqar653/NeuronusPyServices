# Generated by Django 4.2 on 2024-10-21 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NeuroRsa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipient',
            name='emoji',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
