# Generated by Django 3.2.7 on 2021-10-01 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20210928_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='telefone',
            field=models.CharField(max_length=11, verbose_name='telefone'),
        ),
    ]
