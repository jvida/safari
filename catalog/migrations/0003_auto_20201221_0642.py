# Generated by Django 3.1.4 on 2020-12-21 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20201221_0521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodation',
            name='price_from',
            field=models.DecimalField(decimal_places=2, help_text='Insert price from.', max_digits=10),
        ),
        migrations.AlterField(
            model_name='accommodation',
            name='price_to',
            field=models.DecimalField(decimal_places=2, help_text='Insert price to.', max_digits=10),
        ),
    ]
