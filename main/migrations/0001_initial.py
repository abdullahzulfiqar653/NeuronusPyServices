# Generated by Django 4.2 on 2024-09-21 04:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models.mixins.uid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.CharField(editable=False, max_length=15, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(choices=[('number-of-emails', 'Number Of Emails'), ('storage-gb-each-email', 'Storage Gb Each Email')], max_length=100, unique=True)),
                ('unit', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('default', models.FloatField(default=0)),
            ],
            options={
                'verbose_name': 'Product Feature',
                'verbose_name_plural': 'Product Features',
            },
            bases=(models.Model, main.models.mixins.uid.UIDMixin),
        ),
        migrations.CreateModel(
            name='SubscriptionProduct',
            fields=[
                ('id', models.CharField(editable=False, max_length=15, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('updated_at', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, main.models.mixins.uid.UIDMixin),
        ),
        migrations.CreateModel(
            name='SubscriptionProductPrice',
            fields=[
                ('id', models.CharField(editable=False, max_length=15, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('nickname', models.CharField(max_length=256, null=True)),
                ('recurring_interval', models.CharField(max_length=30)),
                ('price', models.DecimalField(decimal_places=2, max_digits=4)),
                ('product', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='product_prices', to='main.subscriptionproduct')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, main.models.mixins.uid.UIDMixin),
        ),
        migrations.CreateModel(
            name='SubscriptionProductFeature',
            fields=[
                ('id', models.CharField(editable=False, max_length=15, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('value', models.PositiveIntegerField()),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_features', to='main.feature')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_features', to='main.subscriptionproduct')),
            ],
            options={
                'verbose_name': 'Product Feature Assignment',
                'verbose_name_plural': 'Product Feature Assignments',
                'unique_together': {('product', 'feature')},
            },
            bases=(models.Model, main.models.mixins.uid.UIDMixin),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.CharField(editable=False, max_length=15, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('end_at', models.DateTimeField(null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('unpaid', 'Unpaid'), ('paused', 'Paused'), ('trialing', 'Trialing'), ('past_due', 'Past Due'), ('canceled', 'Canceled'), ('incomplete', 'Incomplete'), ('incomplete_expired', 'Incomplete Expired')], default='active', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('is_free_trial', models.BooleanField(default=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='main.subscriptionproduct')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscription', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
            },
            bases=(models.Model, main.models.mixins.uid.UIDMixin),
        ),
        migrations.AddField(
            model_name='feature',
            name='products',
            field=models.ManyToManyField(through='main.SubscriptionProductFeature', to='main.subscriptionproduct'),
        ),
    ]