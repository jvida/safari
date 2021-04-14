# Generated by Django 3.1.6 on 2021-04-07 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0027_auto_20210406_0318'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailyplan',
            old_name='name',
            new_name='title',
        ),
        migrations.AlterField(
            model_name='expedition',
            name='date_from',
            field=models.DateField(blank=True, help_text='Select a time window in which You wish to join us for an advanture.', null=True),
        ),
        migrations.AlterField(
            model_name='expedition',
            name='number_of_people',
            field=models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], help_text='Select how many people.', null=True),
        ),
    ]