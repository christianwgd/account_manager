# Generated by Django 2.1.5 on 2019-01-23 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20190123_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='description',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='description'),
        ),
    ]