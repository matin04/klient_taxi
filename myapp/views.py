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



