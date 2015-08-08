# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=0, choices=[(0, b'User'), (1, b'System')])),
                ('content', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_created'],
                'get_latest_by': 'date_created',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'deleted'), (1, b'active'), (5, b'completed'), (2, b'pending'), (3, b'inactive'), (4, b'archived')])),
                ('title', models.CharField(max_length=240)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'ordering': ('title', 'date_created'),
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'deleted'), (1, b'active'), (5, b'completed'), (2, b'pending'), (3, b'inactive'), (4, b'archived')])),
                ('first_name', models.CharField(max_length=240)),
                ('last_name', models.CharField(max_length=240)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, to='pm.Company', null=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'ordering': ('last_name', 'date_created'),
            },
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'deleted'), (1, b'active'), (5, b'completed'), (2, b'pending'), (3, b'inactive'), (4, b'archived')])),
                ('priority', models.IntegerField(default=1, choices=[(0, b'low'), (1, b'normal'), (2, b'high')])),
                ('title', models.CharField(max_length=240)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('attendees', models.ManyToManyField(related_name='attendees', to=settings.AUTH_USER_MODEL, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'ordering': ('title', 'date_created'),
            },
        ),
        migrations.CreateModel(
            name='MeetingInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('attendees', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
                ('meeting', models.ForeignKey(to='pm.Meeting')),
            ],
            options={
                'ordering': ('date_created',),
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.IntegerField(default=1, choices=[(1, b'comment'), (2, b'task created'), (3, b'assigned'), (6, b'task change'), (4, b'tag created'), (5, b'team change')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_viewed', models.DateTimeField(null=True, blank=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('dismissed', models.BooleanField(default=False)),
                ('link', models.URLField(null=True, blank=True)),
                ('from_user', models.ForeignKey(related_name='from_user', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('to_user', models.ForeignKey(related_name='to_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
        migrations.CreateModel(
            name='PageContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title1', models.CharField(max_length=64, null=True, blank=True)),
                ('content1', models.TextField(null=True, blank=True)),
                ('title2', models.CharField(max_length=64, null=True, blank=True)),
                ('content2', models.TextField(null=True, blank=True)),
                ('footer_title1', models.CharField(max_length=64, null=True, blank=True)),
                ('footer_content1', models.TextField(null=True, blank=True)),
                ('footer_title2', models.CharField(max_length=64, null=True, blank=True)),
                ('footer_content2', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'deleted'), (1, b'active'), (5, b'completed'), (2, b'pending'), (3, b'inactive'), (4, b'archived')])),
                ('title', models.CharField(max_length=240)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'ordering': ('title', 'date_created'),
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'deleted'), (1, b'active'), (5, b'completed'), (2, b'pending'), (3, b'inactive'), (4, b'archived')])),
                ('priority', models.IntegerField(default=1, choices=[(0, b'low'), (1, b'normal'), (2, b'high')])),
                ('title', models.CharField(max_length=240)),
                ('description', models.TextField(null=True, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_closed', models.DateTimeField(null=True, blank=True)),
                ('due', models.DateField(null=True, blank=True)),
                ('assigned', models.ManyToManyField(related_name='task_assigned', to=settings.AUTH_USER_MODEL, blank=True)),
                ('comments', models.ManyToManyField(to='pm.Comment', blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('subscribers', models.ManyToManyField(related_name='task_subscribers', to=settings.AUTH_USER_MODEL, blank=True)),
                ('tags', models.ManyToManyField(to='pm.Tag', blank=True)),
            ],
            options={
                'ordering': ('date_created', 'title'),
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(0, b'deleted'), (1, b'active'), (5, b'completed'), (2, b'pending'), (3, b'inactive'), (4, b'archived')])),
                ('title', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('create_by_anonymous', models.CharField(max_length=124, null=True, blank=True)),
                ('assigned', models.ManyToManyField(related_name='ticket_assigned', to=settings.AUTH_USER_MODEL, blank=True)),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('subscribers', models.ManyToManyField(related_name='ticket_subscribers', to=settings.AUTH_USER_MODEL, blank=True)),
                ('tags', models.ManyToManyField(to='pm.Tag', blank=True)),
            ],
            options={
                'ordering': ('date_created', 'title'),
            },
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('name', models.CharField(default=b'', max_length=128, null=True, blank=True)),
                ('type', models.IntegerField(default=1, choices=[(b'image', 1), (b'document', 2)])),
                ('width', models.IntegerField(default=0, null=True, blank=True)),
                ('height', models.IntegerField(default=0, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notify_task_assigned', models.BooleanField(default=True)),
                ('notify_task_comments', models.BooleanField(default=True)),
                ('notify_task_status', models.BooleanField(default=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='contact',
            name='tags',
            field=models.ManyToManyField(to='pm.Tag', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='tags',
            field=models.ManyToManyField(to='pm.Tag', blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='files',
            field=models.ManyToManyField(to='pm.UploadedFile', blank=True),
        ),
    ]
