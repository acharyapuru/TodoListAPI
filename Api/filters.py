import django_filters
from .models import Task

class TaskFilters(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = {
            'title' :['exact','contains','icontains','iexact'],
            'description' : ['exact','contains','icontains','iexact'],
            'completed' : ['exact','iexact']
        }
