from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet, home, list_tasks, create_task, receiver_view, complete_tasks, login_view, logout_view, select_task, TaskTitleViewSet, TaskGroupViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'tasktitles', TaskTitleViewSet)
router.register(r'taskgroups', TaskGroupViewSet)
urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('tasks/', list_tasks, name='tasks'),
    path('tasks/create/', create_task, name='task-create'),
    path('receiver/', receiver_view, name='receiver'),
    path('api/complete-tasks/', complete_tasks, name='complete_tasks'),
    path('api/select-task/', select_task, name='select_task'),
]
