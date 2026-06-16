class OrganizationError( Exception ):
    """Base class for organization-domain errors."""


class LastActiveOwnerError( OrganizationError ):
    """Raised when an operation would leave an organization with no active owner."""
