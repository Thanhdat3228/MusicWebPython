from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Song, Playlist, Comment
from .forms import SongUploadForm, CommentForm
from django.http import FileResponse, Http404, HttpResponse
import os

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'music_app/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')
    
    return render(request, 'music_app/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def upload_song(request):
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save()
            messages.success(request, f'Song "{song.title}" uploaded successfully!')
            return redirect('home')
    else:
        form = SongUploadForm()
    return render(request, 'music_app/upload.html', {'form': form})

@login_required
def home(request):
    songs = Song.objects.all()
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'music_app/home.html', {'songs': songs, 'playlists': playlists})

@login_required
def player(request, song_id):
    song = Song.objects.get(id=song_id)
    playlists = Playlist.objects.filter(user=request.user)
    comments = song.comments.all().order_by('-created_at')
    form = CommentForm()
    return render(request, 'music_app/player.html', {
        'song': song, 
        'playlists': playlists,
        'comments': comments,
        'comment_form': form
    })

@login_required
def create_playlist(request):
    """Tạo playlist mới"""
    if request.method == 'POST':
        playlist_name = request.POST.get('name', '').strip()
        
        if not playlist_name:
            messages.error(request, 'Tên playlist không được để trống.')
            return redirect('home')
        
        # Kiểm tra xem đã có playlist với tên này chưa
        existing_playlist = Playlist.objects.filter(user=request.user, name=playlist_name).first()
        if existing_playlist:
            messages.warning(request, f'Playlist "{playlist_name}" đã tồn tại.')
            return redirect('home')
        
        # Tạo playlist mới
        playlist = Playlist.objects.create(
            name=playlist_name,
            user=request.user
        )
        messages.success(request, f'Đã tạo playlist "{playlist_name}" thành công!')
        return redirect('home')
    
    return redirect('home')

@login_required
def delete_playlist(request, playlist_id):
    """Xóa playlist"""
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        playlist_name = playlist.name
        playlist.delete()
        messages.success(request, f'Đã xóa playlist "{playlist_name}" thành công!')
    except Playlist.DoesNotExist:
        messages.error(request, 'Không tìm thấy playlist hoặc bạn không có quyền xóa.')
    
    return redirect('home')

@login_required
def add_song_to_playlist(request, song_id, playlist_id):
    """Thêm bài hát vào playlist"""
    try:
        song = Song.objects.get(id=song_id)
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        
        # Kiểm tra xem bài hát đã có trong playlist chưa
        if song in playlist.songs.all():
            messages.warning(request, f'"{song.title}" đã có trong playlist "{playlist.name}".')
        else:
            playlist.songs.add(song)
            messages.success(request, f'Đã thêm "{song.title}" vào playlist "{playlist.name}"!')
    except Song.DoesNotExist:
        messages.error(request, 'Không tìm thấy bài hát.')
    except Playlist.DoesNotExist:
        messages.error(request, 'Không tìm thấy playlist hoặc bạn không có quyền.')
    
    # Quay lại trang player
    return redirect('player', song_id=song_id)

@login_required
def remove_song_from_playlist(request, song_id, playlist_id):
    """Xóa bài hát khỏi playlist"""
    try:
        song = Song.objects.get(id=song_id)
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        
        if song in playlist.songs.all():
            playlist.songs.remove(song)
            messages.success(request, f'Đã xóa "{song.title}" khỏi playlist "{playlist.name}"!')
        else:
            messages.warning(request, f'"{song.title}" không có trong playlist "{playlist.name}".')
    except Song.DoesNotExist:
        messages.error(request, 'Không tìm thấy bài hát.')
    except Playlist.DoesNotExist:
        messages.error(request, 'Không tìm thấy playlist hoặc bạn không có quyền.')
    
    return redirect('playlist_detail', playlist_id=playlist_id)

@login_required
def playlist_detail(request, playlist_id):
    """Xem chi tiết playlist và phát nhạc"""
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        songs = playlist.songs.all()
        all_playlists = Playlist.objects.filter(user=request.user)
        return render(request, 'music_app/playlist_detail.html', {
            'playlist': playlist,
            'songs': songs,
            'playlists': all_playlists
        })
    except Playlist.DoesNotExist:
        messages.error(request, 'Không tìm thấy playlist hoặc bạn không có quyền truy cập.')
        return redirect('home')

@login_required
def add_comment(request, song_id):
    if request.method == 'POST':
        song = Song.objects.get(id=song_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.song = song
            comment.save()
            messages.success(request, 'Bình luận đã được đăng!')
    return redirect('player', song_id=song_id)

def stream_song(request, song_id):
    """Stream song with Range request support for seeking."""
    song = Song.objects.get(id=song_id)
    file_path = song.file.path
    
    if not os.path.exists(file_path):
        raise Http404
    
    file_size = os.path.getsize(file_path)
    range_header = request.META.get('HTTP_RANGE', '').strip()
    
    # If no Range header, return full file
    if not range_header:
        response = FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(file_size)
        return response
    
    # Parse Range header (format: "bytes=start-end")
    range_match = range_header.replace('bytes=', '').split('-')
    start = int(range_match[0]) if range_match[0] else 0
    end = int(range_match[1]) if range_match[1] else file_size - 1
    
    # Ensure valid range
    if start >= file_size or end >= file_size:
        return HttpResponse(status=416)  # Range Not Satisfiable
    
    # Calculate content length
    content_length = end - start + 1
    
    # Open file and seek to start position
    file_handle = open(file_path, 'rb')
    file_handle.seek(start)
    
    # Create partial content response
    response = HttpResponse(file_handle.read(content_length), content_type='audio/mpeg', status=206)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
    response['Content-Length'] = str(content_length)
    
    file_handle.close()
    return response

@login_required
def analyze_song_emotion(request, song_id):
    """
    Phân tích cảm xúc bài hát sử dụng AI
    
    Flow:
    1. Lấy bài hát từ database
    2. Kiểm tra có lyrics không
    3. Gọi AI model (EmotionClassifier)
    4. Lưu emotion + confidence vào database
    5. Hiển thị thông báo cho user
    6. Redirect về player page
    
    Args:
        request: HTTP request
        song_id: ID của bài hát cần phân tích
        
    Returns:
        HttpResponse: Redirect to player page
    """
    try:
        # Get song from database
        song = Song.objects.get(id=song_id)
        
        # Check if song has lyrics
        if not song.lyrics or len(song.lyrics.strip()) < 20:
            messages.warning(
                request,
                '⚠️ Bài hát cần có lời bài hát (ít nhất 20 ký tự) để phân tích cảm xúc.'
            )
            return redirect('player', song_id=song_id)
        
        # Import AI model (lazy import to avoid loading at startup)
        from .ml_models import get_emotion_classifier
        
        # Get classifier instance
        classifier = get_emotion_classifier()
        
        # Predict emotion
        result = classifier.predict(song.lyrics)
        
        if isinstance(result, dict) and 'emotion' in result:
            # Save to database
            song.emotion = result['emotion']
            song.emotion_confidence = result['confidence']
            song.save()
            
            # Get Vietnamese emotion name for display
            emotion_display = dict(Song._meta.get_field('emotion').choices)[result['emotion']]
            
            # Success message
            messages.success(
                request,
                f'✅ Phân loại thành công: <strong>{emotion_display}</strong> '
                f'({result["confidence"]:.1%} độ tin cậy)'
            )
        elif isinstance(result, dict) and 'error' in result:
            messages.error(
                request, 
                f'❌ Lỗi AI: {result["error"]}'
            )
        else:
            messages.error(
                request, 
                '❌ Không thể phân tích. Vui lòng kiểm tra lại lời bài hát hoặc thử lại sau.'
            )
            
    except Song.DoesNotExist:
        messages.error(request, '❌ Không tìm thấy bài hát.')
    except Exception as e:
        # Log error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error analyzing emotion for song {song_id}: {e}")
        
        messages.error(
            request, 
            f'❌ Lỗi khi phân tích: {str(e)}'
        )
    
    return redirect('player', song_id=song_id)
