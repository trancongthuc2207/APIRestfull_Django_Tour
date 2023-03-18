# Generated by Django 4.1.7 on 2023-03-09 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traveling', '0006_alter_tour_image_tour_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='image_tour',
            field=models.ImageField(null=True, upload_to='travel/tour/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(null=True, upload_to='user/%Y/%m'),
        ),
    ]
