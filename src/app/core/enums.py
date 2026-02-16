import enum

class CaseInsensitiveValueEnum(enum.Enum):
    """Mixin that enables case-insensitive lookup by enum value."""

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            return cls._value2member_map_.get(value.lower())
        return None
    
class AccountRole(CaseInsensitiveValueEnum):
    """Roles for account members"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class AccountType(CaseInsensitiveValueEnum):
    """Account type classifications"""
    CONSUMER = "consumer"
    COMMUNITY = "community"
    NGO = "ngo"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"


class IntegrationType(CaseInsensitiveValueEnum):
    """Types of integrations available - matches integration_types.code"""
    PAYMENT = "payment"
    EMAIL = "email"
    SMS = "sms"
    CALENDAR = "calendar"
    VIDEO = "video"
    ANALYTICS = "analytics"
    SOCIAL = "social"
    CRM = "crm"
    TICKETING = "ticketing"
    STREAMING = "streaming"
    STORAGE = "storage"
    MARKETING = "marketing"


class IntegrationProvider(CaseInsensitiveValueEnum):
    """Integration providers - matches integration_providers.code"""
    STRIPE = "STRIPE"
    PAYPAL = "PAYPAL"
    SENDGRID = "SENDGRID"
    TWILIO = "TWILIO"
    ZOOM = "ZOOM"
    GOOGLE = "GOOGLE"
    MICROSOFT = "MICROSOFT"


class NotificationType(CaseInsensitiveValueEnum):
    """Notification types - matches notification_types.code"""
    EVENT_REMINDER = "EVENT_REMINDER"
    EVENT_UPDATE = "EVENT_UPDATE"
    EVENT_CANCELLED = "EVENT_CANCELLED"
    NEW_MESSAGE = "NEW_MESSAGE"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    ORDER_REFUNDED = "ORDER_REFUNDED"
    ACCOUNT_INVITE = "ACCOUNT_INVITE"
    FOLLOWER = "FOLLOWER"
    COMMENT = "COMMENT"
    MENTION = "MENTION"


class SubscriptionTier(CaseInsensitiveValueEnum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
