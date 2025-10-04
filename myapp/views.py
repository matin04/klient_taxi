from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from .models import *
from .serializer import RegisterSerializer, UserSerializer, TripSerializer, BookingSerializer
from .premission import IsAdmin,IsTaxiOwnerOrAdmin, IsBookingOwnerOrAdmin
from .filters import TripFilter
from .paginator import StandardResultsSetPagination
from django.db.models import Sum
from rest_framework.views import APIView


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]



class TripListCreateView(generics.ListCreateAPIView):
    queryset = Trip.objects.all().order_by('date')
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TripFilter
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        if self.request.user.role not in ['taxi', 'admin']:
            raise ValidationError("Only Taxi or Admin can create trips.")
        serializer.save(taxi=self.request.user)



class TripRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsTaxiOwnerOrAdmin]
    



class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Booking.objects.all()
        elif user.role == 'user':
            return Booking.objects.filter(user=user)
        elif user.role == 'taxi':
            return Booking.objects.filter(trip__taxi=user)
        
        
    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['user', 'admin']:
            raise ValidationError("Только пользователи могут бронировать поездки.")
        trip = serializer.validated_data['trip']
        seat_requested = serializer.validated_data['seats_booked']
        
        booked_seats = trip.booking_set.aggregate(Sum('seats_booked'))['seats_booked__sum'] or 0
        available_seats = trip.seats - booked_seats
        if seat_requested > available_seats:
            raise ValidationError(f"Недостаточно свободных мест. Доступно мест: {available_seats}")
        serializer.save(user=user)
        profile = self.request.user.profile
        profile.total_bookings += 1
        profile.save()


class BookingRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBookingOwnerOrAdmin]
    


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail":"Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role != 'admin' and request.user != booking.user:
            return Response({'error': 'У вас нет разрешения отменить это бронирование..'}, status=status.HTTP_403_FORBIDDEN)
        booking.delete()
        return Response({"detail":"Booking cancelled"}, status=status.HTTP_200_OK)
    
    

