import enum

import deps

from ..schemas import AddCartEvents, AddLocket, AddRfidCard


class CardEventType(str, enum.Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"
    REJECTED = "REJECTED"  # carte inconnue
    GRANTED = "GRANTED"  # accès autorisé
    DENIED = "DENIED"  # accès refusé
    DEFAULT = "UNKNOW"


class CardTypes(str, enum.Enum):
    MASTERCARD = "MASTERCARD"
    SIMPLECARD = "SIMPLECARD"


class Locket(deps.Base):
    __tablename__ = "presenceCarte"
    __table_args__ = (deps.UniqueConstraint("user_id", "topic", name="uq_user_topic"),)
    __table_args__ = (deps.UniqueConstraint("user_id", "label", name="uq_user_label"),)

    id = deps.Column(
        deps.String,
        primary_key=True,
    )
    user_id = deps.Column(
        deps.String, deps.ForeignKey("users.id"), nullable=False, index=True
    )
    topic = deps.Column(deps.String, nullable=False)
    label = deps.Column(deps.String, nullable=True)
    actif = deps.Column(deps.Boolean, default=False)
    niveauBatterie = deps.Column(deps.Integer, default=100)
    created_at = deps.Column(deps.DateTime, server_default=deps.func.now())
    last_update = deps.Column(
        deps.DateTime, server_default=deps.func.now(), onupdate=deps.func.now()
    )

    def __init__(
        self,
        locket: AddLocket,
    ):
        self.id = deps.make_ids()
        self.topic = locket.topic
        self.label = locket.label
        self.user_id = locket.user_id

    def responseModel(
        self,
    ):
        return {
            "topic": self.topic,
            "id": self.id,
            "nom": self.label,
            "actif": self.actif,
            "niveauBatterie": self.niveauBatterie,
        }


class RFIDCards(deps.Base):
    __tablename__ = "users_cartes"
    __table_args__ = (deps.UniqueConstraint("user_id", "uid", name="uq_user_uid"),)

    id = deps.Column(
        deps.String,
        primary_key=True,
    )
    user_id = deps.Column(
        deps.String, deps.ForeignKey("users.id"), nullable=False, index=True
    )
    locket_id = deps.Column(
        deps.String, deps.ForeignKey("presenceCarte.id"), nullable=False, index=True
    )
    uid = deps.Column(deps.String, nullable=False)  # UID de la carte RFID
    label = deps.Column(deps.String, nullable=True)
    types = deps.Column(
        deps.Enum(CardTypes), nullable=False, default=CardTypes.SIMPLECARD
    )
    status = deps.Column(deps.Boolean, default=False)
    created_at = deps.Column(deps.DateTime, server_default=deps.func.now())

    def __init__(self, locket: AddRfidCard):
        self.uid = locket.uid
        self.locket_id = locket.locket_id
        self.user_id = locket.user_id
        self.label = locket.label if locket.label else "unknown"
        self.types = locket.types.value if locket.types else CardTypes.SIMPLECARD.value
        self.status = True if locket.status else False
        self.id = deps.make_ids()

    def responseModel(
        self,
    ):
        return {
            "id": self.id,
            "rfidId": self.locket_id,
            "type": self.types,
            "nom": self.label,
            "status": self.status,
        }


class CardEvent(deps.Base):
    __tablename__ = "user_cate_event"
    id = deps.Column(deps.String, primary_key=True)
    uid = deps.Column(deps.String, nullable=False)  # UID scanné (même si non autorisé)
    user_id = deps.Column(deps.String, deps.ForeignKey("users.id"), nullable=True)
    topic = deps.Column(deps.String, nullable=True)
    event_type = deps.Column(
        deps.Enum(CardEventType), nullable=False, default=CardEventType.DEFAULT
    )
    message = deps.Column(deps.Text, nullable=True)

    event_date = deps.Column(
        deps.DateTime, server_default=deps.func.now(), default=deps.func.now()
    )

    def __init__(self, event: AddCartEvents):

        self.id = deps.make_ids()
        self.uid = event.uid
        self.user_id = event.user_id
        self.topic = event.topic
        self.event_type = event.event_type
        self.message = event.message

    def responseModel(
        self,
    ):

        return {
            "id": self.id,
            "label": self.topic,
            "event": self.event_type,
            "date": self.event_date,
        }
