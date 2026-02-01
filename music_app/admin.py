from django.contrib import admin
from .models import Song, Playlist, Comment

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'image_preview', 'uploaded_at')
    search_fields = ('title', 'artist', 'album', 'lyrics')
    list_filter = ('uploaded_at', 'artist')
    ordering = ('-uploaded_at',)
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'artist', 'album', 'file', 'image', 'duration', 'lyrics')
        }),
        ('Preview', {
            'fields': ('image_preview',),
            'classes': ('collapse',),
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 50px; height: 50px; object-fit: cover;" />'
        return 'No image'
    image_preview.short_description = 'Cover'
    image_preview.allow_tags = True

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at', 'user')
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'content_preview', 'created_at')
    search_fields = ('content', 'user__username', 'song__title')
    list_filter = ('created_at', 'user', 'song')
    ordering = ('-created_at',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
