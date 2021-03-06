# Generated by Django 2.0.3 on 2018-03-19 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PatternBuddy', '0004_auto_20180220_1927'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=200)),
                ('followers_count', models.PositiveIntegerField(default=0)),
                ('commits_count', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='repository',
            name='comments_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='repository',
            name='pull_request_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='repository',
            name='id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='repository',
            name='last_checked',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='contribution',
            name='contributor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatternBuddy.Contributor'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PatternBuddy.Repository'),
        ),
    ]
