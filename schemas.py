import enum
from typing import Optional

import deps


class CardEventType(str, enum.Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"
    REJECTED = "REJECTED"  # carte inconnue
    GRANTED = "GRANTED"  # accès autorisé
    DENIED = "DENIED"  # accès refusé


class CardTypes(str, enum.Enum):
    MASTERCARD = "MASTERCARD"
    SIMPLECARD = "SIMPLECARD"


# locket shemas models
class AddLocket(deps.BaseModel):
    topic: Optional[str] = None
    label: Optional[str] = None
    user_id: Optional[str] = None


class DelLocket(deps.BaseModel):
    user_id: Optional[str] = None
    locket_id: Optional[str] = None


class UpdateLocket(deps.BaseModel):
    topic: Optional[str] = None
    label: Optional[str] = None
    user_id: Optional[str] = None


class GetLocket(deps.BaseModel):
    user_id: str


class AddCards(deps.BaseModel):
    cart_uid: Optional[str] = None
    card_type: Optional[str] = None
    card_name: Optional[str] = None
    user_id: Optional[str] = None


class DelCards(deps.BaseModel):
    user_id: Optional[str] = None
    card_id: Optional[str] = None


class UpdateCardStatus(deps.BaseModel):
    user_id: Optional[str] = None
    card_id: Optional[str] = None
    status: Optional[str] = None


# Card schemas models
class AddRfidCard(deps.BaseModel):
    user_id: Optional[str] = None
    locket_id: Optional[str] = None
    uid: Optional[str] = None
    label: Optional[str] = None
    types: CardTypes = CardTypes.SIMPLECARD
    status: Optional[bool] = False


class DeleteCard(deps.BaseModel):
    user_id: Optional[str] = None
    card_id: Optional[str] = None


class statusCard(deps.BaseModel):
    user_id: Optional[str] = None
    card_id: Optional[str] = None
    status: Optional[str] = None


class GetCard(deps.BaseModel):
    user_id: Optional[str] = None


# card event schemas models


class AddCartEvents(deps.BaseModel):
    user_id: Optional[str] = None
    uid: Optional[str] = None
    topic: Optional[str] = None
    event_type: Optional[str] = None
    message: Optional[str] = None


class GetEvents(deps.BaseModel):
    user_id: Optional[str] = None


class DeleteHistory(deps.BaseModel):
    user_id: Optional[str] = None
    cart_event_id: Optional[str] = None
