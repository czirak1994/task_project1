from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set to the current time when the task is created
    created_by = models.CharField(max_length=200)  # The username of the user who created the task
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set to the current time whenever the task is updated
    completed_by = models.CharField(max_length=200, null=True, blank=True)  # The username of the user who completed the task
    is_selected = models.BooleanField(default=False)  # Indicates whether the task is selected
    selected_by = models.CharField(max_length=200, null=True, blank=True)  # The username of the user who selected the task

    def __str__(self):
        return self.title   
class TaskGroup(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
class TaskTitle(models.Model):
    title = models.CharField(max_length=200)
    task_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE, related_name='task_titles')

    def __str__(self):
        return self.title       