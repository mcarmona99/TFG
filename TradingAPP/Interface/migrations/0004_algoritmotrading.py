# Generated by Django 3.1.7 on 2021-06-13 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Interface', '0003_auto_20210613_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlgoritmoTrading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
            ],
        ),
    ]
