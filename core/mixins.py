from django.utils import timezone

class TimezoneMixin:
    def save(self, *args, **kwargs):
        if not self.id and hasattr(self, 'date_joined') and not timezone.is_aware(self.date_joined):
            self.date_joined = timezone.make_aware(self.date_joined)
        super().save(*args, **kwargs) 