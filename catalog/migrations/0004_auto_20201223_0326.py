# Generated by Django 3.1.4 on 2020-12-23 00:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20201221_0642'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='park',
            name='ideal_months',
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4)], help_text='Select how many days you wish to stay in this park.')),
                ('accommodation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.accommodation')),
                ('park', models.ForeignKey(help_text='Select a park for this trip.', on_delete=django.db.models.deletion.CASCADE, to='catalog.park')),
            ],
        ),
    ]
