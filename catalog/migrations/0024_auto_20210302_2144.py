# Generated by Django 3.1.6 on 2021-03-02 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0023_auto_20210302_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='park',
            name='picture',
            field=models.ImageField(help_text='Upload an image.', upload_to='park_imgs/'),
        ),
    ]
