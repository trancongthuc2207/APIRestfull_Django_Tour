# Generated by Django 4.1.7 on 2023-03-08 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traveling', '0002_alter_tour_address_tour_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingvote',
            name='amount_star_voting',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
