# Generated by Django 3.1.4 on 2021-04-28 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0037_trip_days_up_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='expedition',
            name='single_trip',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='trip',
            name='days_up_to',
            field=models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], help_text='Select up to how many days.', null=True),
        ),
    ]
