# Generated by Django 5.0.2 on 2025-04-27 11:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phoneNumber', models.CharField(max_length=24)),
                ('otp', models.TextField(blank=True, help_text='Encrypted OTP Value', null=True)),
                ('expiry', models.DateTimeField(blank=True, null=True)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SiteSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmsaasKey', models.TextField(help_text='Encrypted key for TMSaaS payment')),
                ('tmsaasBaseUrl', models.CharField(blank=True, max_length=300, null=True)),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otherName', models.CharField(blank=True, max_length=100, null=True)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='male', max_length=20)),
                ('dob', models.DateTimeField(blank=True, null=True)),
                ('phoneNumber', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.CharField(blank=True, max_length=300, null=True)),
                ('nin', models.CharField(blank=True, max_length=200, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='profile-picture')),
                ('active', models.BooleanField(default=False)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateUpdated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
