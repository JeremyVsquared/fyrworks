import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django import forms
from django.db.models import Q, Count
from django.core import serializers
from django.template import RequestContext
from datetime import date, timedelta
from django.core.exceptions import PermissionDenied

from pm.models import *
from pm.forms import *


@login_required
def dashboard(request, group):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    form = TaskForm()

    items = Task.objects.filter(group=g)

    today = date.today()
    start_week = today - timedelta(today.weekday())
    end_week = start_week + timedelta(days=7)

    total = items.count()
    total_assigned_to_me = items.filter(assigned=request.user).count()
    assigned_to_me = items.filter(assigned=request.user)[:10]
    due_late = items.filter(due__lt=today)[:5]
    total_due_late = items.filter(due__lt=today).count()
    due_today = items.filter(due=today)[:5]
    total_due_today = items.filter(due=today).count()
    due_this_week = items.filter(due__range=[start_week, end_week])[:5]
    total_due_this_week = items.filter(due__range=[start_week, end_week]).count()
    important = items.filter(assigned=request.user, priority=Priority.HIGH)[:5]
    total_important = items.filter(assigned=request.user, priority=Priority.HIGH).count()

    notifications = Notification.objects.filter(to_user=request.user, dismissed=False, group=g)
    total_notifications = notifications.count()
    recent_notifications = notifications[:10]

    stream = Notification.objects.filter(group=g, to_user=None)[:20]

    return render(request, "dashboard.html", {
        'base_url': '/team/' + str(g.pk) + '/',
        'stream': stream,
        'important': important,
        'total_important': total_important,
        'assigned_to_me': assigned_to_me,
        'total_assigned_to_me': total_assigned_to_me,
        'due_today': due_today,
        'total_due_today': total_due_today,
        'due_this_week': due_this_week,
        'total_due_this_week': total_due_this_week,
        'due_late': due_late,
        'total_due_late': total_due_late,
        'notifications': recent_notifications,
        'total_notifications': total_notifications
    }, context_instance=RequestContext(request))


@login_required
def home(request, group):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    form = TaskForm()

    return render(request, 'base.html', {
        'task_active': True,
        'base_url': '/team/' + str(g.pk) + '/',
        'q': request.GET.get('q', '')
    })


@login_required
def search(request, group, output_format='html'):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    items = Task.objects.filter(group=g)

    q = ''
    q_label_list = []
    if request.GET.get('q', None) is not None:
        q = request.GET.get('q')

        for l in q.split(','):
            if l:
                q_label_list.append({
                    'label': l.replace('%20', ' '),
                    'negated_q': q.replace(l, '')
                })
        items = filter_items(items, request.GET.get('q'), request.user.pk)

    today = date.today()
    start_week = today - timedelta(today.weekday())
    end_week = start_week + timedelta(days=7)

    total = items.count()
    due_late = items.filter(due__lt=today).count()
    due_today = items.filter(due=today).count()
    due_this_week = items.filter(due__range=[start_week, end_week]).count()
    important = items.filter(priority=Priority.HIGH).count()

    stream = Notification.objects.filter(group=g, to_user=None)[:10]
    recent_notifications = Notification.objects.filter(to_user=request.user, dismissed=False, group=g)[:10]

    if output_format == 'html':
        if total is 0:
            items = [{'title': 'nothing yet', 'fake': True}]
        form = TaskForm()

        return render(request, 'task_list.html', {
            'q': q,
            'q_label_list': q_label_list,
            'base_url': '/team/' + str(g.pk) + '/',
            'add_form': form,
            'items': items,
            'meta': {
                'total': total,
                'priority': important,
                'due_today': due_today,
                'due_this_week': due_this_week,
                'due_late': due_late,
                'stream': stream,
                'notifications': recent_notifications
            },
            'tags': Tag.objects.filter(group=g, status=Status.ACTIVE),
            'members': g.user_set.filter(~Q(pk=request.user.pk))
        }, context_instance=RequestContext(request))
    else:
        data_seed = {
            'tasks': items.all(),
            'meta': {
                'total': total,
                'priority': important,
                'due_today': due_today,
                'due_this_week': due_this_week,
                'due_late': due_late,
                'stream': stream,
                'notifications': recent_notifications
            }
        }

        data = serializers.serialize(output_format, data_seed)
        return HttpResponse(data)


@login_required
def task(request, group, id):
    form = None
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    try:
        task = Task.objects.get(pk=id, group=g)
    except Task.DoesNotExist:
        raise PermissionDenied()

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            task = form.save()

            n = Notification()
            n.group = g
            n.event = Notification.TASK_CHANGE
            n.from_user = request.user
            n.message = "<i>" + task.title + "</i> task updated"
            n.link = '/team/' + str(g.pk) + '/tasks/#task:' + str(task.pk)
            n.save()

            for u in task.subscribers.all():
                n.pk = None
                n.to_user = u
                n.save()
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_content.html', {
        'base_url': '/team/' + str(g.pk) + '/',
        'task': task,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def task_add(request, group):
    form = None
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    items = []

    if request.method == 'POST':
        task = Task()
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.group = g

            task.save()
            form.save_m2m()

            items.append(task)

            n = Notification()
            n.group = g
            n.event = Notification.TASK_CREATED
            n.from_user = request.user
            n.message = "<i>" + task.title + "</i> task created"
            n.link = '/team/' + str(g.pk) + '/tasks/#task:' + str(task.pk)
            n.save()

            for u in task.subscribers.all():
                n.pk = None
                n.to_user = u
                n.save()
    return render(request, 'task_cards.html', {
        'base_url': '/team/' + str(g.pk) + '/',
        'task': task,
        'add_form': form,
    }, context_instance=RequestContext(request))


@login_required
def task_comment(request, group, id):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    try:
        task = Task.objects.get(pk=id, group=g)
    except Task.DoesNotExist:
        raise PermissionDenied()

    errors = []
    if request.method == 'POST':
        if request.POST.get('comment', None) is not None:
            content = request.POST['comment']
            if content and len(content):
                # create comment
                c = Comment()
                c.created_by = request.user
                c.content = content
                c.type = 1
                c.save()

                # handle file uploads
                if request.FILES:
                    pass

                task.comments.add(c)
                task.save()

                n = Notification()
                n.group = g
                n.event = Notification.COMMENT
                n.from_user = request.user
                n.message = "<i>" + task.title + "</i> has a new comment"
                n.link = '/team/' + str(g.pk) + '/tasks/#task:' + str(task.pk)
                n.save()

                for u in task.subscribers.all():
                    n.pk = None
                    n.to_user = u
                    n.save()

    return render(request, 'task_comments.html', {
        'task': task,
        'base_url': '/team/' + str(g.pk) + '/'
    }, context_instance=RequestContext(request))


@login_required
def tags(request, group, tag):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()
    errors = None

    if request.method == 'POST' and tag is None:
        errors = []

        title = request.POST.get('tag', None)

        if title is None:
            errors.append('title is required')
        else:
            if tag is None:
                tag_obj = Tag()
                tag_obj.group = g
                tag_obj.created_by = request.user
                tag_obj.title = title
                tag_obj.save()
            else:
                try:
                    tag_obj = Tag.objects.get(group=g, pk=tag)
                except Tag.DoesNotExist:
                    raise PermissionDenied()

                tag_obj.title = title
                tag_obj.save()

    tags = Tag.objects.filter(group=g)

    return render(request, 'tags.html', {
        'tags_active': True,
        'errors': errors,
        'base_url': '/team/' + str(g.pk) + '/',
        'tags': tags
    }, context_instance=RequestContext(request))


@login_required
def settings(request, group):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    try:
        settings = UserSettings.objects.get(user=request.user)
    except UserSettings.DoesNotExist:
        settings = UserSettings()
        settings.user = request.user
        settings.save()

    if request.method == 'POST':
        if 'update_settings' in request.POST:
            if request.POST.get('notify_task_assigned', 'off') == 'on':
                notify_task_assigned = True
            else:
                notify_task_assigned = False
            if request.POST.get('notify_task_comments', 'off') == 'on':
                notify_task_comments = True
            else:
                notify_task_comments = False
            if request.POST.get('notify_task_status', 'off') == 'on':
                notify_task_status = True
            else:
                notify_task_status = False

            settings.notify_task_assigned = notify_task_assigned
            settings.notify_task_comments = notify_task_comments
            settings.notify_task_status = notify_task_status
            settings.save()
        elif 'update_account' in request.POST:
            pass
        elif 'update_team' in request.POST:
            pass

    return render(request, 'settings.html', {
        'settings_active': True,
        'base_url': '/team/' + str(g.pk) + '/',
        'user': request.user,
        'settings': settings,
        'group': g
    }, context_instance=RequestContext(request))


@login_required
def analytics(request, group):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied

    open_tasks_per_assignee = Task.objects.values('assigned__username').filter(status=Status.ACTIVE).annotate(
        count=Count('pk')).order_by('assigned')
    open_tasks_per_tag = Task.objects.values('tags__title').filter(status=Status.ACTIVE).annotate(
        count=Count('pk')).order_by('tags')
    open_tasks_per_priority = Task.objects.values('priority').filter(status=Status.ACTIVE).annotate(
        count=Count('pk')).order_by('-priority')

    # friendly priority text
    for t in open_tasks_per_priority:
        t['priority'] = Priority.options[t['priority']][1]

    open_tasks_per_day = []
    closed_tasks_per_day = []
    per_day_labels = []

    # iterate through last 30 days compiling counts of tasks created & closed per day
    for i in reversed(range(0, 29)):
        day = datetime.datetime.now() + datetime.timedelta(-i)
        open_day = Task.objects.filter(date_created__range=(datetime.datetime.combine(day, datetime.time.min),
                                                            datetime.datetime.combine(day, datetime.time.max))).count()
        close_day = Task.objects.filter(date_closed__range=(datetime.datetime.combine(day, datetime.time.min),
                                                            datetime.datetime.combine(day, datetime.time.max))).count()
        open_tasks_per_day.append(str(open_day))
        closed_tasks_per_day.append(str(close_day))

        month_label = "{:%m}".format(day).lstrip('0')
        day_label = "{:%d}".format(day).lstrip('0')
        per_day_labels.append('"' + month_label + '/' + day_label + '"')

    return render(request, 'analytics.html', {
        'analytics_active': True,
        'base_url': '/team/' + str(g.pk) + '/',
        'open_tasks_per_assignee': open_tasks_per_assignee,
        'open_tasks_per_tag': open_tasks_per_tag,
        'open_tasks_per_priority': open_tasks_per_priority,
        'open_tasks_per_day': ",".join(open_tasks_per_day),
        'closed_tasks_per_day': ",".join(closed_tasks_per_day),
        'per_day_labels': ",".join(per_day_labels)
    }, context_instance=RequestContext(request))


@login_required
def notifications(request, group, user, notification, dismissing):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied

    if notification is not None:
        try:
            note = Notification.objects.filter(to_user=request.user, group=g)
        except Notification.DoesNotExist:
            raise PermissionDenied

        if dismissing:
            note.dismissed = True
            note.save()
            data = serializers.serialize("json", {'success': '1'})
        else:
            if note.date_viewed is None:
                note.date_viewed = datetime.datetime.now()
                note.save()
            data = serializers.serialize("json", [note],
                                        fields=('pk', 'event', 'from_user', 'date_created', 'date_viewed', 'message', 'link', 'dismissed'))

    else:
        # ping for notifications in the last 10 minutes
        ten_minutes_ago = datetime.datetime.now() - timedelta(minutes=10)
        recent_notifications = Notification.objects.filter(date_created_gt=ten_minutes_ago, to_user=request.user, group=g)

        for n in recent_notifications.all():
            if n.date_viewed is None:
                n.date_viewed = datetime.datetime.now()
                n.save()

        data = serializers.serialize("json", recent_notifications.all(),
                                    fields=('pk', 'event', 'from_user', 'date_created', 'date_viewed', 'message', 'link', 'dismissed'))

    return HttpResponse(data)


@login_required
def meeting(request, group, id):
    try:
        g = request.user.groups.get(pk=group)
    except Group.DoesNotExist:
        raise PermissionDenied()

    try:
        meeting = Meeting.objects.get(group=g, pk=id)
    except Meeting.DoesNotExist:
        raise PermissionDenied()

    if request.method == 'POST':
        form = MeetingForm(request.POST)

        if form.is_valid():
            meeting = form.save()
    else:
        form = MeetingForm()

    return render(request, 'meeting.html', {
        'meeting': meeting,
        'form': form
    }, context_instance=RequestContext(request))


def public_home(request):
    try:
        page_content = PageContent.objects.get()
    except PageContent.DoesNotExist:
        page_content = {}

    return render(request, 'home.html', {
        'page_content': page_content
    }, context_instance=RequestContext(request))


def signup(request):
    errors = []

    if request.method == 'POST':
        team = request.POST.get('team', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        try:
            validate_email(username)
            if username is None:
                errors.append('Username is invalid')
            else:
                preexisting_users = User.objects.filter(username=username)

                if len(preexisting_users):
                    errors.append('Username already exists')
        except forms.ValidationError:
            errors.append('Username is invalid')

        if team is None:
            errors.append('Team name is invalid')
        if password is None:
            errors.append('Password is invalid')

        if len(errors) == 0:
            u = User.objects.create_user(username, username, password)
            g = Group.objects.create(name=team)

            g.user_set.add(u)

            user = authenticate(username=u, password=password)
            login(request, user)

            Notification.objects.create(
                group=g,
                event=Notification.TEAM_CHANGE,
                from_user=u,
                message=u.username + " created team"
            )

            return redirect('/team/' + str(g.pk) + '/')

    return render(request, 'signup.html', {
        'errors': errors
    }, context_instance=RequestContext(request))


def login_page(request):
    errors = []
    if request.user.is_authenticated():
        try:
            g = request.user.groups.get()

            return redirect('/team/' + str(g.pk) + '/')
        except Group.DoesNotExist:
            pass
    elif request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                try:
                    g = request.user.groups[0]

                    return redirect('/team/' + str(g.pk) + '/')
                except IndexError:
                    errors.append('This account has no team association')
            else:
                errors.append('This account has been disabled')
        else:
            errors.append('Invalid username or password')
    return render(request, 'login.html', {
        'errors': errors
    }, context_instance=RequestContext(request))


def filter_items(items, q, user):
    if q and q != '':
        q = q.split(',')

        for token in q:
            if q == '':
                continue

            q_filter = None
            negate = False

            if ':' in token:
                split_token = token.split(':')

                if split_token[0][0] == '!':
                    negate = True
                    split_token[0] = split_token[0][1:]

                if split_token[0] == 'assigned':
                    if split_token[1] == 'me':
                        q_filter = Q(assigned=user)
                    elif split_token[1] == 'None':
                        q_filter = Q(assigned=None)
                    else:
                        q_filter = Q(assigned__username__icontains=split_token[1])
                elif split_token[0] == 'created_by':
                    if split_token[1] == 'me':
                        q_filter = Q(created_by=user)
                    else:
                        q_filter = Q(created_by__username__icontains=split_token[1])
                elif split_token[0] == 'due':
                    if split_token[1] == 'today':
                        q_filter = Q(due=date.today())
                    elif split_token[1] == 'tomorrow':
                        tomorrow = date.today() + timedelta(days=1)
                        q_filter = Q(due=tomorrow)
                    elif split_token[1] == 'thisweek':
                        today = date.today()
                        start_week = today - timedelta(today.weekday())
                        end_week = start_week + timedelta(days=7)
                        q_filter = Q(due__range=[start_week, end_week])
                    elif split_token[1] == 'late' or split_token[1] == 'overdue':
                        q_filter = Q(due__lt=date.today())
                elif split_token[0] == 'created':
                    if split_token[1] == 'today':
                        q_filter = Q(date_created=date.today())
                    elif split_token[1] == 'yesterday':
                        yesterday = date.today() - timedelta(days=1)
                        q_filter = Q(date_created=yesterday)
                    elif split_token[1] == 'thisweek':
                        today = date.today()
                        start_week = today - timedelta(today.weekday())
                        end_week = start_week + timedelta(days=7)
                        q_filter = Q(date_created__range=[start_week, end_week])
                elif split_token[0] == 'priority':
                    if split_token[1] == 'low':
                        q_filter = Q(priority=Priority.LOW)
                    elif split_token[1] == 'normal':
                        q_filter = Q(priority=Priority.NORMAL)
                    elif split_token[1] == 'high':
                        q_filter = Q(priority=Priority.HIGH)
                elif split_token[0] == 'status':
                    if split_token[1] == 'active':
                        q_filter = Q(status=Status.ACTIVE)
                    elif split_token[1] == 'completed' or split_token[1] == 'done':
                        q_filter = Q(status=Status.COMPLETED)
                    elif split_token[1] == 'pending':
                        q_filter = Q(status=Status.PENDING)
                    elif split_token[1] == 'inactive':
                        q_filter = Q(status=Status.INACTIVE)
                    elif split_token[1] == 'archived':
                        q_filter = Q(status=Status.ARCHIVED)
                elif split_token[0] == 'tag':
                    if split_token[1].lower() == 'none':
                        q_filter = Q(tags=None)
                    else:
                        split_token[1] = split_token[1].replace('%20', ' ')
                        q_filter = Q(tags__title__icontains=split_token[1])
                else:
                    print "I didn't understand token " + split_token[0]
            else:
                q_filter = Q(title__icontains=token)

            if q_filter is not None:
                if negate:
                    items = items.filter(~q_filter)
                else:
                    items = items.filter(q_filter)

    return items
