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

from .models import UserProfile, GroupProfile
from .model.form.user_form import UserSearchForm, UserForm
from .model.form.user_management_form import UserCreateForm, UserEditForm
from .model.form.group_form import GroupSearchForm, GroupForm, GroupProfileForm, GroupMemberForm
from .model.form.login_user_form import LoginForm
from .model.form.profile_form import ProfileEditForm, ProfilePasswordChangeForm
from .utils.aws_s3 import list_s3_files, upload_file_to_s3, delete_file_from_s3
from .model.form.file_form import UploadFileForm


def home(request):
    return render(request, "home.html")

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    print("server error")
    return render(request, '500.html', status=500)

def user_login(request):
    login_form = LoginForm(request.POST or None)
    if login_form.is_valid():
        username_or_email = login_form.cleaned_data.get('username')
        password = login_form.cleaned_data.get('password')
        
        # デバッグ用：入力値をログ出力
        print(f"ログイン試行: username_or_email={username_or_email}")
        
        # まずユーザー名で認証を試行
        user = authenticate(username=username_or_email, password=password)
        print(f"ユーザー名での認証結果: {user}")
        
        # ユーザー名で認証できない場合、メールアドレスで検索して認証を試行
        if user is None:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                print(f"メールアドレスでユーザー発見: {user_obj.username}")
                user = authenticate(username=user_obj.username, password=password)
                print(f"メールアドレス経由での認証結果: {user}")
            except User.DoesNotExist:
                print(f"メールアドレスでユーザーが見つかりません: {username_or_email}")
                user = None
        
        if user:
            if user.is_active:
                login(request, user)
                print(f"ログイン成功: {user.username}")
                return redirect('agri_app:home')
            else:
                print(f"アカウントが非アクティブ: {user.username}")
                messages.error(request, 'アカウントがアクティブではありません。')
        else:
            print("認証失敗")
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
    try:
        if request.method == 'POST':
            if 'upload' in request.POST:
                form = UploadFileForm(request.POST, request.FILES)
                if form.is_valid():
                    upload_file_to_s3(request.FILES['file'])
                    messages.success(request, 'ファイルが正常にアップロードされました。')
                    return redirect('agri_app:s3_file_list')
                else:
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
        return render(request, 's3_file_list.html', {'files': [], 'form': UploadFileForm()})

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
                    print(f"メール送信エラー（開発環境）: {e}")
                    print(f"リセットURL: {reset_url}")
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