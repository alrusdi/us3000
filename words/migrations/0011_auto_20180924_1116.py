# Generated by Django 2.1 on 2018-09-24 08:16

from django.db import migrations
import jsonfield.encoder
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0010_meaning_examples'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pronunciation',
            name='raw_od_data',
            field=jsonfield.fields.JSONField(blank=True, dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={}, null=True, verbose_name='Сырые данные с OD'),
        ),
        migrations.AlterField(
            model_name='word',
            name='raw_od_article',
            field=jsonfield.fields.JSONField(dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={}, verbose_name='Сырые данные с OD'),
        ),
    ]