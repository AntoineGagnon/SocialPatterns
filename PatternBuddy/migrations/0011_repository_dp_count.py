# Generated by Django 2.0.2 on 2018-04-09 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PatternBuddy', '0010_repository_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='dp_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]