# Generated by Django 4.2.6 on 2023-11-13 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiofile',
            name='main_points',
            field=models.TextField(blank=True, null=True),
        ),
    ]
