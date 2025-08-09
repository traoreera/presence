from fasthtml.common import (H2, H3, Button, Div, Form, I, Input,  # noqa: F403
                             Label, Link, Main, Meta, Option, P, Script,
                             Section, Select, Span, Table, Tbody, Th, Thead,
                             Tr)

from core.composants import *  # noqa: F403
from deps import AllPage


class Home:

    def __init__(
        self,
    ):
        self.html = AllPage(
            title="presence",
            head=[
                Link(rel="stylesheet", href="../../css/style.css"),
                Link(rel="stylesheet", href="../../css/locket.css"),
                Script(src="../../js/userBord.js"),
                Meta(charset="UTF-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
                Meta(
                    name="description",
                    content="presence est un plugin pour gérer la présence des utilisateurs dans un bureau grace a des cartes RFID.",
                ),
                Meta(
                    name="keywords",
                    content="locket, plugin, web application, resource management",
                ),
                Meta(name="author", content="Tanga Group"),
                Link(
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                    rel="stylesheet",
                ),
                Link(
                    rel="stylesheet",
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
                ),
                Script(src="https://cdn.jsdelivr.net/npm/sweetalert2@11"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css",
                ),
                Script(src="https://cdn.jsdelivr.net/npm/toastify-js"),
            ],
            plugins=[
                {
                    "name": "Locket",
                    "url": "/app/locket",
                },
                {
                    "name": "Presence",
                    "url": "/app/presence",
                },
            ],
            content=[
                self.mainPage(),
                self.addRfidModal(),
                self.addModalCard(),
                self.modalCards(),
                self.historyModal(),
                Script(src="../../js/Locketscript.js"),
            ],
        )

    def modalCards(
        self,
    ):
        return Div(
            Div(
                Span("×", cls="fermer-modal fermer-modal-card"),
                H2("Cartes pour", Span(id="nomRfidCard", cls="nom-rfid-card")),
                Table(
                    Thead(
                        Tr(
                            Th("Label"),
                            Th("type"),
                            Th("action"),
                        )
                    ),
                    Tbody(id="listeCartesBody"),
                ),
                cls="contenu-modal",
            ),
            id="modalCard",
            cls="modal",
        )

    def addModalCard(
        self,
    ):
        return (
            Div(
                Div(
                    Span("×", cls="fermer-modal fermer-modal-element"),
                    H2(
                        "Ajouter une Nouvelle Carte pour",
                        Span(id="nomRfidElement", cls="nom-rfid-element"),
                    ),
                    Form(
                        Input(type="hidden", id="rfidParentId"),
                        Div(
                            Label("Identifiant de la carte :", fr="idcarte"),
                            Input(
                                type="text",
                                id="idcarte",
                                required="",
                                placeholder="Ex: 1234567890, 0987654321",
                            ),
                            cls="champ-formulaire",
                        ),
                        Div(
                            Label("Label de la carte :", fr="labelElement"),
                            Input(
                                type="text",
                                id="labelElement",
                                required="",
                                placeholder="Ex: Carte d'accès, Badge de sécurité",
                            ),
                            cls="champ-formulaire",
                        ),
                        Div(
                            Label("Type de la carte :", fr="categorieElement"),
                            Select(
                                Option("Simple Card", value="Simple_card"),
                                name="categorieElement",
                                id="categorieElement",
                            ),
                            cls="champ-formulaire",
                        ),
                        Button(
                            "Ajouter cet Élément",
                            type="submit",
                            cls="bouton-primaire",
                        ),
                        id="formulaireAjoutElement",
                    ),
                    cls="contenu-modal",
                ),
                id="modalNouvelElement",
                cls="modal",
            ),
        )

    def addRfidModal(self):
        return Div(
            Div(
                Span("×", cls="fermer-modal"),
                H2("Ajouter un nouveau Dispositif RFID"),
                Form(
                    Div(
                        Label("Topic de presence :", fr="topicNouveauRFID"),
                        Input(
                            type="text",
                            id="topicNouveauRFID",
                            required="",
                            placeholder="Topic du Lockey",
                        ),
                        cls="champ-formulaire",
                    ),
                    Div(
                        Label("Nom du Lockey :", fr="nomNouveauRFID"),
                        Input(
                            type="text",
                            id="nomNouveauRFID",
                            required="",
                            placeholder="Label du Lockey",
                        ),
                        cls="champ-formulaire",
                    ),
                    Button(
                        "Ajouter ce Lockey",
                        type="submit",
                        cls="bouton-primaire",
                    ),
                    id="formulaireAjoutRFID",
                ),
                cls="contenu-modal",
            ),
            id="modalAjouterRFID",
            cls="modal",
        )

    def historyModal(self):
        return Div(
            Div(
                Span(
                    "×",
                    cls="fermer-modal",
                    id="fermerModalHistorique",
                ),
                H2("historique des Dispositifs presense"),
                Table(
                    Thead(
                        Tr(
                            Th("label"),
                            Th("Evennements"),
                            Th("Date"),
                            Th("Action"),
                        )
                    ),
                    Tbody(id="listeHistoriqueBody"),
                ),
                cls="contenu-modal",
            ),
            id="modalHistorique",
            cls="modal",
        )

    def mainPage(self):
        return Main(
            Div(
                Button(
                    I(cls="fas fa-plus-circle"),
                    "Ajouter un nouveau RFID",
                    id="boutonAjouterRFID",
                    cls="bouton-primaire",
                ),
                cls="divbtn",
            ),
            Section(
                H2("Statistiques Générales"),
                Div(
                    H3("Nombre de dispositf de presence actifs"),
                    P("0", id="dashboardCompteurRFID", cls="compteur-grand"),
                    cls="carte-dashboard",
                ),
                Div(Button(I(cls="fas fa-eye"), "historique", id="btnHistorique")),
                cls="section-dashboard",
            ),
            Section(
                H2("Mes Dispositifs RFID"),
                Div(
                    P(
                        'Aucun RFID ajouté pour le moment. Cliquez sur\r\n "Ajouter un nouveau RFID" !',
                        id="messageAucunRFID",
                        cls="message-aucun-rfid",
                    ),
                    id="listeRFID",
                    cls="grille-rfid",
                ),
                cls="section-liste-rfid",
            ),
            cls="contenu-principal conteneur-principal",
        )

    def page(self):
        return self.html.page()
