# Generated by Django 3.0.1 on 2020-01-03 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenge', '0003_auto_20200102_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='stock_industry',
            field=models.CharField(default='Tech', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='challenge',
            name='stock_sector',
            field=models.CharField(default='tech', max_length=256),
            preserve_default=False,
        ),
    ]
