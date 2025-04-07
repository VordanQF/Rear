from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    avatar = models.URLField(null=True, blank=True)
    telegram_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    role = models.CharField(max_length=30, choices=[('svo', 'Боец СВО'),
                                                   ('volunteer', 'Волонтёр'),
                                                   ('mentor', 'Наставник'),
                                                    ('peresel', 'Переселенец'),
                                                    ('family', 'Семья бойцов'),
                                                   ('admin', 'Администратор')],
                            default='user')
    age = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    city = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"


class HelpRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey('main.User', on_delete=models.CASCADE, related_name='help_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    assigned_volunteer = models.ForeignKey(
        'main.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests'
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    telegram_notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.status})"


class Feedback(models.Model):
    request = models.OneToOneField(HelpRequest, on_delete=models.CASCADE, related_name='feedback')
    author = models.ForeignKey('main.User', on_delete=models.SET_NULL, null=True)
    rating = models.PositiveSmallIntegerField()  # от 1 до 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Оценка {self.rating} для {self.request}"


class MentorProfile(models.Model):
    user = models.OneToOneField('main.User', on_delete=models.CASCADE, related_name='mentor_profile')
    expertise = models.CharField(max_length=255)
    available = models.BooleanField(default=True)
    schedule_notes = models.TextField(blank=True, null=True)  # например, "доступен по вечерам"

    def __str__(self):
        return f"Наставник: {self.user.username}"


class Institution(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    website = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=[
        ('legal', 'Юридическая помощь'),
        ('medical', 'Медицинская помощь'),
        ('psychological', 'Психологическая помощь'),
        ('housing', 'Жильё и быт'),
    ])

    def __str__(self):
        return self.name


class TelegramMessageLog(models.Model):
    user = models.ForeignKey('main.User', on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
