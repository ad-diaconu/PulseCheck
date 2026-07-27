import backend.app.core.auth as auth
from backend.app.db.database import (
    Base,
    SessionLocal,
    engine,
)
from backend.app.models import User, UserRole


def seed_test_user():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        test_email = "test@pulsecheck.com"
        exists = db.query(User).filter(User.email == test_email).first()

        if not exists:
            hashed_password = auth.get_password_hash("ParolaTest123!")
            user = User(
                email=test_email,
                hashed_password=hashed_password,
                role=UserRole.admin,
            )
            db.add(user)
            db.commit()
            print(f"Test user created successfully: {test_email}")
        else:
            print("Test user already exists in database.")
    except Exception as e:
        db.rollback()
        print(f"Seeding error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_user()
