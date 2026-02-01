from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_song, name='upload_song'),
    path('player/<int:song_id>/', views.player, name='player'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('playlist/delete/<int:playlist_id>/', views.delete_playlist, name='delete_playlist'),
    path('playlist/<int:playlist_id>/add-song/<int:song_id>/', views.add_song_to_playlist, name='add_song_to_playlist'),
    path('playlist/<int:playlist_id>/remove-song/<int:song_id>/', views.remove_song_from_playlist, name='remove_song_from_playlist'),
    path('comment/<int:song_id>/', views.add_comment, name='add_comment'),
    path('song/<int:song_id>/stream/', views.stream_song, name='stream_song'),
    path('song/<int:song_id>/analyze-emotion/', views.analyze_song_emotion, name='analyze_emotion'),
]