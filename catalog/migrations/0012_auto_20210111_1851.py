# Generated by Django 3.1.4 on 2021-01-11 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_auto_20210106_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expedition',
            name='number_of_people',
            field=models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], help_text='Select how many people. (Can be changed later)'),
        ),
        migrations.AlterField(
            model_name='expedition',
            name='recommended',
            field=models.BooleanField(default=True, help_text='Is this a recommended trip by agency?'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='date_last_edit',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
