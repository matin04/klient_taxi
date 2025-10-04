from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, LogoutView, UserListView, UserRetrieveUpdateDestroyView,
    TripListCreateView, TripRetrieveUpdateDestroyView,
    BookingListCreateView, BookingRetraiveDestroyView,
    CancelBookingView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view()),
    path('trips/', TripListCreateView.as_view()),
    path('trips/<int:pk>/', TripRetrieveUpdateDestroyView.as_view()),
    path('bookings/', BookingListCreateView.as_view()),
    path('bookings/<int:pk>/', BookingRetraiveDestroyView.as_view()),
    path('bookings/cancel/<int:pk>/', CancelBookingView.as_view()),
]
