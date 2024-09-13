import datetime
import secrets
import threading
from typing import List, Optional
from uuid import UUID
import os
from dotenv import load_dotenv

from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from langflow.services.database.models.api_key import ApiKey, ApiKeyCreate, ApiKeyRead, UnmaskedApiKeyRead

load_dotenv()

def get_api_keys(session: Session, user_id: UUID) -> List[ApiKeyRead]:
    query: SelectOfScalar = select(ApiKey).where(ApiKey.user_id == user_id)
    api_keys = session.exec(query).all()
    return [ApiKeyRead.model_validate(api_key) for api_key in api_keys]


def get_api_keys_by_flow_id(session: Session, flow_id: UUID) -> List[ApiKeyRead]:
    query: SelectOfScalar = select(ApiKey).where(ApiKey.flow_id == flow_id)
    api_keys = session.exec(query).all()
    return [ApiKeyRead.model_validate(api_key) for api_key in api_keys]


def create_api_key(session: Session, api_key_create: ApiKeyCreate, user_id: UUID) -> UnmaskedApiKeyRead:
    # Generate a random API key with 32 bytes of randomness
    generated_api_key = f"sk-{secrets.token_urlsafe(32)}"
    expiration_hours = os.getenv("API_KEY_EXPIRATION_HOURS")

    api_key = ApiKey(
        api_key=generated_api_key,
        name=api_key_create.name,
        user_id=user_id,
        created_at=api_key_create.created_at or datetime.datetime.now(datetime.timezone.utc),
        flow_id=api_key_create.flow_id,
        expire_at=api_key_create.expire_at
        or (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=expiration_hours)),
    )

    session.add(api_key)
    session.commit()
    session.refresh(api_key)
    unmasked = UnmaskedApiKeyRead.model_validate(api_key, from_attributes=True)
    unmasked.api_key = generated_api_key
    return unmasked


def delete_api_key(session: Session, api_key_id: UUID) -> None:
    api_key = session.get(ApiKey, api_key_id)
    if api_key is None:
        raise ValueError("API Key not found")
    session.delete(api_key)
    session.commit()


def check_key(session: Session, api_key: str) -> Optional[ApiKey]:
    """Check if the API key is valid and not expired."""
    query: SelectOfScalar = select(ApiKey).where(ApiKey.api_key == api_key)
    api_key_object: Optional[ApiKey] = session.exec(query).first()
    if api_key_object is not None:
        # Check if the API key has expired
        if api_key_object.expire_at is not None and (
            api_key_object.expire_at <= datetime.datetime.now(datetime.timezone.utc)
        ):
            raise ValueError("API Key has expired")
        threading.Thread(
            target=update_total_uses,
            args=(
                session,
                api_key_object,
            ),
        ).start()
    return api_key_object


def update_total_uses(session, api_key: ApiKey):
    """Update the total uses and last used at."""
    # This is running in a separate thread to avoid slowing down the request
    # but session is not thread safe so we need to create a new session

    with Session(session.get_bind()) as new_session:
        new_api_key = new_session.get(ApiKey, api_key.id)
        if new_api_key is None:
            raise ValueError("API Key not found")
        new_api_key.total_uses += 1
        new_api_key.last_used_at = datetime.datetime.now(datetime.timezone.utc)
        new_session.add(new_api_key)
        new_session.commit()
    return new_api_key
