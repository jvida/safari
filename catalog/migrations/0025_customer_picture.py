# Generated by Django 3.1.6 on 2021-03-16 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0024_auto_20210302_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='picture',
            field=models.ImageField(default='profile_imgs/anonymous-user.png', help_text='Upload an image.', upload_to='profile_imgs/'),
        ),
    ]
