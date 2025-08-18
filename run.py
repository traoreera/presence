import os

# Ajout du logging
import sys

from fasthtml.common import APIRouter, Request

import deps
from core.logs.logger_config import get_logger

from . import schemas
from .models import locket  # noqa: F401
from .page.pages import Home

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Configuration du logger pour ce module
logger = get_logger(__name__)


class OPTIONS:
    from .crud.cards import CardCruds
    from .crud.events import EventCard
    from .crud.locket import LocketCruds
    from .task.presence import MqCmd, clientMq

    CRUD: LocketCruds = LocketCruds()
    CARD: CardCruds = CardCruds()
    HOME: Home = Home()
    HISTORY = EventCard()
    MQCMD = MqCmd


logger.info("🔧 OPTIONS du plugin Presence initialisées")

PLUGIN_INFO = {
    "name": "Presence",
    "version": "1.0.0",
    "author": "traore Eliezer",
    "Api_prefix": "/app/presence",
    "tag_for_identified": ["Plugin", "Presence"],
    "trigger": 2,
}

logger.info(f"🔌 Plugin {PLUGIN_INFO['name']} v{PLUGIN_INFO['version']} initialisé")

router = APIRouter(
    prefix=PLUGIN_INFO["Api_prefix"],
)

logger.info(f"🛣️  Router presence initialisé avec préfixe '{PLUGIN_INFO['Api_prefix']}'")


class PresenceTpeRoute:

    def __init__(self):
        logger.info("📍 PresenceTpeRoute initialisé")

    @router("/add", methods=["POST"], name="addPresence")
    @deps.user_validation
    def addPresence(session, request: Request, topic: str, nom: str):
        """
        Adds a locket to the system using the provided session, request, topic, and label.
        """
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"➕ Ajout d'un locket - User: {user_id}, Topic: {topic}, Label: {nom}, IP: {client_ip}"
        )

        try:
            OPTIONS.CRUD.add(
                locket=schemas.AddLocket(
                    user_id=session["user_id"],
                    topic=topic,
                    label=nom,
                )
            )
            logger.info(
                f"✅ Locket ajouté avec succès - User: {user_id}, Topic: {topic}"
            )
            return {"status": "success", "message": "Locket added successfully"}

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de l'ajout du locket - User: {user_id}, Topic: {topic}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while adding the locket.",
            }

    @router("/delete/{locket_id}", methods=["DELETE"], name="deletePresence")
    @deps.user_validation
    def deletePresence(session, request: Request, locket_id: str):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"🗑️  Suppression du locket {locket_id} - User: {user_id}, IP: {client_ip}"
        )

        try:
            OPTIONS.CRUD.remove(
                locket=schemas.DelLocket(
                    user_id=session["user_id"], locket_id=locket_id
                )
            )
            logger.info(f"✅ Locket {locket_id} supprimé du CRUD")

            OPTIONS.CARD.remove_by_id(locket_id)
            logger.info(f"✅ Cartes associées au locket {locket_id} supprimées")

            logger.info(f"✅ Locket {locket_id} supprimé avec succès - User: {user_id}")
            return {"status": "success", "message": "Locket deleted successfully"}

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de la suppression du locket {locket_id} - User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while deleting the locket.",
            }

    @router("/rfid/{locket_id}", methods=["POST"], name="VerifiedUserPresence")
    @deps.user_validation
    def VerifiedUserPresence(
        session, request: Request, locket_id: str, actif: bool = True
    ):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"📡 Mise à jour de la présence RFID - Locket: {locket_id}, User: {user_id}, Actif: {actif}, IP: {client_ip}"
        )

        try:
            # Récupération des informations du locket
            locket_info = OPTIONS.CRUD.get_by_id(locket_id)
            if not locket_info:
                logger.warning(f"⚠️  Locket {locket_id} introuvable")
                return {"status": "error", "message": "Locket not found"}

            topic = locket_info["topic"]
            logger.debug(f"🔍 Topic récupéré pour le locket {locket_id}: {topic}")

            # Publication du message MQTT
            mqtt_topic = OPTIONS.MQCMD.uq_user_topic_cmds(
                base=topic,
                types="cmd",
                user_id=session["user_id"],
            )

            OPTIONS.clientMq.publish(
                topic=mqtt_topic,
                msg=OPTIONS.MQCMD.STATUS,
            )

            logger.info(
                f"✅ Message MQTT publié avec succès - Topic: {mqtt_topic}, Locket: {locket_id}"
            )

            return {
                "status": "success",
                "message": f"Locket presence updated to {'active' if actif else 'inactive'}",
            }

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de la mise à jour de la présence - Locket: {locket_id}, User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while updating presence.",
            }

    @router("/{locket_id}/reset", methods=["GET"], name="resetPresenceTpe")
    @deps.user_validation
    def resetPresenceTpe(session, request: Request, locket_id: str):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"🔄 Reset du locket {locket_id} - User: {user_id}, IP: {client_ip}"
        )

        try:
            locket = OPTIONS.CRUD.get_by_id(locket_id)
            if not locket:
                logger.warning(f"⚠️  Locket {locket_id} introuvable pour le reset")
                return {"status": "error", "message": "Locket not found."}

            logger.debug(f"🔍 Locket trouvé pour reset: {locket}")

            topic = OPTIONS.MQCMD.uq_user_topic_cmds(
                base=locket["topic"], types="cmd", user_id=session["user_id"]
            )

            OPTIONS.clientMq.publish(
                topic=topic,
                msg=OPTIONS.MQCMD.RESET,
            )

            logger.info(
                f"✅ Reset du locket {locket_id} effectué avec succès - User: {user_id}"
            )
            return {
                "status": "success",
                "message": "Locket has been reset successfully",
            }

        except Exception as e:
            logger.error(
                f"❌ Erreur lors du reset du locket {locket_id} - User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while resetting the locket.",
            }


class PresenceCardRoute:

    def __init__(self):
        logger.info("💳 PresenceCardRoute initialisé")

    @router("/add/card", methods=["POST"], name="addCard Presence")
    @deps.user_validation
    def addCard(
        session,
        request: Request,
        rfidId: str,
        idcarte: str,
        label: str,
        categorie: str,
        status: bool,
    ):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"💳 Ajout d'une carte - RFID: {rfidId}, Card: {idcarte[:4]}****, Label: {label}, Type: {categorie}, User: {user_id}, IP: {client_ip}"
        )

        try:
            locket = OPTIONS.CRUD.get_by_id(rfidId)
            if not locket:
                logger.warning(f"⚠️  Locket {rfidId} introuvable pour l'ajout de carte")
                return {"status": "error", "message": "Locket not found"}

            card_type = (
                schemas.CardTypes.MASTERCARD
                if categorie == "Master_card"
                else schemas.CardTypes.SIMPLECARD
            )

            logger.debug(f"🏷️  Type de carte déterminé: {card_type} pour {categorie}")

            OPTIONS.CARD.add(
                locket=schemas.AddRfidCard(
                    uid=idcarte,
                    locket_id=rfidId,
                    user_id=session["user_id"],
                    label=label,
                    types=card_type,
                    status=status,
                )
            )

            logger.info(f"✅ Carte {idcarte[:4]}**** ajoutée avec succès")

            # Publication MQTT pour Master Card
            if categorie == "Master_card":
                logger.info(f"🔑 Traitement spécial pour Master Card {idcarte[:4]}****")

                if locket:
                    topic = OPTIONS.MQCMD.uq_user_topic_cmds(
                        base=locket["topic"],
                        types="cmd",
                        user_id=session["user_id"],
                    )

                    OPTIONS.clientMq.publish(
                        topic=topic,
                        msg=OPTIONS.MQCMD.msg_add(idcarte),
                    )

                    logger.info(
                        f"📡 Message MQTT envoyé pour Master Card {idcarte[:4]}**** - Topic: {topic}"
                    )

            return {"status": "success", "message": "Card added successfully"}

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de l'ajout de la carte {idcarte[:4]}**** - User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while adding the card.",
            }

    @router("/delete/card/{card_id}", methods=["DELETE"])
    @deps.user_validation
    def deleteCard(session, request: Request, card_id: str):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"🗑️  Suppression de la carte {card_id} - User: {user_id}, IP: {client_ip}"
        )

        try:
            response, card_information = OPTIONS.CARD.remove(
                carts=schemas.DeleteCard(user_id=session["user_id"], card_id=card_id)
            )

            logger.info(f"📋 Carte supprimée du CRUD: {card_information}")

            if card_information:
                locket_id = card_information[1]
                card_uid = card_information[0]

                logger.debug(
                    f"🔍 Informations carte: UID={card_uid[:4]}****, Locket={locket_id}"
                )

                # Publication MQTT pour notifier la suppression
                locket_info = OPTIONS.CRUD.get_by_id(locket_id)
                if locket_info:
                    topic = OPTIONS.MQCMD.uq_user_topic_cmds(
                        base=locket_info["topic"],
                        types="cmd",
                        user_id=session["user_id"],
                    )

                    OPTIONS.clientMq.publish(
                        topic=topic,
                        msg=OPTIONS.MQCMD.removeCard(card_uid),
                    )

                    logger.info(
                        f"📡 Message MQTT de suppression envoyé - Topic: {topic}, Card: {card_uid[:4]}****"
                    )
                else:
                    logger.warning(
                        f"⚠️  Locket {locket_id} introuvable pour la notification MQTT"
                    )

            logger.info(f"✅ Carte {card_id} supprimée avec succès - User: {user_id}")
            return {"status": "success", "message": "Card deleted successfully"}

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de la suppression de la carte {card_id} - User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while deleting the card.",
            }

    @router("/status/card/{card_id}", methods=["POST"])
    @deps.user_validation
    def updateCardStatus(session, request: Request, card_id: str, actif: str):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"🔄 Mise à jour du statut de la carte {card_id} vers '{actif}' - User: {user_id}, IP: {client_ip}"
        )

        try:
            response, topic, uid = OPTIONS.CARD.update_status(
                status=schemas.UpdateCardStatus(
                    user_id=session["user_id"], card_id=card_id, status=str(actif)
                )
            )

            logger.info(
                f"📋 Statut de la carte mis à jour en base - Card: {card_id}, Status: {actif}"
            )

            if topic:
                logger.debug(
                    f"📡 Préparation de la publication MQTT - Topic: {topic}, UID: {uid[:4]}****"
                )

                mqtt_topic = OPTIONS.MQCMD.uq_user_topic_cmds(
                    base=topic, types="cmd", user_id=session["user_id"]
                )

                if actif == "False":
                    logger.info(f"❌ Désactivation de la carte {uid[:4]}**** via MQTT")
                    OPTIONS.clientMq.publish(
                        topic=mqtt_topic,
                        msg=OPTIONS.MQCMD.removeCard(uid),
                    )
                else:
                    logger.info(f"✅ Activation de la carte {uid[:4]}**** via MQTT")
                    OPTIONS.clientMq.publish(
                        topic=mqtt_topic,
                        msg=OPTIONS.MQCMD.msg_add(uid),
                    )

                logger.info(f"📡 Message MQTT envoyé avec succès - Topic: {mqtt_topic}")
            else:
                logger.warning(f"⚠️  Aucun topic disponible pour la carte {card_id}")

            return {"status": "success", "message": f"Card status updated to {actif}"}

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de la mise à jour du statut de la carte {card_id} - User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": f"An error occurred while updating the card status: {e}",
            }


class HistoryRouter:

    def __init__(self):
        logger.info("📜 HistoryRouter initialisé")

    @router("/history/delete/{history_id}", methods=["DELETE"])
    @deps.user_validation
    def history(session, request: Request, history_id: str):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"🗑️  Suppression de l'historique {history_id} - User: {user_id}, IP: {client_ip}"
        )

        try:
            result = OPTIONS.HISTORY.delete_by_id(
                event=schemas.DeleteHistory(
                    user_id=session["user_id"], cart_event_id=history_id
                )
            )

            if result:
                logger.info(
                    f"✅ Historique {history_id} supprimé avec succès - User: {user_id}"
                )
                return {"status": "success", "message": "History deleted successfully"}
            else:
                logger.warning(
                    f"⚠️  Échec de la suppression de l'historique {history_id} - User: {user_id}"
                )
                return {
                    "status": "error",
                    "message": "An error occurred while deleting the history.",
                }

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de la suppression de l'historique {history_id} - User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while deleting the history.",
            }


class Plugin(PresenceTpeRoute, PresenceCardRoute, HistoryRouter):

    def __init__(self):
        super().__init__()
        logger.info("🔌 Plugin Presence initialisé avec toutes les routes")

    @router("/", methods=["GET"])
    @deps.user_validation
    @deps.user_validation
    def run(session, request: Request):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"🏠 Accès à la page principale du plugin Presence - User: {user_id}, IP: {client_ip}"
        )

        try:
            result = OPTIONS.HOME.page()
            logger.info(f"✅ Page Presence générée avec succès - User: {user_id}")
            return result
        except Exception as e:
            logger.error(
                f"❌ Erreur lors de la génération de la page Presence - User: {user_id}: {e}"
            )
            raise

    @router("/init", methods=["GET"])
    @deps.user_validation
    def initialization(session, request):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"🔧 Initialisation des données Presence - User: {user_id}, IP: {client_ip}"
        )

        try:
            locket_response = OPTIONS.CRUD.get(
                locket=schemas.GetLocket(user_id=session["user_id"])
            )

            locket_count = len(locket_response) if locket_response else 0
            logger.info(
                f"📍 {locket_count} lockets récupérés pour l'utilisateur {user_id}"
            )

            card_response = OPTIONS.CARD.get(
                card=schemas.GetCard(user_id=session["user_id"])
            )

            card_count = len(card_response) if card_response else 0
            logger.info(
                f"💳 {card_count} cartes récupérées pour l'utilisateur {user_id}"
            )

            logger.info(
                f"✅ Initialisation terminée avec succès - User: {user_id}, Lockets: {locket_count}, Cards: {card_count}"
            )

            return {
                "status": "success",
                "message": "Locket initialized successfully",
                "locket": locket_response if locket_response else [],
                "card": card_response if card_response else [],
            }

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation - User: {user_id}: {e}")
            return {
                "status": "error",
                "message": "An error occurred during initialization.",
                "locket": [],
                "card": [],
            }

    @router("/history", methods=["GET"])
    @deps.user_validation
    def history(session, request: Request):
        user_id = session.get("user_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"📜 Récupération de l'historique - User: {user_id}, IP: {client_ip}"
        )

        try:
            history_data = OPTIONS.HISTORY.get_history(session["user_id"])
            history_count = len(history_data) if history_data else 0

            logger.info(
                f"✅ {history_count} éléments d'historique récupérés - User: {user_id}"
            )

            return {
                "status": "success",
                "message": "History retrieved successfully",
                "history": history_data,
            }

        except Exception as e:
            logger.error(
                f"❌ Erreur lors de la récupération de l'historique - User: {user_id}: {e}"
            )
            return {
                "status": "error",
                "message": "An error occurred while retrieving the history.",
                "history": [],
            }


logger.info("🔌 Plugin Presence chargé avec succès")
