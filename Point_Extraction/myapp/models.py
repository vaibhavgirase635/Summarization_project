from django.db import models

# Create your models here.
class AudioFile(models.Model):

    audio_file = models.FileField(upload_to='audio_files/')
    

class Audio_File_Data(models.Model):
    file_name = models.CharField(max_length=100, blank=True, null=True)
    main_points = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)