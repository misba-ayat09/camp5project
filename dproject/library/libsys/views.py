from django.shortcuts import render,redirect,reverse,get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout,authenticate,login
from .forms import RegistrationForm,LoginForm,BookForm,PaymentForm
from django.contrib.auth.models import User
from .models import Payment, Book, RentBook, UserProfile, Author
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.validators import validate_email
from django.http import HttpResponse,JsonResponse
from dateutil.relativedelta import relativedelta

def home(request):
    return render(request, 'account/home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            emailid = form.cleaned_data.get('emailid')
            userid = form.cleaned_data.get('userid')
            password = form.cleaned_data.get('password')

            if User.objects.filter(username=userid).exists():
                messages.error(request, 'User ID already taken.')
            else:
                # Create the user
                user = User.objects.create_user(
                    username=userid,
                    email=emailid,
                    password=password,
                    first_name=firstname,
                    last_name=lastname
                )

                # Check if the UserProfile already exists before creating a new one
                if not UserProfile.objects.filter(user=user).exists():
                    UserProfile.objects.create(user=user)

                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            userid = form.cleaned_data.get('userid')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = authenticate(username=userid, password=password)
            if user is not None:
                # Check if the user has a UserProfile
                if hasattr(user, 'userprofile'):  # Safely check if UserProfile exists
                    login(request, user)
                    return redirect('customer')  # Redirect to the dashboard after login
                else:
                    messages.error(request, 'User profile does not exist for this user.')
            else:
                messages.error(request, 'Invalid User ID or Password')
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})
def author_page(request):
    return render(request, 'account/author.html')
def membership_page(request):
    return render(request, 'account/membership.html')

def customer(request):
    # Retrieve the logged-in user's first and last name
    firstname = request.user.first_name
    lastname = request.user.last_name

    # Pass the names to the template
    return render(request, 'account/customerpage.html', {
        'firstname': firstname,
        'lastname': lastname
    })



@login_required
def activate_plan(request, plan_duration):
    user_profile = request.user.userprofile

    # Define plan amounts based on duration
    plan_amounts = {
        '6-month': 750,
        '1-year': 1500,
        '2-year': 3000,
    }

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            upi_id = form.cleaned_data.get('upi_id')
            card_number = form.cleaned_data.get('card_number')
            expiry_date = form.cleaned_data.get('expiry_date')
            cvc = form.cleaned_data.get('cvc')
            account_number = form.cleaned_data.get('account_number')
            ifsc_code = form.cleaned_data.get('ifsc_code')

            # Determine the amount based on the plan duration
            amount = plan_amounts.get(plan_duration, 0)

            try:
                # Save the payment details
                payment = Payment.objects.create(
                    user=request.user,
                    payment_method=payment_method,
                    upi_id=upi_id if payment_method == 'upi' else None,
                    card_number=card_number if payment_method == 'credit-card' else None,
                    expiry_date=expiry_date if payment_method == 'credit-card' else None,
                    cvc=cvc if payment_method == 'credit-card' else None,
                    account_number=account_number if payment_method == 'bank-transfer' else None,
                    ifsc_code=ifsc_code if payment_method == 'bank-transfer' else None,
                    amount=amount
                )
                messages.success(request, "Payment successful!")

                # Update subscription details
                user_profile.is_subscribed = True
                user_profile.subscription_start_date = timezone.now().date()
                user_profile.subscription_end_date = (
                    timezone.now().date() + timedelta(days=365) if plan_duration == '1-year' else
                    timezone.now().date() + timedelta(days=730) if plan_duration == '2-year' else
                    timezone.now().date() + timedelta(days=180)
                )
                user_profile.save()

                return redirect('rent_book')
            except Exception as e:
                messages.error(request, f"Error saving payment: {e}")
                return redirect('activate_plan', plan_duration=plan_duration)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PaymentForm()

    return render(request, 'account/payment.html', {'form': form, 'plan_duration': plan_duration, 'plan_amount': plan_amounts.get(plan_duration)})

@login_required
def payment_view(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        plan_type = request.POST.get('plan')

        plan_amounts = {
            '6-month': 750,
            '1-year': 1500,
            '2-year': 3000
        }

        amount = plan_amounts.get(plan_type)

        if amount is None:
            messages.error(request, "Invalid plan selected.")
            return redirect('membership')

        upi_id = request.POST.get('upi_id', None)
        card_number = request.POST.get('card_number', None)
        expiry_date = request.POST.get('expiry_date', None)
        cvc = request.POST.get('cvc', None)
        account_number = request.POST.get('account_number', None)
        ifsc_code = request.POST.get('ifsc_code', None)

        try:
            Payment.objects.create(
                user=request.user,
                payment_method=payment_method,
                amount=amount,
                upi_id=upi_id,
                card_number=card_number,
                expiry_date=expiry_date,
                cvc=cvc,
                account_number=account_number,
                ifsc_code=ifsc_code
            )
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('payment')

        user_profile = request.user.userprofile
        user_profile.is_subscribed = True
        user_profile.subscription_start_date = datetime.now().date()
        user_profile.subscription_end_date = datetime.now().date() + timedelta(
            days=365) if plan_type == '1-year' else timedelta(days=730) if plan_type == '2-year' else timedelta(
            days=180)
        user_profile.save()

        messages.success(request, f"Payment successful! You have activated the {plan_type.replace('-', ' ')} plan.")
        return redirect('rent_book')

    return render(request, 'account/payment.html')



def login_required_view(request, plan_id):
    if request.user.is_authenticated:
        return activate_plan(request, plan_id)
    else:
        messages.info(request, "Please log in first.")
        return redirect(reverse('login') + f'?next={request.path}')

@login_required
def rent_book(request):
    current_date = timezone.now().date()
    one_year_ago = current_date - timedelta(days=365)

    # Check if the user has made a payment within the last year
    membership = Payment.objects.filter(user=request.user, payment_date__gte=one_year_ago).exists()

    if not membership:
        messages.error(request, "You must have an active membership to rent a book.")
        return redirect('membership')

    books = Book.objects.filter(status='Available')
    context = {'books': books}
    return render(request, 'account/rent_book.html', context)



@login_required
def rent_this_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if the book is available
    if book.status == 'Available' and book.copies > 0:
        # Reduce the number of copies by 1
        book.copies -= 1

        # If no more copies are left, mark the book as Unavailable
        if book.copies == 0:
            book.status = 'Unavailable'

        # Save the updated book status
        book.save()

        # Use the rental_days set by the admin to calculate the rental period
        rental_start_date = timezone.now().date()  # Set the current date
        rental_end_date = rental_start_date + timedelta(days=book.rental_days)  # Use the admin-defined rental period

        RentBook.objects.create(
            user=request.user,
            book=book,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            rental_start_date=rental_start_date,
            rental_end_date=rental_end_date
        )

        messages.success(request, f'You have successfully rented {book.name} for {book.rental_days} days.')
    else:
        messages.error(request, 'This book is already rented or no copies are available.')

    return redirect('book_details', book_id=book_id)

@login_required
def book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    context = {
        'book': book
    }
    return render(request, 'account/book_details.html', context)

def books_by_genre(request, genre):
    books = get_list_or_404(Book, genre=genre)
    return render(request, 'account/genre_books.html', {'genre': genre, 'books': books})
@login_required
def view_profile(request):
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)
    rented_books = RentBook.objects.filter(user=user)

    context = {
        'user': user,
        'profile': profile,
        'rented_books': rented_books,
    }

    return render(request, 'account/view_profile.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')



# Admin Login View
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check for predefined credentials
        if username == 'admin' and password == 'admin123':  # Change to your desired credentials
            # Create or get the admin user
            admin_user, created = User.objects.get_or_create(username=username)
            if created:  # If the user was created, set a password
                admin_user.set_password(password)
                admin_user.save()

            # Check if the admin user has a UserProfile, if not, create one
            if not hasattr(admin_user, 'userprofile'):
                UserProfile.objects.create(user=admin_user)

            # Log the user in
            login(request, admin_user)  # Directly log in the user
            return redirect('admin_dashboard')  # Redirect to the admin dashboard
        else:
            return render(request, 'account/admin_login.html', {'error': 'Invalid username or password.'})

    return render(request, 'account/admin_login.html')


# Main Dashboard View
def admin_dashboard(request):
    return render(request, 'account/admin_dashboard.html')

# Add Books
def add_to_collections(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
            return redirect('books_catalog')
        else:
            # Show the errors
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")
    else:
        form = BookForm()

    return render(request, 'account/add_book.html', {'form': form})

def search_authors(request):
    query = request.GET.get('query', '')
    authors = Author.objects.filter(name__icontains=query)
    results = [{'name': author.name} for author in authors]
    return JsonResponse(results, safe=False)
# Books Catalog
def books_catalog(request):
    # Fetch all books from the database
    books = Book.objects.all()
    return render(request, 'account/books_catalog.html', {'books': books})


def edit_book(request, id):  # Use 'id' instead of 'book_id'
    book = get_object_or_404(Book, id=id)  # Fetch the book by ID
    if request.method == 'POST':
        # Get the field to update and the new value
        field = request.POST.get('field')
        value = request.POST.get('value')

        # Update the selected field with the new value
        if field and value:
            setattr(book, field, value)
            book.save()
            messages.success(request, f"{field.capitalize()} updated successfully!")
            return redirect('books_catalog')
        else:
            messages.error(request, "Failed to update the book!")

    # Render the catalog with the editing form
    books = Book.objects.all()
    return render(request, 'account/books_catalog.html', {
        'books': books,
        'editing': True,  # Indicate that we're in editing mode
        'book_id': id  # Pass the ID of the book being edited
    })


def delete_book(request, id):  # Use 'id' instead of 'book_id'
    book = get_object_or_404(Book, id=id)  # Use primary key 'id'
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('books_catalog')

# User Records
def user_records(request):
    return HttpResponse("User Records Page")  # Redirect to book catalog when clicking User Record


# View for displaying overdue books
def overdue_books_view(request):
    # Get books where the rental end date has passed
    overdue_books = RentBook.objects.filter(rental_end_date__lt=timezone.now().date())

    # Calculate overdue days for each book
    for rent in overdue_books:
        rent.overdue_days = (timezone.now().date() - rent.rental_end_date).days

    return render(request, 'account/overduebook.html', {'overdue_books': overdue_books})

def borrowed_books(request):
    borrowed_books = RentBook.objects.all()  # Fetch all borrowed books
    return render(request, 'account/borrowed_books.html', {'borrowed_books': borrowed_books})

@login_required
def user_list_view(request):
    status = request.GET.get('status', 'all')

    # Filter based on subscription status
    if status == 'subscribed':
        users = UserProfile.objects.filter(is_subscribed=True)
    elif status == 'unsubscribed':
        users = UserProfile.objects.filter(is_subscribed=False)
    else:
        users = UserProfile.objects.all()

    return render(request, 'account/userdetails.html', {'users': users, 'status': status})



# Logout Functionality
def admin_logout(request):
    logout(request)
    return redirect('account/admin_login')  # Redirect to the login page after logout