from django.contrib.auth import get_user_model
from django.db import models, transaction

from .enums import OrganizationRole


class OrganizationManager( models.Manager ):

    @transaction.atomic
    def create_for_owner( self, user, name ):
        """Create an organization named `name`, owned by `user` as an active
        OWNER.

        Self-contained: the organization and its owner membership are created in
        one transaction, so a partial failure can never leave an ownerless
        organization.
        """
        organization = self.create( name = name )
        organization.members.create(
            user = user,
            organization_role = OrganizationRole.OWNER,
        )
        return organization

    @transaction.atomic
    def create_for_email( self, email, name ):
        """Create a passwordless user for `email` and an organization named
        `name` that they own.

        The user authenticates via magic link (no usable password). The whole
        operation is atomic.
        """
        user = get_user_model().objects.create_user( email = email )
        return self.create_for_owner( user, name )


class OrganizationMemberManager( models.Manager ):

    def for_user( self, user ):
        """Active memberships for `user` (the organizations they can access)."""
        return self.filter( user = user, is_active = True )

    def active_owners( self, organization ):
        """Active OWNER memberships of `organization`."""
        return self.filter(
            organization = organization,
            organization_role = OrganizationRole.OWNER,
            is_active = True,
        )
