# Generated by Django 3.1.6 on 2021-04-06 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0026_feedback_date_of_trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='expedition',
            name='date_from',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expedition',
            name='date_to',
            field=models.DateField(blank=True, null=True),
        ),
    ]
