# Generated by Django 2.1.5 on 2019-01-24 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailuser', '0011_auto_20190124_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='man_url',
            field=models.URLField(blank=True, null=True, verbose_name='manual url'),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='weburl',
            field=models.URLField(blank=True, null=True, verbose_name='web url'),
        ),
    ]