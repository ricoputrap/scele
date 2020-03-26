# Generated by Django 3.0.4 on 2020-03-25 09:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sceleapp', '0013_auto_20200325_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpost',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userreply',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]