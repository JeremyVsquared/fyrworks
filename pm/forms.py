from models import *
from django.forms import ModelForm


class TaskForm(ModelForm):
	class Meta:
		model = Task
		fields = ['status', 'title', 'description', 'assigned', 'priority', 'due', 'tags']


class MeetingForm(ModelForm):
	class Meta:
		model = Meeting
		fields = ['status', 'title', 'priority', 'attendees']


class MeetingInstanceForm(ModelForm):
	class Meta:
		model = MeetingInstance
		fields = ['notes', 'attendees']