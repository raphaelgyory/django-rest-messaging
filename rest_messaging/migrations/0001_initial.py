# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_check', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('date_left', models.DateTimeField(null=True, blank=True)),
                ('date_last_check', models.DateTimeField(null=True, blank=True)),
                ('participant', models.ForeignKey(to='rest_messaging.Participant')),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('participants', models.ManyToManyField(to='rest_messaging.Participant', through='rest_messaging.Participation')),
            ],
        ),
        migrations.AddField(
            model_name='participation',
            name='thread',
            field=models.ForeignKey(to='rest_messaging.Thread'),
        ),
        migrations.AddField(
            model_name='notificationcheck',
            name='participant',
            field=models.OneToOneField(to='rest_messaging.Participant'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(to='rest_messaging.Participant'),
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(to='rest_messaging.Thread'),
        ),
    ]
