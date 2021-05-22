# Generated by Django 3.1.6 on 2021-05-21 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0043_auto_20210517_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='expedition',
            name='tag',
            field=models.CharField(blank=True, help_text='Enter a tag for this recommended expedition. (e.g. 5day)', max_length=50),
        ),
    ]