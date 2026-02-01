from django import forms
from .models import Song, Comment

class SongUploadForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'album', 'file', 'image', 'lyrics']
        widgets = {
            'lyrics': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...',
                'style': 'background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2);'
            }),
        }