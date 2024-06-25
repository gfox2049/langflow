import warnings
from typing import List, Optional
from uuid import UUID

from loguru import logger
from sqlalchemy import delete
from sqlmodel import Session, col, select

from langflow.schema.message import Message
from langflow.services.database.models.message.model import MessageTable
from langflow.services.deps import session_scope


def get_messages(
    sender: Optional[str] = None,
    sender_name: Optional[str] = None,
    session_id: Optional[str] = None,
    order_by: Optional[str] = "timestamp",
    order: Optional[str] = "DESC",
    flow_id: Optional[UUID] = None,
    limit: Optional[int] = None,
):
    """
    Retrieves messages from the monitor service based on the provided filters.

    Args:
        sender (Optional[str]): The sender of the messages (e.g., "Machine" or "User")
        sender_name (Optional[str]): The name of the sender.
        session_id (Optional[str]): The session ID associated with the messages.
        order_by (Optional[str]): The field to order the messages by. Defaults to "timestamp".
        limit (Optional[int]): The maximum number of messages to retrieve.

    Returns:
        List[Data]: A list of Data objects representing the retrieved messages.
    """
    messages_read: list[Message] = []
    with session_scope() as session:
        stmt = select(MessageTable)
        if sender:
            stmt = stmt.where(MessageTable.sender == sender)
        if sender_name:
            stmt = stmt.where(MessageTable.sender_name == sender_name)
        if session_id:
            stmt = stmt.where(MessageTable.session_id == session_id)
        if flow_id:
            stmt = stmt.where(MessageTable.flow_id == flow_id)
        if order_by:
            if order == "DESC":
                col = getattr(MessageTable, order_by).desc()
            else:
                col = getattr(MessageTable, order_by).asc()
            stmt = stmt.order_by(col)
        if limit:
            stmt = stmt.limit(limit)
        messages = session.exec(stmt)
        messages_read = [Message(**d.model_dump()) for d in messages]

    return messages_read


def add_messages(messages: Message | list[Message], flow_id: Optional[str] = None):
    """
    Add a message to the monitor service.
    """
    try:
        if not isinstance(messages, list):
            messages = [messages]

        if not all(isinstance(message, Message) for message in messages):
            types = ", ".join([str(type(message)) for message in messages])
            raise ValueError(f"The messages must be instances of Message. Found: {types}")

        messages_models: list[MessageTable] = []
        for msg in messages:
            messages_models.append(MessageTable.from_message(msg, flow_id=flow_id))
        with session_scope() as session:
            messages_models = add_messagetables(messages_models, session)
        return messages_models
    except Exception as e:
        logger.exception(e)
        raise e


def add_messagetables(messages: list[MessageTable], session: Session):
    for message in messages:
        try:
            session.add(message)
            session.commit()
            session.refresh(message)
        except Exception as e:
            logger.exception(e)
            raise e
    return [Message(**message.model_dump()) for message in messages]


def delete_messages(session_id: str):
    """
    Delete messages from the monitor service based on the provided session ID.

    Args:
        session_id (str): The session ID associated with the messages to delete.
    """
    with session_scope() as session:
        session.exec(
            delete(MessageTable)
            .where(col(MessageTable.session_id) == session_id)
            .execution_options(synchronize_session="fetch")
        )
        session.commit()


def store_message(
    message: Message,
    flow_id: Optional[str] = None,
) -> List[Message]:
    """
    Stores a message in the memory.

    Args:
        message (Message): The message to store.
        flow_id (Optional[str]): The flow ID associated with the message. When running from the CustomComponent you can access this using `self.graph.flow_id`.

    Returns:
        List[Message]: A list of data containing the stored message.

    Raises:
        ValueError: If any of the required parameters (session_id, sender, sender_name) is not provided.
    """
    if not message:
        warnings.warn("No message provided.")
        return []

    if not message.session_id or not message.sender or not message.sender_name:
        raise ValueError("All of session_id, sender, and sender_name must be provided.")

    return add_messages([message], flow_id=flow_id)
