# Generated by Django 2.1 on 2019-01-14 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0012_wordlearningstate_training_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordlearningstate',
            name='preferred_pronunciation',
            field=models.PositiveIntegerField(default=0, verbose_name='forvo id препочтительного произношения'),
        ),
    ]
