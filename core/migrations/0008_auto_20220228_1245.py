# Generated by Django 3.2 on 2022-02-28 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_servicebooking_service_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicebooking',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicebooking',
            name='payable_amount',
            field=models.FloatField(default=0),
        ),
    ]
