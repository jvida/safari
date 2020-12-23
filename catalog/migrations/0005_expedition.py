# Generated by Django 3.1.4 on 2020-12-23 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20201223_0326'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expedition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_people', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], help_text='Select how many people.')),
                ('recommended', models.BooleanField(default=False, help_text='Is this a recommended trip by agency?')),
                ('trips', models.ManyToManyField(help_text='Select trips you wish to visit.', to='catalog.Trip')),
            ],
        ),
    ]