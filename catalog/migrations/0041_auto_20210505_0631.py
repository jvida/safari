# Generated by Django 3.1.4 on 2021-05-05 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0040_auto_20210505_0153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expedition',
            name='single_trip',
            field=models.BooleanField(null=True),
        ),
    ]
