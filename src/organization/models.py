import uuid

from django.conf import settings
from django.db import models

from common.labeled_enum import LabeledEnumField
from common.models import TimestampedModel

from .enums import OrganizationRole


class Organization( TimestampedModel ):
    """A tenancy boundary: the unit that owns domain objects.

    Users gain access only indirectly, through an OrganizationMember. An
    organization may sit in a hierarchy via `parent`; the hierarchy is purely
    structural in this version (no behavioural inheritance).
    """

    uuid = models.UUIDField(
        'UUID',
        default = uuid.uuid4,
        unique = True,
        null = False,
        editable = False,
    )
    name = models.CharField(
        'Name',
        max_length = 64,
        null = False,
        blank = False,
    )
    parent = models.ForeignKey(
        'self',
        verbose_name = 'Parent',
        related_name = 'children',
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
    )

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return self.name


class OrganizationMember( TimestampedModel ):
    """A user's membership in an organization, carrying their role."""

    organization = models.ForeignKey(
        Organization,
        verbose_name = 'Organization',
        related_name = 'members',
        on_delete = models.CASCADE,
        null = False,
        blank = False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name = 'User',
        related_name = 'organization_members',
        on_delete = models.CASCADE,
        null = False,
        blank = False,
    )
    organization_role = LabeledEnumField(
        OrganizationRole,
        verbose_name = 'Role',
    )
    is_active = models.BooleanField(
        'Is Active',
        default = True,
    )

    class Meta:
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
        constraints = [
            models.UniqueConstraint(
                fields = [ 'organization', 'user' ],
                name = 'unique_organization_member',
            ),
        ]

    def __str__(self):
        return f'{self.user} @ {self.organization} ({self.organization_role.label})'
