# Generated by Django 3.0.4 on 2020-04-10 21:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sceleapp', '0022_auto_20200409_1250'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_count', models.IntegerField(default=0)),
                ('reply_count', models.IntegerField(default=0)),
                ('likes_given_count', models.IntegerField(default=0)),
                ('likes_earned_count', models.IntegerField(default=0)),
                ('grades', models.IntegerField(default=0)),
                ('bonuses', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
