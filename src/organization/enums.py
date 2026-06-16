"""Enumerations for the optional organization (multi-tenancy) app."""
from common.labeled_enum import LabeledEnum


class OrganizationRole( LabeledEnum ):
    """A member's role within an organization.

    The role is a *mechanism* only: it names a tier of membership. Mapping a role
    to concrete capabilities is the consuming application's responsibility.
    """

    OWNER   = ( 'Owner'  , 'Full control of the organization, including membership and ownership.' )
    ADMIN   = ( 'Admin'  , 'Elevated privileges short of ownership.' )
    MEMBER  = ( 'Member' , 'Regular member with no special privileges.' )

    @classmethod
    def default(cls):
        return cls.MEMBER
