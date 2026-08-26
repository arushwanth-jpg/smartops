from rest_framework.permissions import BasePermission


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