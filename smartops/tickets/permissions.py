from rest_framework.permissions import BasePermission


<<<<<<< HEAD
class IsTicketOwnerOrStaff(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        user = request.user

        if user.is_staff:
            return True

        if obj.created_by == user:
            return True

        if obj.assigned_to == user:
            return True

        return False
=======
class IsAdmin(BasePermission):
    """
    Only administrators can perform this action.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsAgent(BasePermission):
    """
    Agents and administrators can perform this action.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["ADMIN", "AGENT"]
        )


class IsRequester(BasePermission):
    """
    Requesters can access their own operations.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "REQUESTER"
        )


class IsAdminOrAgent(BasePermission):
    """
    Admins and agents.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["ADMIN", "AGENT"]
        )
>>>>>>> 6472197e00068fd588ab2f80bfc613e308479f14
