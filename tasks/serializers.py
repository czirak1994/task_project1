from rest_framework import serializers
from .models import Task, TaskTitle, TaskGroup

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']  # Ezzel elkerülheted a beküldési hibákat
class TaskTitleSerializer(serializers.ModelSerializer):
    task_group_name = serializers.CharField(source='task_group.name', read_only=True)
    class Meta:
        model = TaskTitle
        fields = '__all__'
        
class TaskGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGroup
        fields = '__all__'        