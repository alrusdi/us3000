# Generated by Django 2.1 on 2018-09-05 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0005_auto_20180901_1159'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='meaning',
            options={'ordering': ['order'], 'verbose_name': 'Доп. значение', 'verbose_name_plural': 'Доп. значения'},
        ),
        migrations.AddField(
            model_name='meaning',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
    ]
