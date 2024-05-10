from django.db import models

# Create your models here.


class StaffProfile(models.Model):
    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
    email = models.EmailField(max_length=100)
    personal_email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    phone = models.IntegerField()
    # image = models.ImageField(upload_to='profile_image', blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    approved = models.BooleanField(default=True)



    def __str__(self):
        return f"{self.first_name} {self.last_name}"
