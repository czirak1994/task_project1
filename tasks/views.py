from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Task, TaskGroup, TaskTitle
from .serializers import TaskSerializer, TaskTitleSerializer, TaskGroupSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

class TaskTitleViewSet(viewsets.ModelViewSet):
    queryset = TaskTitle.objects.all()
    serializer_class = TaskTitleSerializer
    
class TaskGroupViewSet(viewsets.ModelViewSet):
    queryset = TaskGroup.objects.all()
    serializer_class = TaskGroupSerializer    

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return HttpResponse("Benteler Task Manager")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Átirányítás csoport alapján
            if user.groups.filter(name='keszletezo').exists():
                return redirect('receiver')
            elif user.groups.filter(name='raktaros').exists():
                return redirect('tasks')
            else:
                return redirect('home')
        else:
            return render(request, 'login.html', {'form': {'errors': True}})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save()

        # Send a message over the WebSocket connection
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'tasks',  # This should match the group name in your consumer
            {
                'type': 'task.created',
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    # ... any other task fields you want to include ...
                },
            }
        )


@login_required
def list_tasks(request):
    task_groups = {}
    for task_title in TaskTitle.objects.all():
        group_name = task_title.task_group.name
        if group_name not in task_groups:
            task_groups[group_name] = []
        task_groups[group_name].append(task_title)

    context = {'task_groups': task_groups}
    return render(request, 'tasks.html', context)

def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Task.objects.create(title=title, description=description)
        return redirect('list-tasks')  # Térjen vissza a feladatok listájához

@csrf_exempt
def send_tasks(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            for task_data in data:
                task_data['created_by'] = request.user.username  # Bejelentkezett felhasználó hozzáadása
                serializer = TaskSerializer(data=task_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return JsonResponse({'status': 'error', 'errors': serializer.errors}, status=400)
            return JsonResponse({'status': 'success'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@login_required
def receiver_view(request):
    return render(request, 'receiver.html', {'user': request.user})



@csrf_exempt
def complete_tasks(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            if not task_ids:
                return JsonResponse({'status': 'error', 'message': 'No task IDs provided'}, status=400)

            tasks = Task.objects.filter(id__in=task_ids, completed=False, selected_by=request.user.username)
            tasks.update(completed=True, completed_by=request.user.username)

            # Értesítés a WebSocket csoportnak
            channel_layer = get_channel_layer()
            for task_id in task_ids:
                async_to_sync(channel_layer.group_send)(
                    'tasks', {
                        'type': 'task_completed',
                        'task_id': task_id,
                        'completed_by': request.user.username
                    }
                )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def select_task(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            action = data.get('action')  # Új mező az akció típusának jelzésére ('select' vagy 'deselect')
            username = data.get('username')
            if not task_id or not action or not username:
                return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)

            task = Task.objects.get(id=task_id)
            if action == 'select' and not task.is_selected:
                task.is_selected = True
                task.selected_by = username
                task.save()

                # Értesítés a WebSocket csoportnak
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'tasks', {
                        'type': 'task_selected',
                        'task_id': task_id,
                        'username': username
                    }
                )
                return JsonResponse({'status': 'success'})
            elif action == 'deselect' and task.is_selected and task.selected_by == username:
                task.is_selected = False
                task.selected_by = None
                task.save()

                # Értesítés a WebSocket csoportnak
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'tasks', {
                        'type': 'task_deselected',
                        'task_id': task_id,
                    }
                )
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid action or task state'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)