from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    patronymic = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    birth_date = models.DateField(verbose_name='Дата рождения')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.get_full_name()}"

class UserRole(models.Model):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Doctor(models.Model):
    name = models.CharField(max_length=100, verbose_name='ФИО')
    specialty = models.CharField(max_length=100, verbose_name='Специализация')

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'

    def __str__(self):
        return f"{self.name} - {self.specialty}"

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_time = models.DateTimeField(verbose_name='Время приёма')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        ordering = ['-appointment_time']

    def __str__(self):
        return f"{self.user.username} к {self.doctor.name} на {self.appointment_time}"

    def clean(self):
        if self.appointment_time.minute % 15 != 0:
            raise ValidationError('Время приёма должно быть кратно 15 минутам')

        if self.appointment_time.hour < 9 or self.appointment_time.hour >= 18:
            raise ValidationError('Время приёма должно быть с 9:00 до 18:00')

        if self.appointment_time.weekday() >= 5:
            raise ValidationError('Нельзя записаться на выходной день')

        if self.appointment_time < timezone.now():
            raise ValidationError('Нельзя записаться на прошедшее время')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 