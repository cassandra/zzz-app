from django.contrib import admin

from .models import Organization, OrganizationMember


@admin.register( Organization )
class OrganizationAdmin( admin.ModelAdmin ):
    show_full_result_count = False

    list_display = (
        'name',
        'uuid',
        'parent',
        'created_datetime',
    )
    search_fields = (
        'name',
        'uuid',
    )
    readonly_fields = (
        'uuid',
    )


@admin.register( OrganizationMember )
class OrganizationMemberAdmin( admin.ModelAdmin ):
    show_full_result_count = False

    list_display = (
        'organization',
        'user',
        'organization_role',
        'is_active',
        'created_datetime',
    )
    list_filter = (
        'is_active',
    )
    search_fields = (
        'organization__name',
        'user__email',
    )
