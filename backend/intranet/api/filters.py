from rest_framework import filters

from intranet import models, exceptions


class IsEmployeeFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(employee=request.user)


class InEmployeesFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(employees=request.user)


class YearFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        year = request.QUERY_PARAMS.get('year', None)
        if year:
            return queryset.filter(year__id=year)
        return queryset


class PartTypeFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        part_type = request.QUERY_PARAMS.get("type", "all")
        if part_type not in ["all", "accepted", "rejected", "sent", "pending"]:
            raise exceptions.InvalidParamError("Invalid type")

        if part_type == "accepted":
            return queryset.filter(state=models.STATE_ACCEPTED)
        elif part_type == "rejected":
            return queryset.filter(state=models.STATE_REJECTED)
        elif part_type == "sent":
            return queryset.filter(state=models.STATE_SENT)
        elif part_type == "pending":
            return queryset.filter(state=models.STATE_CREATED)
        return queryset


class ProjectTypeFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        project_type = request.QUERY_PARAMS.get("type", "active")
        if project_type not in ["all", "active", "inactive"]:
            raise exceptions.InvalidParamError("Invalid type")

        if project_type == "active":
            return queryset.filter(active=True)
        elif project_type == "inactive":
            return queryset.filter(active=False)
        return queryset