# Generated by Django 3.2.23 on 2023-11-10 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sandbox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagethread',
            name='scores',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
