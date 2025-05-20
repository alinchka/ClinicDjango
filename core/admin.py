from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Doctor, UserRole, Appointment, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserRoleInline(admin.StackedInline):
    model = UserRole
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (UserRoleInline, UserProfileInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_patronymic', 'get_role')
    
    def get_patronymic(self, obj):
        try:
            return obj.profile.patronymic
        except UserProfile.DoesNotExist:
            return ''
    get_patronymic.short_description = 'Отчество'
    
    def get_role(self, obj):
        try:
            return obj.role.get_role_display()
        except UserRole.DoesNotExist:
            return 'Нет роли'
    get_role.short_description = 'Роль'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'specialty')
    search_fields = ('last_name', 'first_name', 'patronymic', 'specialty')
    
    def get_full_name(self, obj):
        full_name = f"{obj.last_name} {obj.first_name}"
        if obj.patronymic:
            full_name += f" {obj.patronymic}"
        return full_name
    get_full_name.short_description = 'ФИО'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'doctor', 'appointment_time', 'created_at')
    list_filter = ('doctor', 'appointment_time')
    search_fields = ('user__username', 'doctor__last_name', 'doctor__first_name')
    date_hierarchy = 'appointment_time'

# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin) 