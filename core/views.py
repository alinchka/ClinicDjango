from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .forms import UserRegistrationForm, AppointmentForm, DoctorForm, AdminUserForm
from .models import Doctor, Appointment, UserRole

def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def make_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            
            existing_appointment = Appointment.objects.filter(
                doctor=appointment.doctor,
                appointment_time=appointment.appointment_time
            ).exists()
            
            if existing_appointment:
                messages.error(request, 'Это время уже занято. Пожалуйста, выберите другое время.')
            else:
                appointment.save()
                messages.success(request, 'Запись на прием создана успешно!')
                return redirect('my_appointments')
    else:
        form = AppointmentForm()
    
    return render(request, 'core/make_appointment.html', {'form': form})

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(
        user=request.user,
        appointment_time__gte=timezone.now()
    ).order_by('appointment_time')
    return render(request, 'core/my_appointments.html', {'appointments': appointments})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not (request.user == appointment.user or request.user.is_superuser or 
            (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        messages.error(request, 'У вас нет прав для отмены этой записи')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Запись успешно отменена')
        
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin'):
            return redirect('admin_appointments')
        return redirect('my_appointments')
    
    return render(request, 'core/cancel_appointment.html', {'appointment': appointment})

@login_required
def admin_panel(request):
    if request.user.is_superuser:
        try:
            user_role = UserRole.objects.get(user=request.user)
        except UserRole.DoesNotExist:
            UserRole.objects.create(user=request.user, role='admin')
    else:
        try:
            if request.user.role.role != 'admin':
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('home')
        except UserRole.DoesNotExist:
            messages.error(request, 'У вас нет доступа к этой странице')
            return redirect('home')
    
    now = timezone.localtime(timezone.now())
    today = now.date()
    tomorrow = today + timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    tomorrow_start = timezone.make_aware(datetime.combine(tomorrow, datetime.min.time()))
    tomorrow_end = timezone.make_aware(datetime.combine(tomorrow, datetime.max.time()))
    
    today_appointments_count = Appointment.objects.filter(
        appointment_time__range=(today_start, today_end)
    ).count()
    
    tomorrow_appointments_count = Appointment.objects.filter(
        appointment_time__range=(tomorrow_start, tomorrow_end)
    ).count()
    
    total_active_appointments = Appointment.objects.filter(
        appointment_time__gte=now
    ).count()
    
    total_users = User.objects.count()
    total_doctors = Doctor.objects.count()
    new_users_week = User.objects.filter(
        date_joined__gte=week_ago
    ).count()
    
    context = {
        'today_appointments_count': today_appointments_count,
        'tomorrow_appointments_count': tomorrow_appointments_count,
        'total_active_appointments': total_active_appointments,
        'total_users': total_users,
        'total_doctors': total_doctors,
        'new_users_week': new_users_week,
    }
    
    return render(request, 'core/admin/panel.html', context)

@login_required
def admin_appointments(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    now = timezone.localtime(timezone.now())
    
    future_appointments = Appointment.objects.filter(
        appointment_time__gte=now
    ).order_by('appointment_time')
    
    past_appointments = Appointment.objects.filter(
        appointment_time__lt=now
    ).order_by('-appointment_time')
    
    appointments = list(future_appointments) + list(past_appointments)
    
    return render(request, 'core/admin/appointments.html', {
        'appointments': appointments,
        'now': now
    })

@login_required
def admin_doctors(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    doctors = Doctor.objects.all()
    form = DoctorForm()
    return render(request, 'core/admin/doctors.html', {'doctors': doctors, 'form': form})

@login_required
def admin_add_doctor(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Врач успешно добавлен')
            return redirect('admin_doctors')
        else:
            messages.error(request, 'Ошибка при добавлении врача')
    return redirect('admin_doctors')

@login_required
def admin_edit_doctor(request, doctor_id):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные врача обновлены')
        else:
            messages.error(request, 'Ошибка при обновлении данных')
    return redirect('admin_doctors')

@login_required
def admin_delete_doctor(request, doctor_id):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        active_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_time__gte=timezone.now()
        ).exists()
        
        if active_appointments:
            messages.error(request, 'Невозможно удалить врача с активными записями')
        else:
            doctor.delete()
            messages.success(request, 'Врач успешно удален')
    return redirect('admin_doctors')

@login_required
def admin_users(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    users = User.objects.select_related('role').all().order_by('-date_joined')
    return render(request, 'core/admin/users.html', {'users': users})

@login_required
def admin_toggle_user_role(request, user_id):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        if target_user == request.user:
            messages.error(request, 'Вы не можете изменить свою собственную роль')
            return redirect('admin_users')
            
        try:
            user_role = target_user.role
            if user_role.role == 'user':
                user_role.role = 'admin'
                messages.success(request, f'Пользователь {target_user.username} теперь администратор')
            else:
                user_role.role = 'user'
                messages.success(request, f'Пользователь {target_user.username} больше не администратор')
            user_role.save()
        except UserRole.DoesNotExist:
            UserRole.objects.create(user=target_user, role='admin')
            messages.success(request, f'Пользователь {target_user.username} теперь администратор')
    
    return redirect('admin_users')

@login_required
def admin_delete_user(request, user_id):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        if user == request.user:
            messages.error(request, 'Вы не можете удалить свой собственный аккаунт')
            return redirect('admin_users')
            
        active_appointments = Appointment.objects.filter(
            user=user,
            appointment_time__gte=timezone.now()
        ).exists()
        
        if active_appointments:
            messages.error(request, 'Невозможно удалить пользователя с активными записями')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'Пользователь {username} успешно удален')
    
    return redirect('admin_users')

@login_required
def admin_add_user(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Пользователь {user.username} успешно создан')
            return redirect('admin_users')
        else:
            messages.error(request, 'Ошибка при создании пользователя')
    else:
        form = AdminUserForm()
    
    return render(request, 'core/admin/user_form.html', {
        'form': form,
        'title': 'Добавление пользователя',
        'button_text': 'Добавить'
    })

@login_required
def admin_edit_user(request, user_id):
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role.role == 'admin')):
        return redirect('home')
    
    try:
        user = User.objects.select_related('profile', 'role').get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден')
        return redirect('admin_users')
    
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Невозможно редактировать суперпользователя')
        return redirect('admin_users')
    
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Данные пользователя {user.username} обновлены')
                return redirect('admin_users')
            except Exception as e:
                messages.error(request, f'Ошибка при обновлении данных: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле {form.fields[field].label}: {error}')
    else:
        try:
            profile_data = {
                'patronymic': user.profile.patronymic,
                'birth_date': user.profile.birth_date,
            }
        except (UserProfile.DoesNotExist, AttributeError):
            profile_data = {}

        try:
            role_data = {'role': user.role.role}
        except (UserRole.DoesNotExist, AttributeError):
            role_data = {'role': 'user'}

        initial_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            **profile_data,
            **role_data,
        }
        form = AdminUserForm(instance=user, initial=initial_data)
    
    return render(request, 'core/admin/user_form.html', {
        'form': form,
        'title': f'Редактирование пользователя {user.username}',
        'button_text': 'Сохранить',
        'user_being_edited': user
    }) 