import uuid

from django.conf import settings
from django.db import models, transaction

from common.labeled_enum import LabeledEnumField
from common.models import TimestampedModel

from .enums import OrganizationRole
from .exceptions import LastActiveOwnerError
from .managers import OrganizationManager, OrganizationMemberManager


class Organization( TimestampedModel ):
    """A tenancy boundary: the unit that owns domain objects.

    Users gain access only indirectly, through an OrganizationMember. An
    organization may sit in a hierarchy via `parent`; the hierarchy is purely
    structural in this version (no behavioural inheritance).
    """

    objects = OrganizationManager()

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
    """A user's membership in an organization, carrying their role.

    The model guards one invariant: an organization must always retain at least
    one active owner. An operation that would drop the last active owner —
    deleting, demoting, or deactivating it — raises LastActiveOwnerError. The
    check runs under a row lock on the organization, so it is safe against
    concurrent owner changes. (Bulk queryset operations such as
    `QuerySet.update()`/`delete()` bypass these hooks and are not guarded.)
    """

    _LAST_OWNER_MESSAGE = 'An organization must always retain at least one active owner.'

    objects = OrganizationMemberManager()

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

    @property
    def is_active_owner(self):
        return self.is_active and self.organization_role == OrganizationRole.OWNER

    def save( self, *args, **kwargs ):
        # Only an update that strips active-owner status from a current active
        # owner can threaten the invariant; everything else saves directly.
        if self.pk is not None:
            previous = self.__class__.objects.filter( pk = self.pk ).first()
            if previous is not None and previous.is_active_owner and not self.is_active_owner:
                with transaction.atomic():
                    self._assert_another_active_owner_exists()
                    return super().save( *args, **kwargs )
        return super().save( *args, **kwargs )

    def delete( self, *args, **kwargs ):
        if self.is_active_owner:
            with transaction.atomic():
                self._assert_another_active_owner_exists()
                return super().delete( *args, **kwargs )
        return super().delete( *args, **kwargs )

    def _assert_another_active_owner_exists( self ):
        # Lock the organization row so concurrent owner changes serialize: two
        # simultaneous demotions cannot each observe the other as still active.
        Organization.objects.select_for_update().get( pk = self.organization_id )
        another_exists = self.__class__.objects.active_owners(
            self.organization_id
        ).exclude( pk = self.pk ).exists()
        if not another_exists:
            raise LastActiveOwnerError( self._LAST_OWNER_MESSAGE )
        return
