# Generated by Django 3.1 on 2020-09-07 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_auto_20200902_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.CharField(max_length=20, null=True),
        ),
    ]