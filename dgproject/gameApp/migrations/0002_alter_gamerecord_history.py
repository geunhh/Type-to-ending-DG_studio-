# Generated by Django 4.2.16 on 2024-11-20 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamerecord',
            name='history',
            field=models.JSONField(default=list),
        ),
    ]