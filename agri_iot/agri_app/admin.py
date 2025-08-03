from django.contrib import admin
from .models import UserProfile, GroupProfile, StyleSettings, Announcement

# Register your models here.

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'start_date', 'end_date', 'is_active', 'created_by', 'create_at']
    list_filter = ['priority', 'is_active', 'start_date', 'end_date', 'created_by']
    search_fields = ['title', 'content', 'created_by__username']
    readonly_fields = ['created_by', 'create_at', 'update_at']
    filter_horizontal = ['target_groups']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'content', 'priority')
        }),
        ('表示設定', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('対象グループ', {
            'fields': ('target_groups',),
            'description': '何も選択しない場合は全グループに表示されます'
        }),
        ('作成情報', {
            'fields': ('created_by', 'create_at', 'update_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新規作成時のみ
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by')

@admin.register(StyleSettings)
class StyleSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'active_style', 'is_default', 'description', 'create_at', 'update_at']
    list_filter = ['active_style', 'is_default', 'create_at']
    search_fields = ['name', 'description']
    readonly_fields = ['create_at', 'update_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'active_style', 'is_default', 'description')
        }),
        ('タイムスタンプ', {
            'fields': ('create_at', 'update_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # デフォルト設定の場合、他の設定のデフォルトフラグをFalseにする
        if obj.is_default:
            StyleSettings.objects.exclude(pk=obj.pk).update(is_default=False)
        super().save_model(request, obj, form, change)
