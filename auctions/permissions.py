from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin has full access
        if request.user.role == 'admin':
            return True
        
        # Owner has access to their own auctions
        return obj.owner == request.user