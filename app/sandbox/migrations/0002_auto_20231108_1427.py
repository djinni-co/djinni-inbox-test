# Generated by Django 3.2.23 on 2023-11-08 14:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sandbox", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="messagethread",
            name="candidate_suitability",
            field=models.FloatField(blank=True, default=0.0),
        )
    ]
