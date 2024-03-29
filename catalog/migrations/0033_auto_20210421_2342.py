# Generated by Django 3.1.4 on 2021-04-21 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0032_auto_20210421_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodation',
            name='price_from',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Insert price from.', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='accommodation',
            name='price_to',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Insert price to.', max_digits=10, null=True),
        ),
    ]
