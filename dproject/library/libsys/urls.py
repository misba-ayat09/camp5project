from django.urls import path
from django.views.generic import TemplateView
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('author/', views.author_page, name='author'),
    path('search-authors/', views.search_authors, name='search_authors'),
    path('genre/<str:genre>/', views.books_by_genre, name='books_by_genre'),
    path('membership/', views.membership_page, name='membership'),
    path('activate_plan/<str:plan_duration>/', views.activate_plan, name='activate_plan'),
    path('rent/', views.rent_book, name='rent_book'),
    path('rent/<int:book_id>/', views.rent_this_book, name='rent_this_book'),
    path('book/<int:book_id>/', views.book_details, name='book_details'),
    path('payment/', views.payment_view, name='payment'),
    path('customer/', views.customer, name='customer'),
    path('profile/', views.view_profile, name='view_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-to-collections/', views.add_to_collections, name='add_to_collections'),
    path('users/', views.user_list_view, name='user_list'),
    path('books-catalog/', views.books_catalog, name='books_catalog'),
    path('edit/<int:id>/', views.edit_book, name='edit_book'),  # Changed to 'id'
    path('delete/<int:id>/', views.delete_book, name='delete_book'),  # Changed to 'id'
    path('overdue-books/', views.overdue_books_view, name='overdue_books'),
    path('borrowed_books/', views.borrowed_books, name='borrowed_books'),
    path('logout/', views.admin_logout, name='admin_logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)