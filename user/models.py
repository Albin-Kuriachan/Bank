from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from staff.models import StaffProfile


class Profile(models.Model):
    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
    email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    phone = models.IntegerField()
    pan = models.CharField(max_length=10,unique=True)
    aadhaar = models.CharField(max_length=12)
    image = models.ImageField(upload_to='profile_image', blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_staff(self, email, password=None, **extra_fields):
        """
        Creates and saves a staff user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=True, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    customer_id = models.OneToOneField(Profile, on_delete=models.CASCADE, unique=True,null=True)
    staff_id = models.OneToOneField(StaffProfile, on_delete=models.CASCADE, unique=True,null=True)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    reset_password_token = models.CharField(max_length=100,null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['reset_password_token']

    objects = CustomUserManager()



#
# @receiver(post_save, sender=Profile)
# def create_profile(sender, instance, created, **kwargs):
#     # if created and instance.user_type == 'candidate':
#     CustomUser.objects.create(user=instance, email=instance.email,first_name=instance.first_name,last_name=instance.last_name)
#
