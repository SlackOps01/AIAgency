from enum import Enum

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


SUBSCRIPTION_PRICING = {
    SubscriptionTier.FREE: 0,
    SubscriptionTier.PRO: 10_000,
    SubscriptionTier.ENTERPRISE: 20_000,
}


