# Generated by Django 3.0.1 on 2020-01-01 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteuser',
            name='completed_challenges',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='siteuser',
            name='upcoming_challenges',
            field=models.TextField(blank=True),
        ),
    ]
