# Generated by Django 2.1.5 on 2019-01-29 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_auto_20190129_0811'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='redirection',
            options={'ordering': ['email'], 'verbose_name': 'redirection', 'verbose_name_plural': 'redirections'},
        ),
        migrations.RemoveField(
            model_name='redirection',
            name='address',
        ),
        migrations.AddField(
            model_name='redirection',
            name='email',
            field=models.EmailField(default='', max_length=254, unique=True, verbose_name='email'),
            preserve_default=False,
        ),
    ]
