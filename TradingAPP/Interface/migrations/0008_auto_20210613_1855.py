# Generated by Django 3.1.7 on 2021-06-13 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Interface', '0007_auto_20210613_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='algoritmotrading',
            name='imagen',
            field=models.CharField(max_length=200),
        ),
    ]
