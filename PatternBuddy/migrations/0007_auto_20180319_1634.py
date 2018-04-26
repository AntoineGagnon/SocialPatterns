# Generated by Django 2.0.3 on 2018-03-19 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PatternBuddy', '0006_contributor_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='repository',
            old_name='repo_name',
            new_name='full_name',
        ),
        migrations.AddField(
            model_name='repository',
            name='name',
            field=models.CharField(default='smallName', max_length=200),
            preserve_default=False,
        ),
    ]
