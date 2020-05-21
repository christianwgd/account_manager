# Generated by Django 2.1.5 on 2019-01-29 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_account_redirect'),
    ]

    operations = [
        migrations.CreateModel(
            name='Redirection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.EmailField(max_length=254, unique=True, verbose_name='redirection')),
                ('description', models.CharField(blank=True, max_length=80, null=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'redirection',
                'verbose_name_plural': 'redirection',
                'ordering': ['address'],
            },
        ),
        migrations.RemoveField(
            model_name='alias',
            name='account',
        ),
        migrations.RemoveField(
            model_name='account',
            name='redirect',
        ),
        migrations.AddField(
            model_name='account',
            name='type',
            field=models.CharField(choices=[('1', 'Account'), ('2', 'Alias')], default='A', max_length=1, verbose_name='account type'),
        ),
        migrations.DeleteModel(
            name='Alias',
        ),
        migrations.AddField(
            model_name='redirection',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Account', verbose_name='Account'),
        ),
    ]