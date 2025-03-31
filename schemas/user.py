from pydantic import BaseModel, Field
from faker import Faker
from typing import Optional, Dict, Any

fake = Faker()

class BaseUser(BaseModel):
    class ConfigDict:
        extra = "forbid"  # Запрет лишних полей

class PublicUserSchema(BaseUser):
    name: str = Field(default_factory=fake.name)
    email: str = Field(default_factory=fake.email)
    password: str = Field(default_factory=lambda: fake.password(length=12))

class PremiumUserSchema(PublicUserSchema):
    subscription_id: str = Field(default_factory=fake.uuid4)
    credit_card: Optional[str] = Field(default_factory=fake.credit_card_number)

SCHEMAS = {
    "/api/users": PublicUserSchema,
    "premium": PremiumUserSchema
}
