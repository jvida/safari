# Generated by Django 3.1.6 on 2021-03-02 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0022_park_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='park',
            name='picture',
            field=models.ImageField(help_text='Upload an image.', upload_to='catalog/static/img/park_imgs/'),
        ),
    ]