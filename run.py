from fasthtml.common import APIRouter, Request

from . import schemas
from .models import locket  # noqa: F401
from .page.pages import Home


class OPTIONS:
    from .crud.cards import CardCruds
    from .crud.events import EventCard
    from .crud.locket import LocketCruds
    from .task.locket import MqCmd, clientMq

    CRUD: LocketCruds = LocketCruds()
    CARD: CardCruds = CardCruds()
    HOME: Home = Home()
    HISTORY = EventCard()
    MQCMD = MqCmd


PLUGIN_INFO = {
    "name": "Presence",
    "version": "1.0.0",
    "author": "traore Eliezer",
    "Api_prefix": "/app/presence",
    "tag_for_identified": ["Plugin", "Presence"],
    "trigger": 2,
}

router = APIRouter(
    prefix=PLUGIN_INFO["Api_prefix"],
)


class PresenceTpeRoute:

    def __init__(self):
        pass

    @router("/add", methods=["POST"], name="addPresence")
    # @deps.user_validation
    def addPresence(session, request: Request, topic: str, nom: str):
        """
        Adds a locket to the system using the provided session, request, topic, and label.

        Args:
            session (dict): The session object containing user-specific data, such as "user_id".
            request (Request): The HTTP request object.
            topic (str): The topic associated with the locket.
            nom (str): The label or name of the locket.

        Returns:
            dict: A dictionary containing the status and message of the operation.
                On success, returns {"status": "success", "message": "Locket added successfully"}.
                On failure, returns {"status": "error", "message": "An error occurred while adding the locket."}.
        """
        try:
            OPTIONS.CRUD.add(
                locket=schemas.AddLocket(
                    user_id=session["user_id"],
                    topic=topic,
                    label=nom,
                )
            )
            return {"status": "success", "message": "Locket added successfully"}

        except Exception:
            return {
                "status": "error",
                "message": "An error occurred while adding the locket.",
            }

    @router("/delete/{locket_id}", methods=["DELETE"], name="deletePresence")
    # @deps.user_validation
    def deletePresence(session, request: Request, locket_id: str):
        try:
            OPTIONS.CRUD.remove(
                locket=schemas.DelLocket(
                    user_id=session["user_id"], locket_id=locket_id
                )
            )
            OPTIONS.CARD.remove_by_id(locket_id)
            return {"status": "success", "message": "Locket deleted successfully"}
        except Exception:
            return {
                "status": "error",
                "message": "An error occurred while deleting the locket.",
            }

    @router("/rfid/{locket_id}", methods=["POST"], name="VerifiedUserPresence")
    # #@deps.user_validation
    def VerifiedUserPresence(
        session, request: Request, locket_id: str, actif: bool = True
    ):
        OPTIONS.clientMq.publish(
            topic=OPTIONS.MQCMD.uq_user_topic_cmds(
                base=OPTIONS.CRUD.get_by_id(locket_id)["topic"],
                types="cmd",
                user_id=session["user_id"],
            ),
            msg=OPTIONS.MQCMD.STATUS,
        )
        return {
            "status": "success",
            "message": f"Locket presence updated to {'active' if actif else 'inactive'}",
        }

    @router("/{locket_id}/reset", methods=["GET"], name="resetPresenceTpe")
    # #@deps.user_validation
    def resetPresenceTpe(session, request: Request, locket_id: str):
        try:
            locket = OPTIONS.CRUD.get_by_id(locket_id)
            if not locket:
                return {"status": "error", "message": "Locket not found."}
            OPTIONS.clientMq.publish(
                topic=OPTIONS.MQCMD.uq_user_topic_cmds(
                    base=locket["topic"], types="cmd", user_id=session["user_id"]
                ),
                msg=OPTIONS.MQCMD.RESET,
            )
            return {
                "status": "success",
                "message": "Locket has been reset successfully",
            }
        except Exception:
            return {
                "status": "error",
                "message": "An error occurred while adding the card.",
            }


class PresenceCardRoute:

    def __init__(self):
        pass

    @router("/add/card", methods=["POST"], name="addCard Presence")
    # #@deps.user_validation
    def addCard(
        session,
        request: Request,
        rfidId: str,
        idcarte: str,
        label: str,
        categorie: str,
        status: bool,
    ):
        try:
            locket = OPTIONS.CRUD.get_by_id(rfidId)
            OPTIONS.CARD.add(
                locket=schemas.AddRfidCard(
                    uid=idcarte,
                    locket_id=rfidId,
                    user_id=session["user_id"],
                    label=label,
                    types=(
                        schemas.CardTypes.MASTERCARD
                        if categorie == "Master_card"
                        else schemas.CardTypes.SIMPLECARD
                    ),
                    status=status,
                )
            )
            if categorie == "Master_card":
                if locket:
                    OPTIONS.clientMq.publish(
                        topic=OPTIONS.MQCMD.uq_user_topic_cmds(
                            base=locket["topic"],
                            types="cmd",
                            user_id=session["user_id"],
                        ),
                        msg=OPTIONS.MQCMD.msg_add(idcarte),
                    )
            return {"status": "success", "message": "Card added successfully"}
        except Exception:
            return {
                "status": "error",
                "message": "An error occurred while adding the card.",
            }

    @router("/delete/card/{card_id}", methods=["DELETE"])
    # #@deps.user_validation
    def deleteCard(session, request: Request, card_id: str):
        try:
            response, card_information = OPTIONS.CARD.remove(
                carts=schemas.DeleteCard(user_id=session["user_id"], card_id=card_id)
            )
            print(f"Card removed: {card_information}")
            if card_information:
                OPTIONS.clientMq.publish(
                    topic=OPTIONS.MQCMD.uq_user_topic_cmds(
                        base=OPTIONS.CRUD.get_by_id(card_information[1])["topic"],
                        types="cmd",
                        user_id=session["user_id"],
                    ),
                    msg=OPTIONS.MQCMD.removeCard(card_information[0]),
                )
        except Exception as e:
            print(f"Error deleting card: {e}")
            return {
                "status": "error",
                "message": "An error occurred while deleting the card.",
            }

    @router("/status/card/{card_id}", methods=["POST"])
    # #@deps.user_validation
    def updateCardStatus(session, request: Request, card_id: str, actif: str):
        try:
            response, topic, uid = OPTIONS.CARD.update_status(
                status=schemas.UpdateCardStatus(
                    user_id=session["user_id"], card_id=card_id, status=str(actif)
                )
            )
            if topic:
                if actif == "False":
                    OPTIONS.clientMq.publish(
                        topic=OPTIONS.MQCMD.uq_user_topic_cmds(
                            base=topic, types="cmd", user_id=session["user_id"]
                        ),
                        msg=OPTIONS.MQCMD.removeCard(uid),
                    )
                else:
                    OPTIONS.clientMq.publish(
                        topic=OPTIONS.MQCMD.uq_user_topic_cmds(
                            base=topic, types="cmd", user_id=session["user_id"]
                        ),
                        msg=OPTIONS.MQCMD.msg_add(uid),
                    )

            return {"status": "success", "message": f"Card status updated to {actif}"}
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred while updating the card status.{e}",
            }


class HistoryRouter:

    def __init__(self):
        pass

    @router("/history/delete/{history_id}", methods=["DELETE"])
    # #@deps.user_validation
    def history(session, request: Request, history_id: str):

        if OPTIONS.HISTORY.delete_by_id(
            event=schemas.DeleteHistory(
                user_id=session["user_id"], cart_event_id=history_id
            )
        ):
            return {"status": "success", "message": "History deleted successfully"}
        else:
            return {
                "status": "error",
                "message": "An error occurred while deleting the history.",
            }


class Plugin(PresenceTpeRoute, PresenceCardRoute, HistoryRouter):

    def __init__(
        self,
    ):
        super().__init__()
        return

    @router("/", methods=["GET"])
    # ##@deps.user_validation
    def run(session, request: Request):
        session["user_id"] = "bc523c62-6d38-49f1-9741-124886"
        return OPTIONS.HOME.page()

    @router("/init", methods=["GET"])
    def initialization(
        session,
    ):
        try:
            locket_response = OPTIONS.CRUD.get(
                locket=schemas.GetLocket(user_id=session["user_id"])
            )
            card_response = OPTIONS.CARD.get(
                card=schemas.GetCard(user_id=session["user_id"])
            )
            return {
                "status": "success",
                "message": "Locket initialized successfully",
                "locket": locket_response if locket_response else [],
                "card": card_response if card_response else [],
            }

        except Exception:
            return {
                "status": "error",
                "message": "An error occurred during initialization.",
                "locket": [],
                "card": [],
            }

    @router("/history", methods=["GET"])
    # @deps.user_validation
    def history(session, request: Request):
        try:
            return {
                "status": "success",
                "message": "History retrieved successfully",
                "history": OPTIONS.HISTORY.get_history(session["user_id"]),
            }
        except Exception:
            return {
                "status": "error",
                "message": "An error occurred while retrieving the history.",
                "history": [],
            }
