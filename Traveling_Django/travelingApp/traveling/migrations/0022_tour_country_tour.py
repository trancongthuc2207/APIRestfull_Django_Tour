# Generated by Django 4.2 on 2023-04-13 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traveling', '0021_bill_method_pay_bill_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='country_tour',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
