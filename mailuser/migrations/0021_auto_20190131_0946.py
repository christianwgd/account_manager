# Generated by Django 2.1.5 on 2019-01-31 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailuser', '0020_auto_20190130_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirection',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailuser.Account', verbose_name='account'),
        ),
    ]