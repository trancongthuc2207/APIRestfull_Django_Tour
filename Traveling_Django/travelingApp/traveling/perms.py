from rest_framework import permissions


## Staff Action on User
class CanGetUser(permissions.IsAuthenticated):
    def has_permission(self, request, user):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False


class TicketOwnerUser(permissions.IsAuthenticated):
    def has_permission(self, request, ticket):
        if request.user == ticket.user or request.user.is_superuser or request.user.is_staff:
            return True
        return False


class BillOwnerUser(permissions.IsAuthenticated):
    def has_permission(self, request, ticket):
        if request.user == ticket.user or request.user.is_superuser or request.user.is_staff:
            return True
        return False


class CommentOwnerUser(permissions.IsAuthenticated):
    def has_permission(self, request, comment):
        if request.user == comment.user or request.user.is_superuser or request.user.is_staff:
            return True
        return False


class CanCRUD_Tour(permissions.IsAuthenticated):
    def has_permission(self, request, user):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False
