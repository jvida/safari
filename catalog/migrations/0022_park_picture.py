# Generated by Django 3.1.6 on 2021-03-02 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_auto_20210228_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='picture',
            field=models.ImageField(default='null', help_text='Upload an image.', upload_to=''),
            preserve_default=False,
        ),
    ]