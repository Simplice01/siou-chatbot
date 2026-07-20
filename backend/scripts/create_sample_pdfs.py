from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = ROOT / "documents"


def draw_wrapped(pdf, text: str, x: float, y: float, width: float, font: str, size: float, leading: float) -> float:
    pdf.setFont(font, size)
    for line in simpleSplit(text, font, size, width):
        pdf.drawString(x, y, line)
        y -= leading
    return y


def draw_table(pdf, rows: list[tuple[str, str]], x: float, y: float, width: float, label_width: float) -> float:
    value_width = width - label_width
    wrapped_rows = []
    row_heights = []
    for label, value in rows:
        label_lines = simpleSplit(label, "Helvetica-Bold", 9.5, label_width - 12)
        value_lines = simpleSplit(value, "Helvetica", 9.5, value_width - 12)
        lines = max(len(label_lines), len(value_lines))
        wrapped_rows.append((label_lines, value_lines))
        row_heights.append(max(0.82 * cm, lines * 12 + 12))

    current_y = y
    for index, ((label_lines, value_lines), height) in enumerate(zip(wrapped_rows, row_heights)):
        pdf.setFillColor(colors.HexColor("#dfe9dc") if index == 0 else colors.HexColor("#fffdf7"))
        pdf.rect(x, current_y - height, width, height, fill=1, stroke=0)
        pdf.setStrokeColor(colors.HexColor("#b8c8b6"))
        pdf.rect(x, current_y - height, width, height, fill=0, stroke=1)
        pdf.line(x + label_width, current_y, x + label_width, current_y - height)

        pdf.setFillColor(colors.HexColor("#1f2a22"))
        pdf.setFont("Helvetica-Bold", 9.5)
        line_y = current_y - 0.42 * cm
        for line in label_lines:
            pdf.drawString(x + 6, line_y, line)
            line_y -= 12

        pdf.setFont("Helvetica-Bold" if index == 0 else "Helvetica", 9.5)
        line_y = current_y - 0.42 * cm
        for line in value_lines:
            pdf.drawString(x + label_width + 6, line_y, line)
            line_y -= 12
        current_y -= height
    return current_y


def build_pdf(filename: str, title: str, subtitle: str, pages: list[dict[str, str]]) -> None:
    path = DOCUMENTS_DIR / filename
    pdf = canvas.Canvas(str(path))
    for index, item in enumerate(pages, start=1):
        page_size = landscape(A4) if item["orientation"] == "paysage" else portrait(A4)
        width, height = page_size
        margin = 1.45 * cm
        pdf.setPageSize(page_size)

        pdf.setFillColor(colors.HexColor("#49664d"))
        pdf.rect(0, height - 0.42 * cm, width, 0.42 * cm, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#f5f7f2"))
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(margin, height - 0.29 * cm, "SIOU - Systeme Intelligent d'Orientation des Usagers")

        y = height - 1.25 * cm
        if index == 1:
            pdf.setFillColor(colors.HexColor("#1f2a22"))
            y = draw_wrapped(pdf, title, margin, y, width - 2 * margin, "Helvetica-Bold", 23, 29)
            pdf.setFillColor(colors.HexColor("#38443a"))
            y = draw_wrapped(pdf, subtitle, margin, y - 0.2 * cm, width - 2 * margin, "Helvetica", 10.5, 15)
            y -= 0.25 * cm

        pdf.setFillColor(colors.HexColor("#2f6575"))
        y = draw_wrapped(pdf, f"Page {index} - {item['heading']}", margin, y, width - 2 * margin, "Helvetica-Bold", 16, 21)
        pdf.setFillColor(colors.HexColor("#1f241f"))
        y = draw_wrapped(pdf, item["body"], margin, y - 0.2 * cm, width - 2 * margin, "Helvetica", 10.5, 15)
        y -= 0.25 * cm

        label_width = 4.5 * cm if item["orientation"] == "portrait" else 5.5 * cm
        rows = [
            ("Champ", "Valeur"),
            ("Structure", item["structure"]),
            ("Orientation usager", item["orientation_user"]),
            ("Adresse / contact", item["contact"]),
            ("Validite", item["validity"]),
        ]
        y = draw_table(pdf, rows, margin, y, width - 2 * margin, label_width)
        y -= 0.35 * cm

        pdf.setFillColor(colors.HexColor("#5f6f61"))
        draw_wrapped(pdf, f"Note source: {item['note']}", margin, y, width - 2 * margin, "Helvetica", 8.5, 11)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(margin, 0.85 * cm, f"{title} - page {index}")
        pdf.drawRightString(width - margin, 0.85 * cm, f"Orientation: {item['orientation']}")
        pdf.showPage()
    pdf.save()


ANNUAIRE = [
    {
        "orientation": "portrait",
        "heading": "Accueil et logique d'orientation SIOU",
        "body": "SIOU aide la secretaire ou l'agent d'accueil a comprendre une demande formulee librement et a orienter l'usager vers la bonne structure. Le systeme repond a qui fait quoi, ou aller, quel contact utiliser et quelles informations recentes consulter.",
        "structure": "Secretariat d'accueil du MTDI",
        "orientation_user": "Ecouter la demande, poser la question a SIOU, puis communiquer la structure competente a l'usager.",
        "contact": "Accueil MTDI, Boulevard de la Marina, Cotonou. Telephone test: +229 01 90 00 10 10. Horaires: lundi a vendredi, 8h00-17h00.",
        "validity": "Fiche valide pour les tests jusqu'au 31 decembre 2026.",
        "note": "Cette fiche definit le role de l'agent IA: orienter, pas executer la demarche.",
    },
    {
        "orientation": "paysage",
        "heading": "Direction du Numerique",
        "body": "La Direction du Numerique coordonne les politiques publiques liees a la transformation digitale, au pilotage des projets numeriques ministeriels et a l'orientation strategique des services publics numeriques.",
        "structure": "Direction du Numerique du MTDI",
        "orientation_user": "Pour une question sur une politique numerique, un projet public digital ou une strategie sectorielle, orienter vers la Direction du Numerique.",
        "contact": "Bureau DN, 2e etage MTDI, Cotonou. Email test: direction.numerique@mtdi.test. Telephone test: +229 01 90 00 11 01.",
        "validity": "Derniere revision: 15 juillet 2026.",
        "note": "Competente pour la coordination strategique, pas pour les incidents techniques individuels.",
    },
    {
        "orientation": "portrait",
        "heading": "Agence des Systemes d'Information et du Numerique",
        "body": "L'ASIN accompagne la securisation et la mise en oeuvre operationnelle des systemes d'information publics. Elle est l'interlocuteur naturel pour les questions de cybersécurite institutionnelle, de plateformes publiques et d'infrastructure numerique.",
        "structure": "ASIN",
        "orientation_user": "Pour un probleme de cybersecurite publique, une plateforme gouvernementale ou une question d'infrastructure SI, orienter vers l'ASIN.",
        "contact": "Siege ASIN, Zone administrative, Cotonou. Email test: contact@asin.test. Telephone test: +229 01 90 00 12 02.",
        "validity": "Derniere revision: 15 juillet 2026.",
        "note": "Ne pas orienter vers l'ASIN pour une simple demande commerciale d'operateur telecom.",
    },
    {
        "orientation": "paysage",
        "heading": "Agence de Developpement du Numerique",
        "body": "L'ADN suit les initiatives de developpement numerique, les projets de transformation, l'accompagnement des usages et certaines actions de promotion de l'ecosysteme numerique.",
        "structure": "ADN",
        "orientation_user": "Pour un projet d'accompagnement numerique, un programme d'innovation ou une initiative de developpement digital, orienter vers l'ADN.",
        "contact": "Guichet ADN, Cotonou. Email test: orientation@adn.test. Telephone test: +229 01 90 00 13 03.",
        "validity": "Derniere revision: 15 juillet 2026.",
        "note": "Fiche utilisee pour distinguer ADN, DN et ASIN.",
    },
    {
        "orientation": "portrait",
        "heading": "SBIN et services de connectivite",
        "body": "La SBIN est citee comme interlocuteur de services de connectivite, de reseaux et d'offres telecom. SIOU doit orienter vers la SBIN lorsque la demande concerne un abonnement, une ligne, une connexion ou un service telecom.",
        "structure": "SBIN",
        "orientation_user": "Pour une demande d'abonnement internet, de ligne telephonique ou de connectivite, orienter vers le guichet SBIN.",
        "contact": "Agence SBIN Cotonou centre. Telephone test: +229 01 90 00 14 04. Horaires: lundi a samedi, 8h00-18h00.",
        "validity": "Derniere revision: 15 juillet 2026.",
        "note": "Les incidents cyber institutionnels ne relevent pas de cette fiche.",
    },
    {
        "orientation": "paysage",
        "heading": "Guichet Startup et label Startup",
        "body": "Les demandes de label Startup, d'orientation vers les dispositifs d'accompagnement et d'information sur les avantages du Startup Act sont orientees vers le Guichet Startup du ministere.",
        "structure": "Guichet Startup MTDI",
        "orientation_user": "Pour creer une startup ou demander le label Startup, orienter vers le Guichet Startup.",
        "contact": "Guichet Startup, rez-de-chaussee MTDI. Email test: startup@mtdi.test. Telephone test: +229 01 90 00 15 05.",
        "validity": "Derniere revision: 16 juillet 2026.",
        "note": "Cette fiche repond aux questions du type: je veux creer une startup.",
    },
    {
        "orientation": "portrait",
        "heading": "Service information et accueil usagers",
        "body": "Le service information et accueil usagers traite les demandes generales lorsque l'usager ne sait pas quelle direction contacter. Il reformule la demande, verifie les sources et oriente vers la structure competente.",
        "structure": "Service accueil usagers MTDI",
        "orientation_user": "Si la demande est vague, orienter d'abord vers l'accueil usagers pour qualification.",
        "contact": "Hall principal MTDI. Telephone test: +229 01 90 00 16 06. Email test: accueil@mtdi.test.",
        "validity": "Derniere revision: 16 juillet 2026.",
        "note": "Point d'entree par defaut pour les demandes mal formulees.",
    },
    {
        "orientation": "paysage",
        "heading": "Point focal donnees et open data",
        "body": "Les demandes relatives aux jeux de donnees publics, a la reutilisation de donnees administratives et aux projets open data doivent etre orientees vers le point focal donnees du ministere.",
        "structure": "Point focal donnees MTDI",
        "orientation_user": "Pour demander une source de donnees publique ou une information sur l'open data, orienter vers le point focal donnees.",
        "contact": "Email test: donnees@mtdi.test. Rendez-vous sur demande via l'accueil MTDI.",
        "validity": "Derniere revision: 16 juillet 2026.",
        "note": "Ne pas confondre avec les demandes de donnees personnelles, qui necessitent un avis juridique.",
    },
    {
        "orientation": "portrait",
        "heading": "Cellule protection des donnees",
        "body": "La cellule protection des donnees conseille sur les questions de confidentialite, de traitement des donnees personnelles et de conservation des informations collectees lors des interactions avec les usagers.",
        "structure": "Cellule protection des donnees MTDI",
        "orientation_user": "Pour une question sur la protection des donnees personnelles ou la conservation de logs, orienter vers cette cellule.",
        "contact": "Email test: donnees.personnelles@mtdi.test. Telephone test: +229 01 90 00 17 07.",
        "validity": "Derniere revision: 16 juillet 2026.",
        "note": "Fiche utile pour distinguer donnees publiques et donnees personnelles.",
    },
    {
        "orientation": "paysage",
        "heading": "Equipe support SIOU",
        "body": "L'equipe support SIOU recoit les signalements sur les reponses incorrectes, les documents obsoletes et les problemes d'indexation. Elle ne remplace pas les directions metier.",
        "structure": "Equipe support SIOU",
        "orientation_user": "Pour signaler une reponse fausse ou une source obsolète dans SIOU, contacter le support SIOU.",
        "contact": "Email test: support-siou@mtdi.test. Delai cible: 1 jour ouvrable pour accusé de reception.",
        "validity": "Derniere revision: 16 juillet 2026.",
        "note": "Support de l'outil, pas support administratif global.",
    },
    {
        "orientation": "portrait",
        "heading": "Secretariat du cabinet",
        "body": "Le Secretariat du cabinet reçoit les demandes officielles adressees au ministre, les courriers institutionnels et les demandes de rendez-vous formels.",
        "structure": "Secretariat du cabinet MTDI",
        "orientation_user": "Pour un courrier officiel, une audience ou une correspondance institutionnelle, orienter vers le Secretariat du cabinet.",
        "contact": "Bureau courrier MTDI. Email test: cabinet@mtdi.test. Horaires: lundi a vendredi, 8h00-16h00.",
        "validity": "Derniere revision: 17 juillet 2026.",
        "note": "Ne pas orienter les questions techniques courantes vers le cabinet.",
    },
    {
        "orientation": "paysage",
        "heading": "Cellule communication",
        "body": "La cellule communication traite les demandes de presse, de diffusion d'informations officielles, de couverture d'evenements et de publication sur les canaux institutionnels.",
        "structure": "Cellule communication MTDI",
        "orientation_user": "Pour une demande media, une publication officielle ou une couverture d'evenement, orienter vers la cellule communication.",
        "contact": "Email test: communication@mtdi.test. Telephone test: +229 01 90 00 18 08.",
        "validity": "Derniere revision: 17 juillet 2026.",
        "note": "Les demandes d'evenements sont a croiser avec le calendrier officiel.",
    },
    {
        "orientation": "portrait",
        "heading": "Formation numerique des agents publics",
        "body": "Les demandes de formation des agents publics aux outils numeriques, a la bureautique, a la cyberhygiene ou aux services administratifs digitaux sont orientees vers le programme de formation numerique.",
        "structure": "Programme formation numerique MTDI",
        "orientation_user": "Pour inscrire un agent public a une formation numerique, orienter vers le programme de formation.",
        "contact": "Email test: formation@mtdi.test. Sessions mensuelles sur inscription.",
        "validity": "Derniere revision: 17 juillet 2026.",
        "note": "Cette fiche ne concerne pas les formations privees externes.",
    },
    {
        "orientation": "paysage",
        "heading": "Assistance aux plateformes publiques",
        "body": "Les difficultes d'acces a une plateforme publique numerique doivent etre qualifiees: si c'est un incident technique transversal, orienter vers l'ASIN; si c'est une question de procedure, orienter vers la direction metier competente.",
        "structure": "Accueil MTDI et ASIN selon le cas",
        "orientation_user": "Demander le nom de la plateforme, le type d'erreur et l'objectif de l'usager avant orientation.",
        "contact": "Premier niveau: accueil@mtdi.test. Escalade technique: contact@asin.test.",
        "validity": "Derniere revision: 17 juillet 2026.",
        "note": "Cette fiche aide l'agent IA a poser une clarification si necessaire.",
    },
    {
        "orientation": "portrait",
        "heading": "Procedure de prise de rendez-vous",
        "body": "Les rendez-vous avec une direction doivent passer par l'accueil ou le secretariat de la structure concernee. L'usager doit preciser son objet, sa structure d'origine et un contact de rappel.",
        "structure": "Accueil ou secretariat de la structure cible",
        "orientation_user": "Orienter vers le secretariat de la structure competente avec l'objet du rendez-vous.",
        "contact": "Accueil central: +229 01 90 00 10 10. Email test: accueil@mtdi.test.",
        "validity": "Derniere revision: 17 juillet 2026.",
        "note": "SIOU ne prend pas le rendez-vous, il indique le bon canal.",
    },
    {
        "orientation": "paysage",
        "heading": "Questions hors perimetre",
        "body": "Si la demande concerne une demarche non numerique, une information personnelle, un litige prive ou une decision administrative non documentee, SIOU doit indiquer que l'information est absente des documents disponibles.",
        "structure": "Aucune structure confirmée sans source",
        "orientation_user": "Ne pas inventer. Proposer de contacter l'accueil MTDI si la demande reste generale.",
        "contact": "Accueil MTDI: +229 01 90 00 10 10.",
        "validity": "Regle permanente de prudence.",
        "note": "Fiche de refus explicite pour eviter les hallucinations.",
    },
    {
        "orientation": "portrait",
        "heading": "Gouvernance des fiches",
        "body": "Chaque fiche d'information doit avoir un responsable de validation et une date de derniere revision. Les points focaux des agences verifient les informations concernant leur structure.",
        "structure": "Responsable ministere et points focaux agences",
        "orientation_user": "Pour signaler une fiche obsolette, orienter vers le support SIOU ou le point focal concerne.",
        "contact": "support-siou@mtdi.test.",
        "validity": "Revision mensuelle recommandee.",
        "note": "La fiabilite depend de la gouvernance humaine des donnees.",
    },
    {
        "orientation": "paysage",
        "heading": "Escalade des demandes sensibles",
        "body": "Les demandes sensibles liees a la securite, aux donnees personnelles, aux courriers officiels ou a une urgence institutionnelle doivent etre orientees vers la cellule specialisee correspondante.",
        "structure": "ASIN, Cellule protection des donnees ou Secretariat du cabinet",
        "orientation_user": "Identifier le type de sensibilite avant de donner une orientation.",
        "contact": "Cybersecurite: contact@asin.test. Donnees personnelles: donnees.personnelles@mtdi.test. Cabinet: cabinet@mtdi.test.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Page de synthese pour les cas sensibles.",
    },
    {
        "orientation": "portrait",
        "heading": "Reponse attendue de SIOU",
        "body": "Une bonne reponse SIOU est courte, structuree et directement utilisable par une secretaire: orientation, structure competente, adresse ou contact si disponible, information utile et document source.",
        "structure": "Agent IA SIOU",
        "orientation_user": "Repondre comme un assistant d'accueil administratif, pas comme un consultant technique.",
        "contact": "Source obligatoire: nom du document et page lorsque disponible.",
        "validity": "Regle de qualite V1.",
        "note": "Cette page fixe le format ideal de reponse.",
    },
    {
        "orientation": "paysage",
        "heading": "Synthese annuaire",
        "body": "L'annuaire SIOU couvre l'accueil MTDI, la Direction du Numerique, l'ASIN, l'ADN, la SBIN, le Guichet Startup, la cellule communication, la protection des donnees et le support SIOU.",
        "structure": "Corpus annuaire SIOU",
        "orientation_user": "Utiliser ce document pour repondre aux questions qui commencent par qui contacter, ou aller, quelle structure est competente.",
        "contact": "Voir chaque fiche specifique pour le contact exact.",
        "validity": "Corpus de test V1.",
        "note": "Cette synthese ne remplace pas les fiches detaillees.",
    },
]


PROCEDURES = [
    {
        "orientation": "portrait",
        "heading": "Demande de label Startup",
        "body": "L'usager qui veut demander le label Startup doit d'abord contacter le Guichet Startup pour verifier son eligibilite, obtenir la liste des pieces et connaitre le calendrier de depot.",
        "structure": "Guichet Startup MTDI",
        "orientation_user": "Orienter vers le Guichet Startup et demander a l'usager de preparer une description du projet, les statuts et les informations sur l'equipe.",
        "contact": "startup@mtdi.test. Guichet Startup, rez-de-chaussee MTDI.",
        "validity": "Procedure de test valide jusqu'au 31 decembre 2026.",
        "note": "Procedure d'orientation, pas depot reel du dossier.",
    },
    {
        "orientation": "paysage",
        "heading": "Creation d'une startup numerique",
        "body": "Pour une creation de startup numerique, SIOU oriente vers le Guichet Startup pour le label et vers l'ADN pour les programmes d'accompagnement numerique disponibles.",
        "structure": "Guichet Startup et ADN",
        "orientation_user": "Si l'usager demande par ou commencer, conseiller le Guichet Startup puis l'ADN pour l'accompagnement.",
        "contact": "startup@mtdi.test et orientation@adn.test.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Reponse attendue pour: je veux creer une startup.",
    },
    {
        "orientation": "portrait",
        "heading": "Incident de cybersecurite",
        "body": "Un incident de cybersecurite touchant une plateforme publique ou un systeme d'information institutionnel doit etre signale a l'ASIN avec une description de l'incident, l'heure observee et le service affecte.",
        "structure": "ASIN",
        "orientation_user": "Orienter vers l'ASIN. Ne pas demander de mot de passe ni d'information sensible dans le chat.",
        "contact": "contact@asin.test. Telephone test: +229 01 90 00 12 02.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Cas prioritaire pour une orientation rapide.",
    },
    {
        "orientation": "paysage",
        "heading": "Probleme d'abonnement internet",
        "body": "Une demande concernant une ligne, une facture, un abonnement internet ou une connexion telecom doit etre orientee vers la SBIN lorsque le service concerne releve de cet operateur.",
        "structure": "SBIN",
        "orientation_user": "Orienter vers le guichet SBIN avec le numero de ligne ou la reference client si l'usager la possede.",
        "contact": "Agence SBIN Cotonou centre. Telephone test: +229 01 90 00 14 04.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Ne pas confondre connectivite telecom et cybersecurite institutionnelle.",
    },
    {
        "orientation": "portrait",
        "heading": "Demande d'information open data",
        "body": "Une personne qui cherche un jeu de donnees public ou une autorisation de reutilisation de donnees institutionnelles doit etre orientee vers le point focal donnees.",
        "structure": "Point focal donnees MTDI",
        "orientation_user": "Orienter vers donnees@mtdi.test et demander de preciser le jeu de donnees recherche.",
        "contact": "donnees@mtdi.test.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Le point focal donnees ne traite pas les demandes d'acces a des donnees personnelles.",
    },
    {
        "orientation": "paysage",
        "heading": "Protection des donnees personnelles",
        "body": "Si l'usager demande comment sont conservees ses informations, comment exercer un droit lie a ses donnees ou comment signaler un traitement suspect, SIOU oriente vers la cellule protection des donnees.",
        "structure": "Cellule protection des donnees MTDI",
        "orientation_user": "Orienter vers donnees.personnelles@mtdi.test et eviter de collecter des details personnels dans la conversation.",
        "contact": "donnees.personnelles@mtdi.test.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Reponse attendue pour les questions de confidentialite.",
    },
    {
        "orientation": "portrait",
        "heading": "Evenement Benin IA Forum",
        "body": "Le Benin IA Forum est annonce comme un evenement de test consacre a l'intelligence artificielle publique. Il est prevu le 12 septembre 2026 a Cotonou, avec inscription via la cellule communication.",
        "structure": "Cellule communication MTDI",
        "orientation_user": "Pour une question sur un evenement IA en septembre 2026, orienter vers la cellule communication.",
        "contact": "communication@mtdi.test. Lieu: Palais des Congres de Cotonou.",
        "validity": "Evenement de test valable jusqu'au 12 septembre 2026.",
        "note": "Cette fiche permet de tester les questions quoi de neuf.",
    },
    {
        "orientation": "paysage",
        "heading": "Atelier cyberhygiene agents publics",
        "body": "Un atelier de cyberhygiene pour agents publics est programme le 5 octobre 2026. Il couvre mots de passe, phishing, protection des postes et signalement d'incident.",
        "structure": "Programme formation numerique MTDI",
        "orientation_user": "Orienter les agents publics interesses vers le programme de formation numerique.",
        "contact": "formation@mtdi.test. Inscription avant le 25 septembre 2026.",
        "validity": "Evenement de test valable jusqu'au 5 octobre 2026.",
        "note": "A utiliser pour les demandes de formation cyber.",
    },
    {
        "orientation": "portrait",
        "heading": "Journee portes ouvertes services numeriques",
        "body": "La journee portes ouvertes des services numeriques est prevue le 20 novembre 2026. Les usagers pourront rencontrer l'accueil MTDI, l'ADN, l'ASIN et le Guichet Startup.",
        "structure": "Cellule communication MTDI",
        "orientation_user": "Pour connaitre les services presents a la journee portes ouvertes, citer l'accueil MTDI, l'ADN, l'ASIN et le Guichet Startup.",
        "contact": "communication@mtdi.test. Lieu: Hall MTDI, Cotonou.",
        "validity": "Evenement de test valable jusqu'au 20 novembre 2026.",
        "note": "Evenement transversal utile pour les questions d'actualite.",
    },
    {
        "orientation": "paysage",
        "heading": "Signalement d'une reponse incorrecte",
        "body": "Lorsqu'une secretaire constate qu'une reponse SIOU est incorrecte, elle doit signaler la question, la reponse, le document source affiche et la correction proposee si elle la connait.",
        "structure": "Equipe support SIOU",
        "orientation_user": "Orienter vers support-siou@mtdi.test pour corriger la base de connaissances.",
        "contact": "support-siou@mtdi.test.",
        "validity": "Procedure permanente de test.",
        "note": "Le signalement nourrit la gouvernance documentaire.",
    },
    {
        "orientation": "portrait",
        "heading": "Demande vague d'un usager",
        "body": "Si l'usager dit seulement qu'il a un probleme avec le numerique, SIOU doit demander ou inferer la categorie: startup, cybersecurite, connectivite, donnees, plateforme publique ou rendez-vous.",
        "structure": "Accueil MTDI",
        "orientation_user": "Si la categorie n'est pas claire, orienter vers l'accueil MTDI pour qualification.",
        "contact": "accueil@mtdi.test. Telephone test: +229 01 90 00 10 10.",
        "validity": "Regle permanente de clarification.",
        "note": "L'agent IA peut demander une precision si les sources ne suffisent pas.",
    },
    {
        "orientation": "paysage",
        "heading": "Courrier officiel au ministere",
        "body": "Une demande d'audience, un courrier officiel ou une invitation institutionnelle doit etre transmise au Secretariat du cabinet, pas au support SIOU.",
        "structure": "Secretariat du cabinet MTDI",
        "orientation_user": "Orienter vers cabinet@mtdi.test avec l'objet du courrier et les coordonnees du demandeur.",
        "contact": "cabinet@mtdi.test. Bureau courrier MTDI.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Distingue orientation administrative et support applicatif.",
    },
    {
        "orientation": "portrait",
        "heading": "Publication d'une annonce officielle",
        "body": "Une demande de publication d'une annonce sur les canaux du ministere doit etre adressee a la cellule communication avec le texte, la date souhaitee et le responsable de validation.",
        "structure": "Cellule communication MTDI",
        "orientation_user": "Orienter vers communication@mtdi.test.",
        "contact": "communication@mtdi.test.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Fiche pour demandes media et annonces.",
    },
    {
        "orientation": "paysage",
        "heading": "Formation bureautique et services publics numeriques",
        "body": "Les agents publics qui souhaitent une formation aux outils bureautiques, aux demarches numeriques ou aux bonnes pratiques digitales doivent contacter le programme formation numerique.",
        "structure": "Programme formation numerique MTDI",
        "orientation_user": "Orienter vers formation@mtdi.test et demander le service d'origine de l'agent.",
        "contact": "formation@mtdi.test.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "Formation interne pour agents publics.",
    },
    {
        "orientation": "portrait",
        "heading": "Rendez-vous avec une direction",
        "body": "Pour obtenir un rendez-vous avec une direction, l'usager doit preciser le motif, la structure visee et un contact de rappel. SIOU indique le secretariat competent mais ne fixe pas le rendez-vous.",
        "structure": "Secretariat de la direction competente",
        "orientation_user": "Identifier d'abord la structure competente, puis orienter vers son secretariat.",
        "contact": "Accueil central: accueil@mtdi.test.",
        "validity": "Derniere revision: 18 juillet 2026.",
        "note": "L'agent IA oriente seulement.",
    },
    {
        "orientation": "paysage",
        "heading": "Demande hors documents",
        "body": "Si la question porte sur le passeport, le permis de conduire, les impots, une bourse universitaire ou une information qui n'est pas dans le corpus SIOU, l'assistant doit dire que l'information est absente des documents disponibles.",
        "structure": "Aucune structure SIOU confirmee",
        "orientation_user": "Ne pas inventer une orientation. Proposer de contacter l'accueil si la question touche le numerique.",
        "contact": "Accueil MTDI: accueil@mtdi.test.",
        "validity": "Regle permanente de refus.",
        "note": "Fiche piege pour tester l'absence de connaissance externe.",
    },
    {
        "orientation": "portrait",
        "heading": "Informations attendues dans une reponse",
        "body": "La reponse doit indiquer l'orientation pratique, la structure competente, le contact ou l'adresse si disponible, une information utile et le document source affiche par l'interface.",
        "structure": "Agent IA SIOU",
        "orientation_user": "Faire court: l'agent d'accueil doit comprendre la reponse en quelques secondes.",
        "contact": "La source est affichee par l'application.",
        "validity": "Regle de qualite V1.",
        "note": "Page de controle pour la forme des reponses.",
    },
    {
        "orientation": "paysage",
        "heading": "Canal de diffusion pilote",
        "body": "Le canal de diffusion pilote vise d'abord un usage interne au secretariat et a l'accueil. Une ouverture publique via portail vitrine pourra etre etudiee apres validation du corpus et de la gouvernance.",
        "structure": "Accueil MTDI et equipe projet SIOU",
        "orientation_user": "Pour la phase pilote, privilegier les usages de guichet et d'accueil.",
        "contact": "support-siou@mtdi.test.",
        "validity": "Decision pilote de test.",
        "note": "Explique pourquoi le chatbot doit etre efficace pour une secretaire.",
    },
    {
        "orientation": "portrait",
        "heading": "Priorite de reponse au guichet",
        "body": "Au guichet, la priorite est une reponse courte en moins de 15 secondes, lisible et directement exploitable. La citation du document renforce la confiance de la secretaire.",
        "structure": "Agent IA SIOU",
        "orientation_user": "Repondre rapidement, sans longs paragraphes techniques.",
        "contact": "Source documentaire obligatoire.",
        "validity": "Objectif d'experience V1.",
        "note": "Fiche issue du role principal de la secretaire.",
    },
    {
        "orientation": "paysage",
        "heading": "Synthese procedures et evenements",
        "body": "Ce document couvre le label Startup, la creation de startup, les incidents cyber, les abonnements internet, l'open data, la protection des donnees, les formations et les evenements IA de test.",
        "structure": "Corpus procedures et evenements SIOU",
        "orientation_user": "Utiliser ce document pour repondre aux questions comment faire, ou aller pour une procedure, ou quoi de neuf.",
        "contact": "Voir chaque fiche specifique.",
        "validity": "Corpus de test V1.",
        "note": "Synthese generale du second PDF.",
    },
]


def main() -> None:
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    build_pdf(
        "siou-annuaire-services-publics.pdf",
        "Annuaire d'orientation des services publics numeriques SIOU",
        "Corpus de test de 20 pages pour orienter les usagers vers les directions, agences, contacts et services competents.",
        ANNUAIRE,
    )
    build_pdf(
        "siou-procedures-evenements-numeriques.pdf",
        "Procedures et evenements numeriques SIOU",
        "Corpus de test de 20 pages pour repondre aux questions de demarches, incidents, formations et actualites numeriques.",
        PROCEDURES,
    )
    print("PDF metier SIOU crees dans backend/documents/")


if __name__ == "__main__":
    main()

