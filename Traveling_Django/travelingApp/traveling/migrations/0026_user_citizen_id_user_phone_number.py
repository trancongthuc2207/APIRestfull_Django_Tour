# Generated by Django 4.2 on 2023-05-01 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traveling', '0025_likeblog'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='citizen_id',
            field=models.CharField(max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=12, null=True),
        ),
    ]
