# Generated by Django 4.2 on 2025-02-18 18:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models.mixins.uid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('NeuroMail', '0004_emailattachment_s3_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempMail',
            fields=[
                ('id', models.CharField(editable=False, max_length=15, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tempmail', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
                'abstract': False,
            },
            bases=(models.Model, main.models.mixins.uid.UIDMixin),
        ),
    ]
