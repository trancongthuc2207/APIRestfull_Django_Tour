# Generated by Django 4.1.7 on 2023-03-22 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traveling', '0012_alter_tour_image_tour'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='image_tour',
            field=models.ImageField(null=True, upload_to='travel/tour/%Y/%m'),
        ),
    ]
