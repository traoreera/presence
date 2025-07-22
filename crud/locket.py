import deps

from ..models.locket import Locket
from ..schemas import AddLocket, DelLocket, GetLocket, UpdateLocket


class OPTIONS:

    def __init__(self):
        super(OPTIONS, self).__init__()

    def for_refresh(self, locket: AddLocket):
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


class LocketCruds(OPTIONS):
    def __init__(self):
        super().__init__()
        self.db = deps.Session = deps.db

    def get(self, locket: GetLocket):
        response = [
            {
                "topic": i.topic,
                "id": i.id,
                "nom": i.label,
                "actif": i.actif,
                "niveauBatterie": i.niveauBatterie,
            }
            for i in (
                self.db.query(Locket).filter(Locket.user_id == locket.user_id).all()
            )
        ]

        return response if response else None

    def get_by_id(self, locket_id: str):
        response = self.db.query(Locket).filter(Locket.id == locket_id).first()
        return response.responseModel() if response else None

    def add(self, locket: AddLocket):
        try:
            self.db.add(Locket(locket=locket))
            return self._extracted_from_update_4(locket)
        except Exception as e:
            print(f"Error adding locket: {e}")
            self.rollback()

    def remove(self, locket: DelLocket):

        if (
            self.db.query(Locket)
            .filter(Locket.id == locket.locket_id)
            .filter(Locket.user_id == locket.user_id)
            .delete()
        ):
            self.db.commit()
            return True
        else:
            self.rollback()
            return False

    def update(self, locket: UpdateLocket):

        if (
            response := self.db.query(Locket)
            .filter(Locket.user_id == locket.user_id)
            .filter(Locket.topic == locket.topic)
            .first()
        ):
            response.topic = locket.topic
            response.label = locket.label
            return self._extracted_from__extracted_from_update_4_15(response)
