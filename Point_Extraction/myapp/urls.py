from django.urls import path
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('extract_points/', extract_main_points, name='extract_points'),
    path('from_recordings/', Extract_points_from_recordings, name='from_recordings'),
    path('from_meetings/', Extract_points_from_meetings, name='from_meetings'),
    path('audio_files/', all_files, name='audio_files'),
    path('delete_file/<int:id>/', delete_file, name='delete_file'),
    path('show_points/<int:id>/', show_points, name='show_points')
]
