# Generated by Django 4.1.7 on 2023-04-01 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traveling', '0018_alter_tour_amount_like_alter_tour_amount_people_tour_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='price_tour',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]