from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from .models import *
from .serializer import RegisterSerializer, UserSerializer, TripSerializer, BookingSerializer
from .premission import IsAdmin,IsTaxiOwnerOrAdmin, IsBookingOwnerOrAdmin
from .filter import TripFilter
from .paginator import StandardResultsSetPagination
from django.db.models import Sum

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LogoutView(generics.ListAPIView):
    permission_classes = (IsAuthenticated)
    
    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"ddetail":"Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail":"Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]



class TripListCreateView(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    firterset_class = TripFilter
    pagination_class = StandardResultsSetPagination
    
    def perform_crete(self, serializer):
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
        else:
            return Booking.objects.none()
        
        
    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['user', 'admin']:
            raise ValidationError("Только пользователи могут бронировать поездки.")
        trip = serializer.validated_data['trip']
        seat_requested = serializer.validated_data['seats_booked']
        
        booked_seats = trip.booking_set.aggregate(Sum('seats_booked'))['total'] or 0
        available_seats = trip.seats - booked_seats
        if seat_requested > available_seats:
            raise ValidationError(f"Недостаточно свободных мест. Доступно мест: {available_seats}")
        serializer.save(user=user)
        
        

class BookingRetraiveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBookingOwnerOrAdmin]
    


class CancelBookingView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail":"Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != 'admin' and request.user != booking.user:
            return Response({'error': 'У вас нет разрешения отменить это бронирование..'}, status=status.HTTP_403_FORBIDDEN)
        booking.delete()
        return Response({"detail":"Booking cancelled"}, status=status.HTTP_209_OK)
    
    

