# Generated by Django 3.0.2 on 2020-02-06 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20200202_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalinfo',
            name='account_number',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
