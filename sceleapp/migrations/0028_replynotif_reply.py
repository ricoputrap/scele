# Generated by Django 3.0.4 on 2020-04-14 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sceleapp', '0027_auto_20200413_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='replynotif',
            name='reply',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sceleapp.UserReply'),
        ),
    ]