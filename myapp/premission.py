from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsTaxiOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or (request.user.role == 'taxi' and obj.taxi == request.user)

class IsBookingOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj.user == request.user
