from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import UserProfile, GroupProfile, StyleSettings, Announcement, EmailSettings
from .model.form.user_form import UserSearchForm, UserForm
from .model.form.user_management_form import UserCreateForm, UserEditForm
from .model.form.group_form import GroupSearchForm, GroupForm, GroupProfileForm, GroupMemberForm
from .model.form.login_user_form import LoginForm
from .model.form.profile_form import ProfileEditForm, ProfilePasswordChangeForm
from .model.form.announcement_form import AnnouncementForm, AnnouncementSearchForm, EmailSettingsForm
from .utils.aws_s3 import list_s3_files, upload_file_to_s3, delete_file_from_s3
from .model.form.file_form import UploadFileForm


def home(request):
    # 現在表示すべきお知らせを取得
    now = timezone.now()
    announcements = Announcement.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-priority', '-start_date')
    
    # ユーザーが所属するグループのお知らせのみをフィルタリング
    if request.user.is_authenticated:
        visible_announcements = []
        for announcement in announcements:
            if announcement.is_visible_to_user(request.user):
                visible_announcements.append(announcement)
        announcements = visible_announcements
    else:
        # 未ログインユーザーには何も表示しない
        announcements = []
    
    # 最新5件まで表示（フィルタリング後にスライス）
    announcements = announcements[:5]
    
    return render(request, "home.html", {
        'announcements': announcements
    })

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)

def health_check(request):
    """ヘルスチェック用エンドポイント"""
    return HttpResponse("OK", content_type="text/plain")

def user_login(request):
    login_form = LoginForm(request.POST or None)
    if login_form.is_valid():
        username_or_email = login_form.cleaned_data.get('username')
        password = login_form.cleaned_data.get('password')
        
        # まずユーザー名で認証を試行
        user = authenticate(username=username_or_email, password=password)
        
        # ユーザー名で認証できない場合、メールアドレスで検索して認証を試行
        if user is None:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user:
            if user.is_active:
                login(request, user)
                return redirect('agri_app:home')
            else:
                messages.error(request, 'アカウントがアクティブではありません。')
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています。')

    return render(request, 'user/login.html', context={
        'login_form': login_form
    })

# @login_required
def user_logout(request):
    logout(request)
    return redirect('agri_app:user_login')

@login_required
def s3_file_list_view(request):
    # form変数を関数の最初で初期化
    form = UploadFileForm()
    
    try:
        if request.method == 'POST':
            if 'upload' in request.POST:
                print(f"アップロードリクエスト受信: {request.FILES}")
                form = UploadFileForm(request.POST, request.FILES)
                print(f"フォーム有効性: {form.is_valid()}")
                if form.is_valid():
                    try:
                        print(f"アップロード開始: {request.FILES['file'].name}")
                        upload_file_to_s3(request.FILES['file'])
                        print("アップロード成功")
                        messages.success(request, 'ファイルが正常にアップロードされました。')
                        return redirect('agri_app:s3_file_list')
                    except Exception as e:
                        print(f"アップロードエラー: {str(e)}")
                        messages.error(request, f'ファイルのアップロードに失敗しました: {str(e)}')
                else:
                    print(f"フォームエラー: {form.errors}")
                    messages.error(request, 'ファイルのアップロードに失敗しました。')
            elif 'delete' in request.POST:
                key_to_delete = request.POST.get('file_key')
                if key_to_delete:
                    delete_file_from_s3(key_to_delete)
                    messages.success(request, 'ファイルが正常に削除されました。')
                    return redirect('agri_app:s3_file_list')
                else:
                    messages.error(request, '削除するファイルが指定されていません。')
        else:
            form = UploadFileForm()

        files = list_s3_files()
        return render(request, 's3_file_list.html', {'files': files, 'form': form})
    except Exception as e:
        messages.error(request, f'S3ファイルリストの取得中にエラーが発生しました: {str(e)}')
        return render(request, 's3_file_list.html', {'files': [], 'form': form})

# ユーザー管理機能
@login_required
def user_list(request):
    """ユーザー一覧表示"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    search_form = UserSearchForm(request.GET)
    users = User.objects.all().order_by('username')
    
    if search_form.is_valid():
        username = search_form.cleaned_data.get('username')
        first_name = search_form.cleaned_data.get('first_name')
        role = search_form.cleaned_data.get('role')
        
        if username:
            users = users.filter(username__icontains=username)
        if first_name:
            users = users.filter(first_name__icontains=first_name)
        if role:
            if role == 'admin':
                users = users.filter(is_staff=True)
            elif role == 'staff':
                users = users.filter(is_staff=False, is_superuser=False)
            elif role == 'guest':
                users = users.filter(is_active=False)
    
    return render(request, 'user_management/user_list.html', {
        'users': users,
        'search_form': search_form
    })

@login_required
def user_create(request):
    """ユーザー作成"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'ユーザー "{user.username}" を作成しました。')
            return redirect('agri_app:user_list')
    else:
        form = UserCreateForm()
    
    return render(request, 'user_management/user_form.html', {
        'form': form,
        'title': 'ユーザー作成'
    })

@login_required
def user_detail(request, user_id):
    """ユーザー詳細表示"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'user_management/user_detail.html', {
        'user_detail': user
    })

@login_required
def user_edit(request, user_id):
    """ユーザー編集"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'ユーザー "{user.username}" を更新しました。')
            return redirect('agri_app:user_detail', user_id=user.id)
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'user_management/user_form.html', {
        'form': form,
        'title': 'ユーザー編集'
    })

@login_required
def user_delete(request, user_id):
    """ユーザー削除"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'ユーザー "{username}" を削除しました。')
        return redirect('agri_app:user_list')
    
    return render(request, 'user_management/user_confirm_delete.html', {
        'user_detail': user
    })

# プロフィール機能
@login_required
def profile_view(request):
    """プロフィール表示"""
    return render(request, 'profile/profile.html', {
        'user': request.user
    })

@login_required
def profile_edit(request):
    """プロフィール編集"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'プロフィールを更新しました。')
            return redirect('agri_app:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'profile/profile_edit.html', {
        'form': form
    })

@login_required
def password_change(request):
    """パスワード変更"""
    if request.method == 'POST':
        form = ProfilePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'パスワードを変更しました。')
            return redirect('agri_app:profile')
    else:
        form = ProfilePasswordChangeForm(request.user)
    
    return render(request, 'profile/password_change.html', {
        'form': form
    })

def password_reset(request):
    """パスワードリセット"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # メールアドレスでユーザーを検索（大文字小文字を区別しない）
            user = User.objects.get(email__iexact=email)
            # パスワードリセットトークンを生成
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # リセットURLを生成
            reset_url = request.build_absolute_uri(
                reverse('agri_app:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # メール送信
            subject = 'パスワードリセットのご案内'
            message = render_to_string('password_reset/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return redirect('agri_app:password_reset_done')
            except Exception as e:
                # メール送信エラーの場合
                if settings.DEBUG:
                    # 開発環境ではコンソールに出力
                    messages.success(request, f'開発環境: リセットリンクをコンソールに出力しました。URL: {reset_url}')
                    return redirect('agri_app:password_reset_done')
                else:
                    # 本番環境ではエラーメッセージを表示
                    messages.error(request, 'メール送信に失敗しました。しばらく時間をおいて再度お試しください。')
                    
        except User.DoesNotExist:
            messages.error(request, 'このメールアドレスは登録されていません。')
    
    return render(request, 'password_reset/password_reset_form.html')

def password_reset_done(request):
    """パスワードリセットメール送信完了"""
    return render(request, 'password_reset/password_reset_done.html', {
        'debug': settings.DEBUG
    })

def password_reset_confirm(request, uidb64, token):
    """パスワードリセット確認"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            # パスワードの検証
            if not password1 or not password2:
                messages.error(request, 'パスワードを入力してください。')
            elif password1 != password2:
                messages.error(request, 'パスワードが一致しません。')
            elif len(password1) < 8:
                messages.error(request, 'パスワードは8文字以上で入力してください。')
            else:
                try:
                    # Djangoのパスワードバリデーションを使用
                    from django.contrib.auth.password_validation import validate_password
                    validate_password(password1, user)
                    
                    # パスワードを設定
                    user.set_password(password1)
                    user.save()
                    messages.success(request, 'パスワードが正常にリセットされました。')
                    return redirect('agri_app:password_reset_complete')
                except Exception as e:
                    messages.error(request, f'パスワードの設定に失敗しました: {str(e)}')
        
        return render(request, 'password_reset/password_reset_confirm.html')
    else:
        messages.error(request, 'パスワードリセットリンクが無効です。')
        return redirect('agri_app:password_reset')

def password_reset_complete(request):
    """パスワードリセット完了"""
    return render(request, 'password_reset/password_reset_complete.html')

# グループ管理ビュー
@login_required
def group_list(request):
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    search_form = GroupSearchForm(request.GET)
    groups = Group.objects.all()
    
    if search_form.is_valid():
        name = search_form.cleaned_data.get('name')
        is_active = search_form.cleaned_data.get('is_active')
        
        if name:
            groups = groups.filter(name__icontains=name)
        
        if is_active:
            # GroupProfileのis_activeフィールドでフィルタリング
            if is_active == 'True':
                groups = groups.filter(groupprofile__is_active=True)
            elif is_active == 'False':
                groups = groups.filter(groupprofile__is_active=False)
    
    # ページネーション
    paginator = Paginator(groups, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'groups': page_obj,
        'search_form': search_form,
    }
    return render(request, 'group_management/group_list.html', context)

@login_required
def group_create(request):
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        profile_form = GroupProfileForm(request.POST)
        
        if group_form.is_valid() and profile_form.is_valid():
            try:
                group = group_form.save()
                profile = profile_form.save(commit=False)
                profile.group = group
                profile.save()
                
                messages.success(request, 'グループが正常に作成されました。')
                return redirect('agri_app:group_list')
            except Exception as e:
                messages.error(request, f'グループの作成中にエラーが発生しました: {str(e)}')
        else:
            messages.error(request, '入力内容にエラーがあります。確認してください。')
    else:
        group_form = GroupForm()
        profile_form = GroupProfileForm()
    
    context = {
        'group_form': group_form,
        'profile_form': profile_form,
        'title': '新規グループ作成'
    }
    return render(request, 'group_management/group_form.html', context)

@login_required
def group_detail(request, group_id):
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    group = get_object_or_404(Group, id=group_id)
    try:
        profile = group.groupprofile
    except GroupProfile.DoesNotExist:
        profile = None
    
    # グループのメンバー数
    member_count = group.user_set.count()
    
    # グループの権限
    permissions = group.permissions.all()
    
    context = {
        'group': group,
        'profile': profile,
        'member_count': member_count,
        'permissions': permissions,
    }
    return render(request, 'group_management/group_detail.html', context)

@login_required
def group_edit(request, group_id):
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    group = get_object_or_404(Group, id=group_id)
    try:
        profile = group.groupprofile
    except GroupProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        group_form = GroupForm(request.POST, instance=group)
        profile_form = GroupProfileForm(request.POST, instance=profile)
        
        if group_form.is_valid() and profile_form.is_valid():
            try:
                group = group_form.save()
                profile = profile_form.save(commit=False)
                profile.group = group
                profile.save()
                
                messages.success(request, 'グループが正常に更新されました。')
                return redirect('agri_app:group_detail', group_id=group.id)
            except Exception as e:
                messages.error(request, f'グループの更新中にエラーが発生しました: {str(e)}')
        else:
            messages.error(request, '入力内容にエラーがあります。確認してください。')
    else:
        group_form = GroupForm(instance=group)
        profile_form = GroupProfileForm(instance=profile)
    
    context = {
        'group_form': group_form,
        'profile_form': profile_form,
        'group': group,
        'title': 'グループ編集'
    }
    return render(request, 'group_management/group_form.html', context)

@login_required
def group_delete(request, group_id):
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'グループ「{group_name}」が削除されました。')
        return redirect('agri_app:group_list')
    
    context = {
        'group': group,
    }
    return render(request, 'group_management/group_confirm_delete.html', context)

@login_required
def group_members(request, group_id):
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        member_form = GroupMemberForm(request.POST, group=group)
        if member_form.is_valid():
            # 現在のメンバーをクリア
            group.user_set.clear()
            
            # 新しいメンバーを追加
            users = member_form.cleaned_data.get('users', [])
            group.user_set.add(*users)
            
            messages.success(request, 'グループメンバーが更新されました。')
            return redirect('agri_app:group_detail', group_id=group.id)
    else:
        member_form = GroupMemberForm(group=group)
    
    context = {
        'group': group,
        'member_form': member_form,
    }
    return render(request, 'group_management/group_members.html', context)

@login_required
def announcement_list(request):
    """お知らせ一覧表示"""
    # 権限チェック: スーパーユーザーのみアクセス可能
    if not request.user.is_superuser:
        messages.error(request, 'この機能にアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    search_form = AnnouncementSearchForm(request.GET or None)
    announcements = Announcement.objects.all()
    
    if search_form.is_valid():
        keyword = search_form.cleaned_data.get('keyword')
        priority = search_form.cleaned_data.get('priority')
        status = search_form.cleaned_data.get('status')
        target_type = search_form.cleaned_data.get('target_type')
        target_group = search_form.cleaned_data.get('target_group')
        
        if keyword:
            announcements = announcements.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        
        if priority:
            announcements = announcements.filter(priority=priority)
        
        if target_type:
            if target_type == 'all_groups':
                announcements = announcements.filter(is_all_groups=True)
            elif target_type == 'specific_groups':
                announcements = announcements.filter(is_all_groups=False)
        
        if target_group:
            announcements = announcements.filter(target_groups=target_group)
        
        if status:
            now = timezone.now()
            if status == 'active':
                announcements = announcements.filter(
                    is_active=True,
                    start_date__lte=now,
                    end_date__gte=now
                )
            elif status == 'inactive':
                announcements = announcements.filter(is_active=False)
            elif status == 'expired':
                announcements = announcements.filter(end_date__lt=now)
            elif status == 'future':
                announcements = announcements.filter(start_date__gt=now)
    
    # 日付順でソート
    announcements = announcements.order_by('-start_date')
    
    return render(request, 'announcement/announcement_list.html', {
        'announcements': announcements,
        'search_form': search_form
    })


@login_required
def announcement_create(request):
    """お知らせ作成"""
    # 権限チェック: スーパーユーザーのみアクセス可能
    if not request.user.is_superuser:
        messages.error(request, 'この機能にアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            form.save_m2m()  # ManyToManyフィールドを保存
            messages.success(request, 'お知らせが正常に作成されました。')
            return redirect('agri_app:announcement_list')
        else:
            messages.error(request, 'お知らせの作成に失敗しました。')
    else:
        form = AnnouncementForm()
    
    return render(request, 'announcement/announcement_form.html', {
        'form': form,
        'title': 'お知らせ作成'
    })


@login_required
def announcement_detail(request, announcement_id):
    """お知らせ詳細表示"""
    # 権限チェック: スーパーユーザーのみアクセス可能
    if not request.user.is_superuser:
        messages.error(request, 'この機能にアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    
    return render(request, 'announcement/announcement_detail.html', {
        'announcement': announcement
    })


@login_required
def announcement_edit(request, announcement_id):
    """お知らせ編集"""
    # 権限チェック: スーパーユーザーのみアクセス可能
    if not request.user.is_superuser:
        messages.error(request, 'この機能にアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'お知らせが正常に更新されました。')
            return redirect('agri_app:announcement_list')
        else:
            messages.error(request, 'お知らせの更新に失敗しました。')
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'announcement/announcement_form.html', {
        'form': form,
        'announcement': announcement,
        'title': 'お知らせ編集'
    })


@login_required
def announcement_delete(request, announcement_id):
    """お知らせ削除"""
    # 権限チェック: スーパーユーザーのみアクセス可能
    if not request.user.is_superuser:
        messages.error(request, 'この機能にアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'お知らせが正常に削除されました。')
        return redirect('agri_app:announcement_list')
    
    return render(request, 'announcement/announcement_confirm_delete.html', {
        'announcement': announcement
    })


@login_required
def announcement_send_email(request, announcement_id):
    """お知らせの手動メール送信"""
    # 権限チェック: スーパーユーザーのみアクセス可能
    if not request.user.is_superuser:
        messages.error(request, 'この機能にアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    
    if request.method == 'POST':
        if announcement.can_send_email():
            result = announcement.send_manual_email()
            
            if result.get('error'):
                messages.error(request, f'メール送信に失敗しました: {result["error"]}')
            elif result['success_count'] > 0:
                success_message = f'メール送信が完了しました。成功: {result["success_count"]}件'
                if result['failed_users']:
                    failed_count = len(result['failed_users'])
                    success_message += f', 失敗: {failed_count}件'
                messages.success(request, success_message)
                
                # 失敗したユーザーがいる場合は警告メッセージを表示
                if result['failed_users']:
                    failed_users_text = ', '.join([f'{user["user"]}({user["email"]})' for user in result['failed_users'][:5]])
                    if len(result['failed_users']) > 5:
                        failed_users_text += f' 他{len(result["failed_users"]) - 5}名'
                    messages.warning(request, f'送信失敗ユーザー: {failed_users_text}')
            else:
                messages.warning(request, '送信対象ユーザーが見つかりませんでした。')
        else:
            messages.error(request, 'メール送信の条件を満たしていません。')
    
    return redirect('agri_app:announcement_detail', announcement_id=announcement_id)


@login_required
def style_settings(request):
    """スタイル設定管理ビュー"""
    # 権限チェック: スーパーユーザーのみアクセス可能
    if not request.user.is_superuser:
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    if request.method == 'POST':
        # スタイル設定の更新
        style_id = request.POST.get('style_id')
        if style_id:
            try:
                style_setting = StyleSettings.objects.get(id=style_id)
                style_setting.is_default = True
                style_setting.save()
                messages.success(request, f'スタイル設定「{style_setting.name}」をデフォルトに設定しました。')
            except StyleSettings.DoesNotExist:
                messages.error(request, '指定されたスタイル設定が見つかりません。')
        else:
            messages.error(request, 'スタイル設定が指定されていません。')
    
    # 現在のスタイル設定を取得
    current_style = StyleSettings.get_active_style()
    style_settings_list = StyleSettings.objects.all().order_by('-is_default', 'name')
    
    return render(request, 'style_settings/style_settings.html', {
        'current_style': current_style,
        'style_settings_list': style_settings_list
    })

@login_required
def email_settings_list(request):
    """メール送信設定一覧表示"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    search_form = EmailSettingsForm(request.GET)
    email_settings = EmailSettings.objects.all()
    
    if search_form.is_valid():
        name = search_form.cleaned_data.get('name')
        is_active = search_form.cleaned_data.get('is_active')
        
        if name:
            email_settings = email_settings.filter(name__icontains=name)
        
        if is_active:
            if is_active == 'True':
                email_settings = email_settings.filter(is_active=True)
            elif is_active == 'False':
                email_settings = email_settings.filter(is_active=False)
    
    # ページネーション
    paginator = Paginator(email_settings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'email_settings': page_obj,
        'search_form': search_form,
    }
    return render(request, 'email_settings/email_settings_list.html', context)

@login_required
def email_settings_create(request):
    """メール送信設定作成"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    if request.method == 'POST':
        form = EmailSettingsForm(request.POST)
        if form.is_valid():
            email_setting = form.save()
            messages.success(request, f'メール送信設定「{email_setting.name}」を作成しました。')
            return redirect('agri_app:email_settings_list')
    else:
        form = EmailSettingsForm()
    
    return render(request, 'email_settings/email_settings_form.html', {
        'form': form,
        'title': 'メール送信設定作成'
    })

@login_required
def email_settings_detail(request, email_setting_id):
    """メール送信設定詳細表示"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    email_setting = get_object_or_404(EmailSettings, pk=email_setting_id)
    return render(request, 'email_settings/email_settings_detail.html', {
        'email_setting': email_setting
    })

@login_required
def email_settings_edit(request, email_setting_id):
    """メール送信設定編集"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    email_setting = get_object_or_404(EmailSettings, pk=email_setting_id)
    
    if request.method == 'POST':
        form = EmailSettingsForm(request.POST, instance=email_setting)
        if form.is_valid():
            form.save()
            messages.success(request, f'メール送信設定「{email_setting.name}」を更新しました。')
            return redirect('agri_app:email_settings_detail', email_setting_id=email_setting.id)
    else:
        form = EmailSettingsForm(instance=email_setting)
    
    return render(request, 'email_settings/email_settings_form.html', {
        'form': form,
        'title': 'メール送信設定編集'
    })

@login_required
def email_settings_delete(request, email_setting_id):
    """メール送信設定削除"""
    # 権限チェック: 管理者またはスーパーユーザーのみアクセス可能
    if not request.user.is_authenticated or (not request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'このページにアクセスする権限がありません。')
        return redirect('agri_app:home')
    
    email_setting = get_object_or_404(EmailSettings, pk=email_setting_id)
    
    if request.method == 'POST':
        email_setting_name = email_setting.name
        email_setting.delete()
        messages.success(request, f'メール送信設定「{email_setting_name}」が削除されました。')
        return redirect('agri_app:email_settings_list')
    
    return render(request, 'email_settings/email_settings_confirm_delete.html', {
        'email_setting': email_setting
    })