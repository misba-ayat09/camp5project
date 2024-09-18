from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(default=False)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# Function to return the current date
def get_current_date():
    return datetime.now().date()

# Function to return the end date as 1 year from the current date
def get_default_end_date():
    return get_current_date() + timedelta(days=365)

# Model for book details

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    book_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    GENRE_CHOICES = [
        ('Romance', 'Romance'),
        ('Comic', 'Comic'),
        ('Horror', 'Horror'),
        ('Research', 'Research'),
    ]
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)

    RENT_CHOICES = [
        ('100', '100'),
        ('200', '200'),
        ('300', '300'),
    ]
    rent = models.CharField(max_length=10, choices=RENT_CHOICES)

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    copies = models.IntegerField(default=1)
    rental_days = models.IntegerField(default=7)

    # New fields
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    pdf = models.FileField(upload_to='book_pdfs/', null=True, blank=True)

    def __str__(self):
        return self.name

# Model for rental records
class RentBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} rented {self.book.name}"



class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('credit-card', 'Credit Card'),
        ('bank-transfer', 'Bank Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)  # Format: MM/YYYY
    cvc = models.CharField(max_length=4, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.payment_method} - {self.amount}"

    def clean(self):
        # Ensure that the necessary fields for the chosen payment method are filled in
        if self.payment_method == 'upi' and not self.upi_id:
            raise ValidationError("UPI ID is required for UPI payment.")
        if self.payment_method == 'credit-card':
            if not self.card_number:
                raise ValidationError("Card number is required for credit card payment.")
            if not self.expiry_date:
                raise ValidationError("Expiry date is required for credit card payment.")
            if not self.cvc:
                raise ValidationError("CVC is required for credit card payment.")
        if self.payment_method == 'bank-transfer':
            if not self.account_number:
                raise ValidationError("Account number is required for bank transfer.")
            if not self.ifsc_code:
                raise ValidationError("IFSC code is required for bank transfer.")


# Signal to create and save UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
