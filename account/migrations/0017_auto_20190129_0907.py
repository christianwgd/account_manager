# Generated by Django 2.1.5 on 2019-01-29 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_auto_20190129_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='type',
            field=models.CharField(choices=[('1', 'Account'), ('2', 'Alias')], default='1', max_length=1, verbose_name='account type'),
        ),
    ]
