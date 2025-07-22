import deps

from ..models.locket import CardEvent, CardEventType
from ..schemas import AddCartEvents, DeleteHistory, GetCard


class OPTIONS:

    def __init__(self):
        super(OPTIONS, self).__init__()

    def for_refresh(self, locket: AddCartEvents):
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


class EventCard(OPTIONS):

    def __init__(self):
        super().__init__()
        self.db: deps.Session = deps.db

    def add(self, event: AddCartEvents):
        try:
            self.db.add(
                CardEvent(
                    event=AddCartEvents(
                        user_id=event.user_id,
                        uid=event.uid,
                        event_type=(
                            event.event_type
                            if event.event_type
                            in ["ADD", "REMOVE", "REJECTED", "GRANTED", "DENIED"]
                            else CardEventType.DEFAULT
                        ),
                        message=event.message,
                        topic=event.topic,
                    )
                )
            )
            return self._extracted_from_update_4(event)
        except Exception:
            return self.rollback()

    def get_by_user_id(self, event: GetCard):

        try:
            if responses := (
                self.db.query(CardEvent)
                .filter(CardEvent.user_id == event.user_id)
                .all()
            ):
                events = [i.responseModel() for i in responses]
                return events
            else:
                return []

        except Exception:
            return []

    def delete_by_month(self, month: int):
        try:
            events_to_delete = (
                self.db.query(CardEvent)
                .filter(CardEvent.created_at.month == month)
                .all()
            )
            for event in events_to_delete:
                self.db.delete(event)
            self.db.commit()
            return True
        except Exception:
            return self.rollback()

    def get_history(self, user_id: str):
        try:
            return [
                i.responseModel()
                for i in self.db.query(CardEvent)
                .filter(CardEvent.user_id == user_id)
                .order_by(CardEvent.event_date.desc())
                .all()
            ]

        except Exception:
            return []

    def delete_by_id(self, event: DeleteHistory):
        try:
            if (
                event := self.db.query(CardEvent)
                .filter(CardEvent.id == event.cart_event_id)
                .filter(CardEvent.user_id == event.user_id)
            ):
                event.delete()
                self.db.commit()
                return True
            else:
                return False
        except Exception:
            return self.rollback()
