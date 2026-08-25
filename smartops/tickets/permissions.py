from rest_framework.permissions import BasePermission


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