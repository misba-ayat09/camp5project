# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .models import Book, Author
import re

# Validator for user ID (must contain both letters and numbers)
def validate_userid(value):
    if not re.search(r'[a-zA-Z]', value) or not re.search(r'\d', value):
        raise ValidationError("User ID must contain both letters and numbers.")

# Validator for password (must be at least 8 characters and contain both letters and numbers)
def validate_password(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[a-zA-Z]', value) or not re.search(r'\d', value):
        raise ValidationError("Password must contain both letters and numbers.")

class RegistrationForm(forms.Form):
    firstname = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    lastname = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    emailid = forms.EmailField(
        required=True,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={'placeholder': 'Example@gmail.com'})
    )
    userid = forms.CharField(
        max_length=50,
        required=True,
        validators=[validate_userid],
        widget=forms.TextInput(attrs={'placeholder': 'ABCED12'})
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        validators=[validate_password],
        widget=forms.PasswordInput(attrs={'placeholder': 'password only contain 8 characters only both numberic and alphabet'})
    )
    confirm_password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    # Custom validation for passwords
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")

        return cleaned_data
def validate_userid(value):
    if not re.search(r'[a-zA-Z]', value) or not re.search(r'\d', value):
        raise ValidationError("User ID must contain both letters and numbers.")

# Validator for password (must contain both letters and numbers)
def validate_password(value):
    if not re.search(r'[a-zA-Z]', value) or not re.search(r'\d', value):
        raise ValidationError("Password must contain both letters and numbers.")

class LoginForm(forms.Form):
    userid = forms.CharField(
        max_length=50,
        required=True,
        validators=[validate_userid],
        widget=forms.TextInput(attrs={'placeholder': 'User ID'})
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        validators=[validate_password],
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )



class BookForm(forms.ModelForm):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        label='Author',
        empty_label='Select Author',
        widget=forms.Select(attrs={'class': 'author-select'})
    )

    class Meta:
        model = Book
        fields = ['book_id', 'name', 'author', 'genre', 'rent', 'status', 'copies', 'rental_days', 'cover_image', 'pdf']
        widgets = {
            'genre': forms.Select(choices=[
                ('Romance', 'Romance'),
                ('Comic', 'Comic'),
                ('Horror', 'Horror'),
                ('Research', 'Research'),
            ]),
            'rent': forms.Select(choices=[
                ('100', '100'),
                ('200', '200'),
                ('300', '300'),
            ]),
            'status': forms.Select(choices=[
                ('Available', 'Available'),
                ('Unavailable', 'Unavailable'),
            ]),
        }

class PaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('credit-card', 'Credit Card'),
        ('bank-transfer', 'Bank Transfer'),
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, required=True)
    upi_id = forms.CharField(required=False)
    card_number = forms.CharField(required=False)
    expiry_date = forms.CharField(required=False)
    cvc = forms.CharField(required=False)
    account_number = forms.CharField(required=False)
    ifsc_code = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        upi_id = cleaned_data.get('upi_id')
        card_number = cleaned_data.get('card_number')
        expiry_date = cleaned_data.get('expiry_date')
        cvc = cleaned_data.get('cvc')
        account_number = cleaned_data.get('account_number')
        ifsc_code = cleaned_data.get('ifsc_code')

        # Validate UPI payment
        if payment_method == 'upi':
            if not upi_id:
                self.add_error('upi_id', "UPI ID is required for UPI payment.")

        # Validate Credit Card payment
        elif payment_method == 'credit-card':
            if not card_number:
                self.add_error('card_number', "Card number is required for credit card payment.")
            if not expiry_date:
                self.add_error('expiry_date', "Expiry date is required for credit card payment.")
            if not cvc:
                self.add_error('cvc', "CVC is required for credit card payment.")

        # Validate Bank Transfer payment
        elif payment_method == 'bank-transfer':
            if not account_number:
                self.add_error('account_number', "Account number is required for bank transfer.")
            if not ifsc_code:
                self.add_error('ifsc_code', "IFSC code is required for bank transfer.")

        return cleaned_data

