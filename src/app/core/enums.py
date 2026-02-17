import enum

class CaseInsensitiveValueEnum(enum.Enum):
    """Mixin that enables case-insensitive lookup by enum value."""

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            return cls._value2member_map_.get(value.lower())
        return None


class AttendeeStatus(CaseInsensitiveValueEnum):
    """Attendee RSVP status"""
    INTERESTED = "interested"
    GOING = "going"
    NOT_GOING = "not_going"
    ATTENDED = "attended"


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


class OrderStatus(CaseInsensitiveValueEnum):
    """Order status types"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"


class PaymentMethod(CaseInsensitiveValueEnum):
    """Payment method types"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class SubscriptionTier(CaseInsensitiveValueEnum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
