from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Appointment, Doctor, UserProfile, UserRole
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    patronymic = forms.CharField(max_length=150, required=False, label='Отчество')
    birth_date = forms.DateField(required=True, label='Дата рождения',
                               widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'patronymic', 'birth_date', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Зарегистрироваться', css_class='btn btn-primary w-100'))
        self.helper.layout = Layout(
            Div(
                Div(Field('username', css_class='form-control'), css_class='col-md-6'),
                Div(Field('email', css_class='form-control'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('first_name', css_class='form-control'), css_class='col-md-6'),
                Div(Field('last_name', css_class='form-control'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('patronymic', css_class='form-control'), css_class='col-md-6'),
                Div(Field('birth_date', css_class='form-control'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('password1', css_class='form-control'), css_class='col-md-6'),
                Div(Field('password2', css_class='form-control'), css_class='col-md-6'),
                css_class='row'
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(
                user=user,
                patronymic=self.cleaned_data['patronymic'],
                birth_date=self.cleaned_data['birth_date']
            )
            # Создаем роль пользователя
            UserRole.objects.create(
                user=user,
                role='user'
            )
        return user

class AdminUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-control'}))
    patronymic = forms.CharField(required=False, label='Отчество', widget=forms.TextInput(attrs={'class': 'form-control'}))
    birth_date = forms.CharField(required=False, label='Дата рождения', widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    role = forms.ChoiceField(
        choices=[('user', 'Пользователь'), ('admin', 'Администратор')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(required=False, label='Активен', initial=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        if instance:
            # Заполняем поля из профиля пользователя
            try:
                if hasattr(instance, 'profile'):
                    self.initial['patronymic'] = instance.profile.patronymic
                    # Форматируем дату в читаемый вид
                    birth_date = instance.profile.birth_date
                    self.initial['birth_date'] = birth_date.strftime('%d.%m.%Y') if birth_date else ''
                else:
                    profile = UserProfile.objects.get(user=instance)
                    self.initial['patronymic'] = profile.patronymic
                    birth_date = profile.birth_date
                    self.initial['birth_date'] = birth_date.strftime('%d.%m.%Y') if birth_date else ''
            except UserProfile.DoesNotExist:
                pass
            
            # Заполняем поле роли
            try:
                if hasattr(instance, 'role'):
                    self.initial['role'] = instance.role.role
                else:
                    user_role = UserRole.objects.get(user=instance)
                    self.initial['role'] = user_role.role
            except UserRole.DoesNotExist:
                self.initial['role'] = 'user'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Сохранить', css_class='btn btn-primary'))
        self.helper.layout = Layout(
            Div(
                Div(Field('username', css_class='form-control'), css_class='col-md-6'),
                Div(Field('email', css_class='form-control'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('first_name', css_class='form-control'), css_class='col-md-4'),
                Div(Field('last_name', css_class='form-control'), css_class='col-md-4'),
                Div(Field('patronymic', css_class='form-control'), css_class='col-md-4'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('birth_date', css_class='form-control', readonly=True), css_class='col-md-6'),
                Div(Field('role', css_class='form-control'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('is_active', css_class='form-check-input'), css_class='col-md-12'),
                css_class='row mb-3'
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # Обновляем или создаем роль пользователя
            UserRole.objects.update_or_create(
                user=user,
                defaults={'role': self.cleaned_data['role']}
            )
            
            # Обновляем или создаем профиль пользователя, но НЕ обновляем дату рождения
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'patronymic': self.cleaned_data.get('patronymic', ''),
                }
            )
        return user

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_time']
        labels = {
            'doctor': 'Врач',
            'appointment_time': 'Время приёма'
        }
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            )
        }

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data.get('appointment_time')
        if appointment_time and not timezone.is_aware(appointment_time):
            appointment_time = timezone.make_aware(appointment_time)
        return appointment_time

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].empty_label = 'Выберите врача'
        self.fields['appointment_time'].input_formats = ['%Y-%m-%dT%H:%M']

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialty']
        labels = {
            'name': 'ФИО',
            'specialty': 'Специализация'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'})
        } 