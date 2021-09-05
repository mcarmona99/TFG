# Generated by Django 3.1.7 on 2021-09-05 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Interface', '0012_sesion_raw_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesion',
            name='datos_inicio',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sesion',
            name='datos_mercado',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sesion',
            name='marco_tiempo',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
