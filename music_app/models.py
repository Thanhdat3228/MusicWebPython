from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='songs/')
    image = models.ImageField(upload_to='covers/', blank=True, null=True, help_text="Album cover image")
    duration = models.DurationField(null=True, blank=True)
    lyrics = models.TextField(blank=True, help_text="Lời bài hát")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # AI Emotion Classification fields
    emotion = models.CharField(
        max_length=20,
        choices=[
            ('happy', 'Vui'),
            ('sad', 'Buồn'),
            ('relaxed', 'Thư giãn'),
            ('contemplative', 'Sâu lắng'),
            ('unknown', 'Chưa phân loại')
        ],
        default='unknown',
        blank=True,
        help_text="Cảm xúc được phân loại bởi AI"
    )
    emotion_confidence = models.FloatField(
        default=0.0,
        help_text="Độ tin cậy của AI (0.0 - 1.0)"
    )

    @property
    def emotion_confidence_pct(self):
        return self.emotion_confidence * 100

    def __str__(self):
        return f"{self.title} - {self.artist}"

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.song.title}'
