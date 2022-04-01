# Generated by Django 4.0.2 on 2022-04-01 08:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0023_alter_account_unique_together_account_comment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='type',
            field=models.CharField(choices=[('mail', 'mail accounts'), ('othr', 'passwords')], default='mail', max_length=4, verbose_name='Type'),
        ),
    ]
