from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, Group


class Status(models.Model):
    DELETED = 0
    ACTIVE = 1
    PENDING = 2
    INACTIVE = 3
    ARCHIVED = 4
    COMPLETED = 5

    options = (
        (DELETED, 'deleted'),
        (ACTIVE, 'active'),
        (COMPLETED, 'completed'),
        (PENDING, 'pending'),
        (INACTIVE, 'inactive'),
        (ARCHIVED, 'archived'),
    )

    class Meta:
        managed = False


class Priority(models.Model):
    LOW = 0
    NORMAL = 1
    HIGH = 2

    options = (
        (LOW, 'low'),
        (NORMAL, 'normal'),
        (HIGH, 'high'),
    )

    class Meta:
        managed = False


class UserSettings(models.Model):
    user = models.ForeignKey(User)
    notify_task_assigned = models.BooleanField(default=True)
    notify_task_comments = models.BooleanField(default=True)
    notify_task_status = models.BooleanField(default=True)


class Tag(models.Model):
    status = models.IntegerField(choices=Status.options, default=Status.ACTIVE)
    title = models.CharField(max_length=240)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    group = models.ForeignKey(Group)

    def __str__(self):
        return self.title

    def tasks(self):
        return self.task_set

    class Meta:
        ordering = ('title', 'date_created',)


class UploadedFile(models.Model):
    IMAGE = 1
    DOCUMENT = 2
    FILETYPES = (
        ('image', IMAGE),
        ('document', DOCUMENT)
    )

    url = models.URLField()
    name = models.CharField(max_length=128, default='', null=True, blank=True)
    type = models.IntegerField(choices=FILETYPES, default=IMAGE)
    width = models.IntegerField(default=0, null=True, blank=True)
    height = models.IntegerField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.type = self.DOCUMENT

        supported_image_types = ['jpeg', 'jpg', 'png', 'gif']
        for t in supported_image_types:
            if '.' + str(t) in self.name:
                self.type = self.IMAGE

        super(UploadedFile, self).save(*args, **kwargs)

    def is_image(self):
        return self.type == self.IMAGE


class Comment(models.Model):
    TYPES = (
        (0, 'User'),
        (1, 'System'),
    )
    type = models.IntegerField(choices=TYPES, default=0)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    files = models.ManyToManyField(UploadedFile, blank=True)

    def __str__(self):
        return self.content

    class Meta:
        get_latest_by = "date_created"
        ordering = ["date_created"]


class Task(models.Model):
    status = models.IntegerField(choices=Status.options, default=Status.ACTIVE)
    priority = models.IntegerField(choices=Priority.options, default=Priority.NORMAL)
    title = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    comments = models.ManyToManyField(Comment, blank=True)

    group = models.ForeignKey(Group)
    created_by = models.ForeignKey(User)
    assigned = models.ManyToManyField(User, blank=True, related_name="task_assigned")
    subscribers = models.ManyToManyField(User, blank=True, related_name="task_subscribers")
    date_created = models.DateTimeField(auto_now_add=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    due = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    # estimate = models.DoubleField(null=True, blank=True)
    # percentage_complete = models.IntegerFIeld(default='0')

    def __str__(self):
        return self.title

    def add_comment(self, comment):
        # notify subscribers
        for s in self.subscribers.all():
            if s != comment.created_by:
                n = Notification()
                n.to_user = s
                n.from_user = comment.created_by
                n.message = ""
                n.save()

        # add to collection
        self.comments.add(comment)

    def priority_color(self):
        color = ''

        if self.priority is Priority.HIGH:
            color = 'red'
        elif self.priority is Priority.LOW:
            color = 'yellow'

        return color

    class Meta:
        ordering = ('date_created', 'title',)


class Ticket(models.Model):
    status = models.IntegerField(choices=Status.options, default=Status.ACTIVE)
    title = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)
    create_by_anonymous = models.CharField(max_length=124, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True)
    assigned = models.ManyToManyField(User, blank=True, related_name="ticket_assigned")
    subscribers = models.ManyToManyField(User, blank=True, related_name="ticket_subscribers")
    group = models.ForeignKey(Group)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('date_created', 'title',)


class Company(models.Model):
    status = models.IntegerField(choices=Status.options, default=Status.ACTIVE)
    title = models.CharField(max_length=240)

    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title', 'date_created',)


class Contact(models.Model):
    status = models.IntegerField(choices=Status.options, default=Status.ACTIVE)
    first_name = models.CharField(max_length=240)
    last_name = models.CharField(max_length=240)
    company = models.ForeignKey(Company, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        ordering = ('last_name', 'date_created',)


class Meeting(models.Model):
    status = models.IntegerField(choices=Status.options, default=Status.ACTIVE)
    priority = models.IntegerField(choices=Priority.options, default=Priority.NORMAL)
    title = models.CharField(max_length=240)

    group = models.ForeignKey(Group)
    created_by = models.ForeignKey(User)
    attendees = models.ManyToManyField(User, blank=True, related_name="attendees")
    date_created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title', 'date_created',)


class MeetingInstance(models.Model):
    meeting = models.ForeignKey(Meeting)
    date_created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    attendees = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.date_created

    class Meta:
        ordering = ('date_created',)


class Notification(models.Model):
    COMMENT = 1
    TASK_CREATED = 2
    ASSIGNED = 3
    TASK_CHANGE = 6
    TAG_CREATED = 4
    TEAM_CHANGE = 5
    events = (
        (COMMENT, 'comment'),
        (TASK_CREATED, 'task created'),
        (ASSIGNED, 'assigned'),
        (TASK_CHANGE, 'task change'),
        (TAG_CREATED, 'tag created'),
        (TEAM_CHANGE, 'team change')
    )

    group = models.ForeignKey(Group)
    event = models.IntegerField(choices=events, default=COMMENT)
    to_user = models.ForeignKey(User, related_name="to_user", null=True, blank=True)
    from_user = models.ForeignKey(User, related_name="from_user")
    date_created = models.DateTimeField(auto_now_add=True)
    date_viewed = models.DateTimeField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    dismissed = models.BooleanField(default=False)
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.message

    def icon(self):
        if self.event == self.COMMENT:
            return 'mdi-communication-comment'
        elif self.event == self.TASK_CREATED:
            return 'mdi-av-new-releases'
        elif self.event == self.ASSIGNED:
            return 'mdi-toggle-radio-button-on'
        elif self.event == self.TAG_CREATED:
            return 'mdi-communication-comment'
        elif self.event == self.TEAM_CHANGE:
            return 'mdi-action-group-work'
        elif self.event == self.TASK_CHANGE:
            return 'mdi-toggle-check-box'

    def dismiss_url(self):
        return '/team/' + str(self.group.pk) + '/notifications/' + str(self.to_user.pk) + '/' + str(self.pk) + '/'

    class Meta:
        ordering = ('-date_created',)


class PageContent(models.Model):
    title1 = models.CharField(max_length=64, null=True, blank=True)
    content1 = models.TextField(null=True, blank=True)
    title2 = models.CharField(max_length=64, null=True, blank=True)
    content2 = models.TextField(null=True, blank=True)
    footer_title1 = models.CharField(max_length=64, null=True, blank=True)
    footer_content1 = models.TextField(null=True, blank=True)
    footer_title2 = models.CharField(max_length=64, null=True, blank=True)
    footer_content2 = models.TextField(null=True, blank=True)


admin.site.register(UserSettings)
admin.site.register(Task)
admin.site.register(Ticket)
admin.site.register(Contact)
admin.site.register(Company)
admin.site.register(Meeting)
admin.site.register(MeetingInstance)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(PageContent)
