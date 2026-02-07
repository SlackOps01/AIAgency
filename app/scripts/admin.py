from app.core.database import SessionLocal
from app.scripts.hashing import hash_password
from app.models.users import User
from app.enums.users import UserRole
from app.enums.subscription import SubscriptionTier
from app.core.config import CONFIG
from sqlalchemy.exc import IntegrityError
from app.core.logging import logger

def create_admin():
    db = SessionLocal()
    try:
        admin = User(
            email=CONFIG.ADMIN_EMAIL,
            hashed_password=hash_password(CONFIG.ADMIN_PASSWORD),
            full_name="Admin",
            username=CONFIG.ADMIN_USERNAME,
            role=UserRole.ADMIN,
            is_active=True,
            subscription_tier=SubscriptionTier.ENTERPRISE,
        )
        db.add(admin)
        db.commit()
        logger.info("Admin created successfully")
    except IntegrityError:
        logger.info("Admin already exists")
    finally:
        db.close()


