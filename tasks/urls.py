from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, home, list_tasks, TaskTitleViewSet, TaskGroupViewSet
router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'tasktitles', TaskTitleViewSet)
router.register(r'taskgroups', TaskGroupViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('api/', include(router.urls)),
    path('tasks/', list_tasks, name='tasks'),
]