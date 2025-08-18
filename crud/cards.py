import deps

from ..models.locket import Locket, RFIDCards
from ..schemas import (
    AddCartEvents,
    AddRfidCard,
    CardEventType,
    DeleteCard,
    GetCard,
    UpdateCardStatus,
)
from .events import EventCard


class OPTIONS:

    def __init__(self):
        super(OPTIONS, self).__init__()
        self.EVENTCRUD = EventCard()

    def for_refresh(self, locket: AddRfidCard):
        try:
            self.db.refresh(locket)
            return True
        except Exception:
            self.rollback()

    def rollback(self):
        self.db.rollback()
        return False

    def _extracted_from_update_4(self, locket):
        return self._extracted_from__extracted_from_update_4_15(locket)

    # TODO Rename this here and in `update` and `_extracted_from_update_4`
    def _extracted_from__extracted_from_update_4_15(self, arg0):
        self.db.commit()
        self.for_refresh(arg0)
        return True


class CardCruds(OPTIONS):
    def __init__(self):
        super().__init__()
        self.db = deps.Session = deps.db

    def get(self, card: GetCard):
        response = [
            {
                "id": i.id,
                "rfidId": i.locket_id,
                "type": i.types,
                "nom": i.label,
                "actif": i.status,
            }
            for i in (
                self.db.query(RFIDCards).filter(RFIDCards.user_id == card.user_id).all()
            )
        ]

        return response if response else None

    def add(self, locket: AddRfidCard):
        try:
            self.db.add(
                RFIDCards(
                    AddRfidCard(
                        uid=locket.uid,
                        locket_id=locket.locket_id,
                        user_id=locket.user_id,
                        label=locket.label if locket.label else "unknown",
                        types=locket.types.value if locket.types else "SIMPLECARD",
                        status=True if locket.status else False,
                    )
                )
            )
            self.EVENTCRUD.add(
                event=AddCartEvents(
                    user_id=locket.user_id,
                    uid=locket.uid,
                    topic=locket.label,
                    event_type=CardEventType.ADD,
                )
            )
            return self._extracted_from_update_4(locket)
        except Exception as e:
            print(f"Error adding card: {e}")
            self.rollback()

    def remove(self, carts: DeleteCard):
        response = (
            self.db.query(RFIDCards)
            .filter(RFIDCards.id == carts.card_id)
            .filter(RFIDCards.user_id == carts.user_id)
        )
        if response.first().types == "MASTERCARD":
            result = (True, [response.first().uid, response.first().locket_id])

            self.db.commit()
            self.EVENTCRUD.add(
                event=AddCartEvents(
                    user_id=carts.user_id,
                    uid=carts.card_id,
                    topic=response.first().label,
                    event_type=CardEventType.REMOVE,
                    message="Removing message.",
                )
            )
            response.delete()
            return result
        else:
            response.delete()
            self.db.commit()
            self.EVENTCRUD.add(
                event=AddCartEvents(
                    user_id=carts.user_id,
                    uid=carts.card_id,
                    topic=response.first().label,
                    event_type=CardEventType.REMOVE,
                    message="Removing message.",
                )
            )
            return (True, None)

    def remove_by_id(self, idLocket: str):
        if response := (
            self.db.query(RFIDCards).filter(RFIDCards.locket_id == idLocket)
        ):
            self.EVENTCRUD.add(
                event=AddCartEvents(
                    user_id=response.first().user_id,
                    uid=response.first().uid,
                    topic="multi-delete",
                    message=str([i for i in response.first().label]),
                    event_type=CardEventType.REMOVE,
                )
            )
            return True
        else:
            return False

    def get_user_acess(self, user_id: str, card_uuid: str) -> bool:
        if response := (
            self.db.query(RFIDCards)
            .filter(RFIDCards.user_id == user_id)
            .filter(RFIDCards.uid == card_uuid)
            .first()
        ):
            if response.status:
                self.EVENTCRUD.add(
                    event=AddCartEvents(
                        user_id=response.user_id,
                        uid=response.uid,
                        topic=response.label,
                        event_type=CardEventType.GRANTED,
                        message=f"user {response.user_id} as {CardEventType.GRANTED}",
                    )
                )
                return True
            else:
                self.EVENTCRUD.add(
                    event=AddCartEvents(
                        user_id=response.user_id,
                        uid=card_uuid,
                        topic=response.label,
                        message="status desactivate",
                        event_type=CardEventType.REJECTED,
                    )
                )
                return False

        self.EVENTCRUD.add(
            event=AddCartEvents(
                user_id=user_id,
                uid=card_uuid,
                topic="Uknow card",
                event_type=CardEventType.DENIED,
                message=f"user {user_id} as {CardEventType.DENIED}",
            )
        )
        return False

    def update_status(self, status: UpdateCardStatus):
        try:
            response = (
                self.db.query(RFIDCards)
                .filter(RFIDCards.id == status.card_id)
                .filter(RFIDCards.user_id == status.user_id)
                .first()
            )
            if response:
                response.status = True if status.status == "True" else False
                self.db.commit()
                if response.types == "MASTERCARD":
                    locket = (
                        self.db.query(Locket)
                        .filter(Locket.id == response.locket_id)
                        .first()
                    )
                    if locket:
                        return (True, locket.topic, response.uid)
            return (False, None, None)
        except Exception as e:
            print(f"Error updating card status: {e}")
            self.rollback()
            return (False, None, None)
