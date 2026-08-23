# -*- coding: utf-8 -*-
"""Guide d'utilisation BSE Medical System — niveau debutant complet."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, KeepTogether, ListFlowable)

# Chemins relatifs au script : le guide est regenere dans le depot, d'ou il est
# publie avec le site. Relancer apres toute evolution de l'application :
#     python tools-guide.py
REPO = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(REPO, "guide-bse-medical-system.pdf")

OR   = colors.HexColor("#a8800a")   # ocre lisible sur papier
ORC  = colors.HexColor("#c49708")
NOIR = colors.HexColor("#1b1b19")
GRIS = colors.HexColor("#5d5d58")
GRISC= colors.HexColor("#e7e6e0")
CREME= colors.HexColor("#faf9f5")
ROUGE= colors.HexColor("#c0392b")
ORANG= colors.HexColor("#c8701a")
VERT = colors.HexColor("#3f7a4c")
BLEU = colors.HexColor("#4a7290")
VIOL = colors.HexColor("#6f4f96")
DECES= colors.HexColor("#4a4a46")

def st(nom, **kw):
    base = dict(name=nom, fontName="Helvetica", fontSize=10.2, leading=15.2,
                textColor=NOIR, alignment=TA_LEFT, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(**base)

S = {
    "titre":    st("titre", fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=colors.white, alignment=TA_CENTER, spaceAfter=4),
    "stitre":   st("stitre", fontSize=11, leading=15, textColor=ORC, alignment=TA_CENTER, spaceAfter=0),
    "h1":       st("h1", fontName="Helvetica-Bold", fontSize=16.5, leading=20, textColor=NOIR, spaceAfter=3, spaceBefore=0),
    "h1num":    st("h1num", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=OR, spaceAfter=1),
    "h2":       st("h2", fontName="Helvetica-Bold", fontSize=11.6, leading=15, textColor=NOIR, spaceBefore=9, spaceAfter=3),
    "p":        st("p"),
    "pc":       st("pc", alignment=TA_CENTER),
    "petit":    st("petit", fontSize=8.8, leading=12.4, textColor=GRIS),
    "puce":     st("puce", spaceAfter=3),
    "encadre":  st("encadre", fontSize=9.6, leading=13.8),
    "cell":     st("cell", fontSize=9.2, leading=12.6, spaceAfter=0),
    "cellb":    st("cellb", fontName="Helvetica-Bold", fontSize=9.2, leading=12.6, spaceAfter=0),
    "cellblanc":st("cellblanc", fontName="Helvetica-Bold", fontSize=9.2, leading=12.6, textColor=colors.white, spaceAfter=0),
    "somm":     st("somm", fontSize=10.5, leading=17, spaceAfter=0),
}

def P(txt, s="p"): return Paragraph(txt, S[s])

def puces(items, style="puce"):
    return ListFlowable([Paragraph(i, S[style]) for i in items],
                        bulletType="bullet", start="\u2022", leftIndent=13,
                        bulletFontSize=8, bulletOffsetY=1, spaceAfter=6)

def encadre(titre, corps, coul=ORC, fond=colors.HexColor("#fdf7e3")):
    inner = [Paragraph(titre, ParagraphStyle("bt", parent=S["encadre"], fontName="Helvetica-Bold",
                                             textColor=coul, spaceAfter=3))]
    for c in ([corps] if isinstance(corps, str) else corps):
        inner.append(Paragraph(c, S["encadre"]))
    t = Table([[inner]], colWidths=[163*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), fond),
        ("LINEBEFORE", (0,0), (0,-1), 2.4, coul),
        ("BOX", (0,0), (-1,-1), 0.4, colors.HexColor("#e3ddc4")),
        ("LEFTPADDING", (0,0), (-1,-1), 9), ("RIGHTPADDING", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    return t

def tableau(donnees, largeurs, entete=True, tailles=None):
    t = Table(donnees, colWidths=largeurs, repeatRows=1 if entete else 0)
    style = [
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.4, GRISC),
        ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 5.5), ("BOTTOMPADDING", (0,0), (-1,-1), 5.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CREME]),
    ]
    if entete:
        style += [("BACKGROUND", (0,0), (-1,0), NOIR)]
    t.setStyle(TableStyle(style))
    return t

def etapes(liste):
    """Suite d'etapes numerotees, avec la pastille ocre."""
    lignes = []
    for i, (t, d) in enumerate(liste, 1):
        pastille = Table([[Paragraph(f'<font color="white"><b>{i}</b></font>', S["cell"])]],
                         colWidths=[7.6*mm], rowHeights=[7.6*mm])
        pastille.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), OR),
                                      ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                      ("ALIGN", (0,0), (-1,-1), "CENTER"),
                                      ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0),
                                      ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
        txt = [Paragraph(f"<b>{t}</b>", S["cell"])]
        if d: txt.append(Paragraph(d, ParagraphStyle("d", parent=S["cell"], textColor=GRIS, spaceBefore=2)))
        lignes.append([pastille, txt])
    t = Table(lignes, colWidths=[11*mm, 152*mm])
    t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                           ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 4),
                           ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    return t

def maquette_fiche():
    """Reproduction schematique de la fiche de triage, pour la decortiquer."""
    l = []
    def ligne(etiq, val, coul=NOIR, gras=False, fond=colors.white):
        hexa = "#" + coul.hexval()[2:]
        return [Paragraph(f'<font size="7" color="#8a8a84">{etiq}</font>', S["cell"]),
                Paragraph(f'<font color="{hexa}">{"<b>" if gras else ""}{val}{"</b>" if gras else ""}</font>', S["cell"])]
    donnees = [
        [Paragraph('<font size="7" color="#8a8a84">FICHE DE TRIAGE</font>', S["cell"]),
         Paragraph('<font size="8" color="white"><b> CRITIQUE </b></font>', S["cell"])],
        ligne("", "H&Eacute;MORRAGIE INTERNE", NOIR, True),
        ligne("ZONE TOUCH&Eacute;E", "Torse"),
        ligne("PROTECTION", "Plaques balistiques port&eacute;es : NON", OR),
        ligne("BILAN", "Blessure perforante &agrave; l'abdomen causant<br/>une importante h&eacute;morragie interne."),
        ligne("PROTOCOLE DE SOIN", "Bandage + Poche de transfusion<br/>+ &Eacute;pin&eacute;phrine", NOIR, True),
    ]
    t = Table(donnees, colWidths=[34*mm, 100*mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f2f1ec")),
        ("BACKGROUND", (1,0), (1,0), ROUGE),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("BOX", (0,0), (-1,-1), 0.7, colors.HexColor("#cfcec7")),
        ("LINEABOVE", (0,0), (-1,0), 2.6, ROUGE),
        ("LINEBELOW", (0,0), (-1,0), 0.4, colors.HexColor("#cfcec7")),
        ("INNERGRID", (0,1), (-1,-1), 0.3, colors.HexColor("#eceae3")),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return t

# ---------------------------------------------------------------- document
class Doc(BaseDocTemplate):
    def __init__(self, chemin, **kw):
        BaseDocTemplate.__init__(self, chemin, pagesize=A4,
                                 leftMargin=23*mm, rightMargin=23*mm,
                                 topMargin=22*mm, bottomMargin=20*mm, **kw)
        cadre = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="n")
        self.addPageTemplates([
            PageTemplate(id="couv", frames=[Frame(0, 0, A4[0], A4[1], id="c")], onPage=self.fond_couv),
            PageTemplate(id="std", frames=[cadre], onPage=self.deco),
        ])
    def fond_couv(self, c, d):
        c.setFillColor(NOIR); c.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        c.setFillColor(ORC); c.rect(0, A4[1]-6*mm, A4[0], 6*mm, fill=1, stroke=0)
        c.setStrokeColor(ORC); c.setLineWidth(0.6)
        c.rect(14*mm, 14*mm, A4[0]-28*mm, A4[1]-28*mm, fill=0, stroke=1)
    def deco(self, c, d):
        c.setFillColor(ORC); c.rect(0, A4[1]-4.5*mm, A4[0], 4.5*mm, fill=1, stroke=0)
        c.setFont("Helvetica", 7.4); c.setFillColor(GRIS)
        c.drawString(23*mm, A4[1]-11*mm, "BSE MEDICAL SYSTEM  //  GUIDE D'UTILISATION")
        c.setStrokeColor(GRISC); c.setLineWidth(0.4)
        c.line(23*mm, A4[1]-13.5*mm, A4[0]-23*mm, A4[1]-13.5*mm)
        c.line(23*mm, 15*mm, A4[0]-23*mm, 15*mm)
        c.setFont("Helvetica", 7.6); c.setFillColor(GRIS)
        c.drawString(23*mm, 11*mm, "Bravo Sierra Events")
        c.setFont("Helvetica-Bold", 8.4); c.setFillColor(NOIR)
        c.drawRightString(A4[0]-23*mm, 11*mm, str(c.getPageNumber() - 1))

def chapitre(num, titre):
    return KeepTogether([Spacer(1, 2*mm),
                         P(f"CHAPITRE {num}", "h1num"), P(titre, "h1"),
                         Table([[""]], colWidths=[163*mm], rowHeights=[1.6],
                               style=TableStyle([("BACKGROUND", (0,0), (-1,-1), ORC)])),
                         Spacer(1, 4*mm)])

# ---------------------------------------------------------------- contenu
h = []

# --- Couverture
h.append(Spacer(1, 52*mm))
logo = os.path.join(REPO, "icons", "logo-bse@2x.png")
if os.path.exists(logo):
    im = Image(logo); r = im.imageWidth / im.imageHeight
    im.drawHeight = 34*mm; im.drawWidth = 34*mm*r; im.hAlign = "CENTER"
    h += [im, Spacer(1, 14*mm)]
h.append(P("BSE MEDICAL SYSTEM", "titre"))
h.append(Spacer(1, 3*mm))
h.append(P("FRONTLINE  //  FIELD APPLICATION", "stitre"))
h.append(Spacer(1, 22*mm))
bandeau = Table([[Paragraph('<font color="white" size="15"><b>Guide d\'utilisation</b></font>', S["pc"])]],
                colWidths=[110*mm])
bandeau.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#2a2a26")),
                             ("BOX", (0,0), (-1,-1), 0.7, ORC),
                             ("ALIGN", (0,0), (-1,-1), "CENTER"),
                             ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9)]))
bandeau.hAlign = "CENTER"
h += [bandeau, Spacer(1, 9*mm)]
h.append(Paragraph('<font color="#9b9b96" size="10.5">Pour d&eacute;couvrir l\'application, sans rien conna&icirc;tre au d&eacute;part</font>', S["pc"]))
h.append(Spacer(1, 45*mm))
h.append(Paragraph('<font color="#c49708" size="9">https://project-bsm-7d32c.web.app</font>', S["pc"]))
h.append(PageBreak())

# --- Sommaire
h.append(P("Sommaire", "h1"))
h.append(Table([[""]], colWidths=[163*mm], rowHeights=[1.6],
               style=TableStyle([("BACKGROUND", (0,0), (-1,-1), ORC)])))
h.append(Spacer(1, 6*mm))
somm = [
    ("1", "&Agrave; quoi sert cette application", "2"),
    ("2", "Installer l'application sur votre t&eacute;l&eacute;phone", "3"),
    ("3", "Votre premier diagnostic", "4"),
    ("4", "Lire une fiche de triage", "5"),
    ("5", "Les niveaux de gravit&eacute;", "6"),
    ("6", "Les modes de jeu", "7"),
    ("7", "Le mode Extr&ecirc;me en d&eacute;tail", "8"),
    ("8", "Les r&eacute;glages", "9"),
    ("9", "Cr&eacute;er vos propres paquets de cartes", "11"),
    ("10", "Jouer &agrave; plusieurs : l'organisateur", "12"),
    ("11", "Jouer &agrave; plusieurs : le joueur", "14"),
    ("12", "Le QG, onglet par onglet", "15"),
    ("13", "Sur le terrain : conseils pratiques", "16"),
    ("14", "En cas de probl&egrave;me", "17"),
]
lignes = [[Paragraph(f'<font color="#a8800a"><b>{n}</b></font>', S["somm"]),
           Paragraph(t, S["somm"]),
           Paragraph(f'<font color="#5d5d58">{p}</font>', S["somm"])] for n, t, p in somm]
ts = Table(lignes, colWidths=[10*mm, 140*mm, 13*mm])
ts.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                        ("ALIGN", (2,0), (2,-1), "RIGHT"),
                        ("LINEBELOW", (0,0), (-1,-2), 0.3, GRISC),
                        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                        ("LEFTPADDING", (0,0), (-1,-1), 0)]))
h += [ts, Spacer(1, 10*mm)]
h.append(encadre("&Agrave; qui s'adresse ce guide",
    "Vous n'avez jamais ouvert l'application&nbsp;? Vous &ecirc;tes exactement la bonne personne. "
    "Ce guide part de z&eacute;ro et n'attend aucune connaissance pr&eacute;alable, ni en airsoft m&eacute;dical, "
    "ni en informatique. Lisez les chapitres 1 &agrave; 5 pour jouer d&egrave;s cet apr&egrave;s-midi&nbsp;; "
    "le reste vous servira quand vous voudrez organiser une partie."))
h.append(PageBreak())

# --- Ch 1
h.append(chapitre(1, "&Agrave; quoi sert cette application"))
h.append(P("BSE Medical System remplace le jeu de cartes papier que les m&eacute;dics d'airsoft trimballent "
           "dans leur poche. Quand un joueur est touch&eacute;, le m&eacute;dic sort son t&eacute;l&eacute;phone, "
           "appuie sur un bouton, et l'application tire une blessure au hasard avec le protocole de soin "
           "correspondant."))
h.append(P("Fini les cartes mouill&eacute;es, perdues ou m&eacute;lang&eacute;es. Et surtout&nbsp;: "
           "l'organisateur peut d&eacute;cider &agrave; distance de ce que chaque &eacute;quipe va tirer."))
h.append(Spacer(1, 3*mm))
h.append(P("Le principe, en quatre temps", "h2"))
h.append(etapes([
    ("Un joueur est touch&eacute;", "Il se met au sol et appelle un m&eacute;dic."),
    ("Le m&eacute;dic arrive et ouvre l'application", "Il appuie sur le gros bouton rond au centre de l'&eacute;cran."),
    ("L'application tire une blessure", "Une fiche appara&icirc;t&nbsp;: la zone touch&eacute;e, la gravit&eacute;, et les soins &agrave; appliquer."),
    ("Le m&eacute;dic applique le protocole", "Garrot, bandage, attelle... selon ce qu'indique la fiche. Le bless&eacute; repart ensuite."),
]))
h.append(Spacer(1, 2*mm))
h.append(encadre("Le mat&eacute;riel reste bien r&eacute;el",
    "L'application ne remplace pas votre trousse. Elle vous dit <b>quoi faire</b>&nbsp;; c'est &agrave; vous "
    "de poser le vrai garrot factice et le vrai bandage. Si un type de soin n'est pas disponible sur "
    "l'&eacute;v&eacute;nement &mdash; personne n'a de pansement 3 c&ocirc;t&eacute;s, par exemple &mdash; "
    "l'organisateur le retire du jeu <b>avant</b> la partie, et les blessures qui l'exigent ne sortent plus."))
h.append(PageBreak())

# --- Ch 2
h.append(chapitre(2, "Installer l'application sur votre t&eacute;l&eacute;phone"))
h.append(P("Il n'y a rien &agrave; t&eacute;l&eacute;charger sur un magasin d'applications. Tout passe par "
           "votre navigateur habituel."))
h.append(etapes([
    ("Ouvrez l'adresse dans votre navigateur",
     "<b>https://project-bsm-7d32c.web.app</b> &mdash; Chrome sur Android, Safari sur iPhone."),
    ("Ajoutez l'application &agrave; votre &eacute;cran d'accueil",
     "Sur <b>Android</b>&nbsp;: menu &laquo;&nbsp;trois points&nbsp;&raquo; puis &laquo;&nbsp;Installer l'application&nbsp;&raquo; "
     "ou &laquo;&nbsp;Ajouter &agrave; l'&eacute;cran d'accueil&nbsp;&raquo;.<br/>"
     "Sur <b>iPhone</b>&nbsp;: bouton Partager (le carr&eacute; avec la fl&egrave;che) puis &laquo;&nbsp;Sur l'&eacute;cran d'accueil&nbsp;&raquo;."),
    ("Lancez-la depuis l'ic&ocirc;ne",
     "Une croix m&eacute;dicale dor&eacute;e sur fond noir appara&icirc;t avec vos autres applications. "
     "Elle s'ouvre en plein &eacute;cran, sans barre d'adresse."),
]))
h.append(Spacer(1, 2*mm))
h.append(encadre("&Agrave; faire au briefing, pas sur le terrain",
    ["Chaque t&eacute;l&eacute;phone doit ouvrir l'application <b>une fois avec du r&eacute;seau</b>. "
     "L'application se met alors enti&egrave;rement en m&eacute;moire sur l'appareil.",
     "Une fois cette premi&egrave;re ouverture faite, elle fonctionne <b>sans aucun r&eacute;seau</b>&nbsp;: "
     "vous pouvez tirer des blessures en plein bois, en mode avion. Seul le jeu &agrave; plusieurs "
     "demande une connexion."],
    coul=ROUGE, fond=colors.HexColor("#fdf1ef")))
h.append(Spacer(1, 3*mm))
h.append(P("Ce que vous voyez en arrivant", "h2"))
h.append(P("L'&eacute;cran d'accueil s'appelle <b>DIAGNOSTIC M&Eacute;DICAL</b>. On y trouve&nbsp;:"))
h.append(puces([
    "un ou plusieurs <b>gros boutons ronds</b> au centre&nbsp;: ce sont vos tirages disponibles&nbsp;;",
    "un bandeau <b>PAQUET ACTIF</b> en bas, qui indique combien de cartes sont en jeu&nbsp;;",
    "en haut &agrave; droite, trois boutons&nbsp;: <b>multijoueur</b>, <b>mes paquets</b> et <b>r&eacute;glages</b>&nbsp;;",
    "en haut, un bandeau gris avec votre pseudo et votre &eacute;quipe.",
]))
h.append(PageBreak())

# --- Ch 3
h.append(chapitre(3, "Votre premier diagnostic"))
h.append(P("C'est l'usage principal de l'application, et le plus simple."))
h.append(etapes([
    ("Appuyez sur le bouton rond", "Le plus courant s'appelle <b>BALISTIQUE</b>&nbsp;: c'est une blessure par tir."),
    ("Attendez l'analyse", "Un bilan <b>MARCH</b> d&eacute;file pendant quelques secondes. C'est le temps du diagnostic, "
     "profitez-en pour observer le bless&eacute;."),
    ("Lisez la fiche", "Elle indique la gravit&eacute;, la zone touch&eacute;e et le protocole &agrave; appliquer."),
    ("Appliquez les soins, puis appuyez sur &laquo;&nbsp;Nouveau diagnostic&nbsp;&raquo;",
     "Vous revenez &agrave; l'accueil, pr&ecirc;t pour le bless&eacute; suivant."),
]))
h.append(Spacer(1, 2*mm))
h.append(P("Que veut dire MARCH&nbsp;?", "h2"))
h.append(P("C'est l'ordre dans lequel un secouriste examine un bless&eacute;, du plus mortel au moins urgent. "
           "L'application l'affiche pour vous mettre dans le bain&nbsp;:"))
march = [[Paragraph(f'<font color="#a8800a"><b>{l}</b></font>', S["cellb"]), Paragraph(t, S["cell"])]
         for l, t in [("M", "<b>Massive bleeding</b> &mdash; les h&eacute;morragies massives d'abord"),
                      ("A", "<b>Airways</b> &mdash; les voies respiratoires"),
                      ("R", "<b>Respiration</b> &mdash; la ventilation"),
                      ("C", "<b>Circulation</b> &mdash; le pouls, le choc"),
                      ("H", "<b>Head / Hypothermia</b> &mdash; la t&ecirc;te et le refroidissement")]]
tm = Table(march, colWidths=[10*mm, 153*mm])
tm.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0),
                        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3)]))
h += [tm, Spacer(1, 4*mm)]
h.append(encadre("L'&eacute;cran reste allum&eacute;",
    "Tant qu'une fiche est affich&eacute;e, le t&eacute;l&eacute;phone ne se verrouille pas. Vous pouvez le poser "
    "pour soigner &agrave; deux mains&nbsp;: le protocole sera toujours l&agrave; quand vous le reprendrez."))
h.append(PageBreak())

# --- Ch 4
h.append(chapitre(4, "Lire une fiche de triage"))
h.append(P("Toutes les fiches sont b&acirc;ties de la m&ecirc;me fa&ccedil;on. Voici &agrave; quoi ressemble "
           "une fiche compl&egrave;te&nbsp;:"))
h.append(Spacer(1, 2*mm))
h.append(maquette_fiche())
h.append(Spacer(1, 5*mm))
h.append(P("Chaque partie, une par une", "h2"))
h.append(tableau([
    [Paragraph("Zone de la fiche", S["cellblanc"]), Paragraph("Ce que &ccedil;a veut dire", S["cellblanc"])],
    [Paragraph("<b>Badge de gravit&eacute;</b>", S["cell"]), Paragraph("En haut &agrave; droite, color&eacute;. Il donne d'un coup d'&oelig;il l'urgence de la situation. Le liser&eacute; du haut de la fiche a la m&ecirc;me couleur.", S["cell"])],
    [Paragraph("<b>Titre</b>", S["cell"]), Paragraph("Le nom court de la blessure, en gros caract&egrave;res.", S["cell"])],
    [Paragraph("<b>Zone touch&eacute;e</b>", S["cell"]), Paragraph("O&ugrave; le bless&eacute; est atteint&nbsp;: t&ecirc;te, torse, bras gauche, jambe droite...", S["cell"])],
    [Paragraph("<b>Protection</b>", S["cell"]), Paragraph("N'appara&icirc;t qu'en mode Extr&ecirc;me. Rappelle si le bless&eacute; portait un casque ou des plaques.", S["cell"])],
    [Paragraph("<b>Bilan</b>", S["cell"]), Paragraph("La description de la blessure, &agrave; lire &agrave; voix haute au bless&eacute; pour le r&ocirc;le-play.", S["cell"])],
    [Paragraph("<b>Protocole de soin</b>", S["cell"]), Paragraph("<b>La partie la plus importante</b>&nbsp;: exactement ce que vous devez faire.", S["cell"])],
], [38*mm, 125*mm]))
h.append(Spacer(1, 4*mm))
h.append(encadre("Attention au compte &agrave; rebours",
    ["Si l'organisateur a activ&eacute; l'option hardcore, certaines blessures d&eacute;clenchent un "
     "<b>bip r&eacute;gulier</b> et un bandeau rouge <b>H&Eacute;MORRAGIE ACTIVE</b>.",
     "Vous avez alors un temps limit&eacute; pour appliquer les soins et appuyer sur "
     "<b>SOINS EFFECTU&Eacute;S</b>. Si le temps s'&eacute;coule, le bless&eacute; meurt&nbsp;: l'&eacute;cran "
     "devient noir et le bip se transforme en son continu."],
    coul=ROUGE, fond=colors.HexColor("#fdf1ef")))
h.append(PageBreak())

# --- Ch 5
h.append(chapitre(5, "Les niveaux de gravit&eacute;"))
h.append(P("Cinq niveaux, toujours les m&ecirc;mes, avec un code couleur constant dans toute l'application."))
h.append(Spacer(1, 2*mm))
def pastille(txt, coul):
    t = Table([[Paragraph(f'<font color="white" size="9"><b>{txt}</b></font>', S["cell"])]], colWidths=[24*mm])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), coul), ("ALIGN", (0,0), (-1,-1), "CENTER"),
                           ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
    return t
h.append(tableau([
    [Paragraph("Gravit&eacute;", S["cellblanc"]), Paragraph("Ce que cela signifie pour le m&eacute;dic", S["cellblanc"])],
    [pastille("D&Eacute;C&Egrave;S", DECES), Paragraph("Rien &agrave; faire. Le joueur est mort, il repart au point de r&eacute;apparition.", S["cell"])],
    [pastille("CRITIQUE", ROUGE), Paragraph("Urgence vitale. C'est sur ces blessures que le compte &agrave; rebours se d&eacute;clenche, si l'option est active.", S["cell"])],
    [pastille("GRAVE", ORANG), Paragraph("S&eacute;rieux mais stable. Prenez le temps de bien appliquer le protocole.", S["cell"])],
    [pastille("L&Eacute;G&Egrave;RE", VERT), Paragraph("Bobologie. Un bandage et le joueur repart.", S["cell"])],
    [pastille("SP&Eacute;CIAL", VIOL), Paragraph("Cas particulier, souvent li&eacute; &agrave; une protection. Lisez bien le protocole&nbsp;: il d&eacute;pend du port du casque ou du gilet.", S["cell"])],
], [30*mm, 133*mm]))
h.append(Spacer(1, 5*mm))
h.append(P("Pourquoi certaines blessures sortent plus souvent", "h2"))
h.append(P("Chaque carte poss&egrave;de une <b>quantit&eacute;</b>, comme s'il y avait plusieurs exemplaires "
           "de la m&ecirc;me carte dans le paquet. Une carte en 4 exemplaires sortira deux fois plus souvent "
           "qu'une carte en 2 exemplaires. L'organisateur r&egrave;gle ces quantit&eacute;s pour donner "
           "le ton de sa partie&nbsp;: plus de bobologie, ou plus d'urgences vitales."))
h.append(PageBreak())

# --- Ch 6
h.append(chapitre(6, "Les modes de jeu"))
h.append(P("Le mode d&eacute;termine quel jeu de cartes est utilis&eacute;. On le choisit dans les "
           "<b>R&eacute;glages</b>, ou l'organisateur l'impose en partie."))
h.append(Spacer(1, 2*mm))
h.append(tableau([
    [Paragraph("Mode", S["cellblanc"]), Paragraph("Cartes", S["cellblanc"]), Paragraph("Pour qui", S["cellblanc"])],
    [Paragraph("<b>Classique</b>", S["cell"]), Paragraph("8", S["cell"]),
     Paragraph("Les d&eacute;butants. Soins simples&nbsp;: garrot, bandage, attelle. Id&eacute;al pour une premi&egrave;re partie.", S["cell"])],
    [Paragraph("<b>Avanc&eacute;</b>", S["cell"]), Paragraph("10", S["cell"]),
     Paragraph("Les habitu&eacute;s. Protocoles plus longs, morphine et &eacute;pin&eacute;phrine entrent en jeu.", S["cell"])],
    [Paragraph("<b>Extr&ecirc;me</b>", S["cell"]), Paragraph("17", S["cell"]),
     Paragraph("Le plus r&eacute;aliste. Vous d&eacute;signez la zone touch&eacute;e sur une silhouette, et les blessures en d&eacute;coulent. Voir le chapitre suivant.", S["cell"])],
    [Paragraph("<b>Explosion</b>", S["cell"]), Paragraph("14", S["cell"]),
     Paragraph("Un paquet <b>en plus</b>, pour les grenades et les explosifs. Il ajoute un second bouton rond sur l'accueil.", S["cell"])],
], [30*mm, 18*mm, 115*mm]))
h.append(Spacer(1, 5*mm))
h.append(P("Le cas particulier de l'explosion", "h2"))
h.append(P("Le paquet Explosion contient les blessures par souffle et par &eacute;clats. Il s'active dans les "
           "R&eacute;glages, en mode Avanc&eacute; ou Extr&ecirc;me, et fait appara&icirc;tre un bouton "
           "<b>EXPLOSION</b> orange &agrave; c&ocirc;t&eacute; du bouton Balistique."))
h.append(encadre("Une explosion ne respecte pas les protections",
    "C'est voulu&nbsp;: contrairement aux blessures par tir, une carte explosion peut tuer un joueur "
    "<b>m&ecirc;me s'il porte un casque et des plaques</b>. Un souffle traverse la protection. "
    "Ne cherchez pas l'erreur, c'est la r&egrave;gle du jeu."))
h.append(PageBreak())

# --- Ch 7
h.append(chapitre(7, "Le mode Extr&ecirc;me en d&eacute;tail"))
h.append(P("C'est le mode le plus immersif, et le seul o&ugrave; <b>vous</b> d&eacute;cidez de la zone touch&eacute;e "
           "au lieu de la laisser au hasard."))
h.append(etapes([
    ("Appuyez sur le bouton de tirage", "Au lieu de la fiche, une <b>silhouette humaine</b> appara&icirc;t."),
    ("Touchez la zone o&ugrave; le joueur a &eacute;t&eacute; atteint",
     "T&ecirc;te, torse, bras ou jambe. <b>La vue est en miroir</b>&nbsp;: le bras droit du bless&eacute; "
     "est &agrave; votre gauche sur l'&eacute;cran, comme si vous lui faisiez face."),
    ("R&eacute;pondez &agrave; la question de protection",
     "Pour la t&ecirc;te&nbsp;: &laquo;&nbsp;Casque balistique port&eacute;&nbsp;?&nbsp;&raquo;. Pour le torse&nbsp;: "
     "&laquo;&nbsp;Gilet pare-balles port&eacute;&nbsp;?&nbsp;&raquo;. Regardez le bless&eacute; et r&eacute;pondez honn&ecirc;tement."),
    ("La fiche s'affiche", "Elle ne contient que des blessures coh&eacute;rentes avec la zone <b>et</b> avec votre r&eacute;ponse."),
]))
h.append(Spacer(1, 2*mm))
h.append(P("Pourquoi la question de protection change tout", "h2"))
h.append(P("La r&eacute;ponse filtre r&eacute;ellement les cartes disponibles. Un joueur casqu&eacute; ne peut "
           "pas tirer &laquo;&nbsp;Tir direct &agrave; la t&ecirc;te (sans casque)&nbsp;&raquo;&nbsp;:"))
h.append(Spacer(1, 1*mm))
h.append(tableau([
    [Paragraph("Zone touch&eacute;e", S["cellblanc"]), Paragraph("Protection port&eacute;e", S["cellblanc"]), Paragraph("Sans protection", S["cellblanc"])],
    [Paragraph("<b>T&ecirc;te</b>", S["cell"]),
     Paragraph("Impact sur casque<br/><font size='8' color='#5d5d58'>Repos 2 minutes</font>", S["cell"]),
     Paragraph("Plaie au front, traumatisme cr&acirc;nien, <b>ou tir mortel</b>", S["cell"])],
    [Paragraph("<b>Torse</b>", S["cell"]),
     Paragraph("Impact sur plaque, &eacute;raflure au flanc, c&ocirc;tes fractur&eacute;es", S["cell"]),
     Paragraph("Pneumothorax, h&eacute;morragie interne, <b>ou tir vital</b>", S["cell"])],
    [Paragraph("<b>Bras / Jambe</b>", S["cell"]),
     Paragraph("<font color='#5d5d58'>Question non pos&eacute;e</font>", S["cell"]),
     Paragraph("Blessures propres au membre&nbsp;: une fracture du f&eacute;mur ne peut pas sortir sur un bras.", S["cell"])],
], [30*mm, 62*mm, 71*mm]))
h.append(Spacer(1, 4*mm))
h.append(encadre("La morale du mode Extr&ecirc;me",
    "Porter un casque et des plaques vous sauve r&eacute;ellement la vie dans ce mode. C'est le meilleur "
    "argument pour convaincre vos joueurs de s'&eacute;quiper correctement."))
h.append(PageBreak())

# --- Ch 8
h.append(chapitre(8, "Les r&eacute;glages"))
h.append(P("On y acc&egrave;de par le bouton <b>curseurs</b>, en haut &agrave; droite de l'&eacute;cran. "
           "Pensez &agrave; appuyer sur <b>VALIDER</b> en bas pour conserver vos changements&nbsp;; "
           "<b>ANNULER</b> remet tout comme avant."))
h.append(Spacer(1, 2*mm))
h.append(P("Profil multijoueur", "h2"))
h.append(P("Votre <b>pseudo</b>. C'est le nom sous lequel l'organisateur vous verra. Mettez-le avant de "
           "rejoindre une partie&nbsp;: c'est plus simple pour tout le monde."))
h.append(P("Mode de jeu", "h2"))
h.append(P("Classique, Avanc&eacute;, Extr&ecirc;me, ou l'un de vos paquets personnels. En partie, ce r&eacute;glage "
           "est verrouill&eacute;&nbsp;: c'est l'organisateur qui d&eacute;cide."))
h.append(P("Option hardcore : le risque de mort", "h2"))
h.append(P("Une fois coch&eacute;e, quatre r&eacute;glages apparaissent&nbsp;:"))
h.append(tableau([
    [Paragraph("R&eacute;glage", S["cellblanc"]), Paragraph("Effet", S["cellblanc"])],
    [Paragraph("<b>Probabilit&eacute;</b>", S["cell"]), Paragraph("Les chances qu'une blessure d&eacute;clenche le compte &agrave; rebours. 40&nbsp;% par d&eacute;faut&nbsp;: environ une blessure critique sur deux.", S["cell"])],
    [Paragraph("<b>D&eacute;lai mini</b>", S["cell"]), Paragraph("Le temps le plus court dont dispose le m&eacute;dic. 30 secondes par d&eacute;faut.", S["cell"])],
    [Paragraph("<b>D&eacute;lai maxi</b>", S["cell"]), Paragraph("Le temps le plus long. 60 secondes par d&eacute;faut. Le d&eacute;lai r&eacute;el est tir&eacute; au hasard entre les deux, et le m&eacute;dic ne le voit pas.", S["cell"])],
    [Paragraph("<b>&Eacute;tendre aux Graves</b>", S["cell"]), Paragraph("Par d&eacute;faut, seules les blessures Critiques peuvent tuer. Cochez pour durcir nettement la partie.", S["cell"])],
], [32*mm, 131*mm]))
h.append(PageBreak())

h.append(P("Mat&eacute;riel requis", "h2"))
h.append(P("Cette liste ne suit pas le contenu de votre trousse au fil de la partie. Elle d&eacute;finit "
           "<b>quels types de soins sont en jeu</b>&nbsp;: on d&eacute;coche le mat&eacute;riel dont on ne dispose "
           "pas, et l'application cesse de tirer les blessures qui l'exigent."))
h.append(P("C'est un r&eacute;glage de <b>pr&eacute;paration</b>, pas un r&eacute;glage de terrain&nbsp;: il se fait "
           "avant la partie, et normalement par l'organisateur."))
h.append(encadre("Un joueur ne retire pas de cartes du jeu",
    ["En partie, vos r&eacute;glages sont <b>verrouill&eacute;s</b>&nbsp;: c'est l'organisateur qui d&eacute;cide du "
     "mat&eacute;riel et des quantit&eacute;s, pour que tous les m&eacute;dics jouent le m&ecirc;me paquet. "
     "Vous ne pouvez donc pas &eacute;carter une blessure parce qu'elle vous arrange mal.",
     "En solo, en revanche, vous configurez librement votre propre jeu.",
     "<b>Exemple.</b> Aucun m&eacute;dic de l'&eacute;v&eacute;nement n'a de pansement 3 c&ocirc;t&eacute;s&nbsp;? "
     "L'organisateur d&eacute;coche ce mat&eacute;riel avant la partie&nbsp;: la plaie soufflante et le "
     "pneumothorax disparaissent du paquet pour tout le monde."]))
h.append(Spacer(1, 3*mm))
h.append(P("Cartes actives", "h2"))
h.append(P("La liste compl&egrave;te des blessures du mode, <b>tri&eacute;es par gravit&eacute;</b>&nbsp;: "
           "d&eacute;c&egrave;s d'abord, puis critiques, graves, l&eacute;g&egrave;res et sp&eacute;ciales. Pour chaque carte&nbsp;:"))
h.append(puces([
    "l'&oelig;il ouvre le <b>catalogue</b> et vous montre la carte en entier&nbsp;;",
    "les boutons <b>&ndash;</b> et <b>+</b> r&egrave;glent sa quantit&eacute; dans le paquet&nbsp;;",
    "le <b>pourcentage</b> &agrave; droite indique ses chances de sortir. Il se met &agrave; jour tout seul&nbsp;;",
    "une ligne <b>gris&eacute;e</b> signifie que le mat&eacute;riel manque&nbsp;: cette carte ne sortira pas.",
]))
h.append(Spacer(1, 2*mm))
h.append(encadre("R&eacute;gler une carte &agrave; z&eacute;ro",
    "Mettre la quantit&eacute; &agrave; 0 retire compl&egrave;tement la carte du paquet. C'est la fa&ccedil;on "
    "propre d'&eacute;carter une blessure qui ne vous pla&icirc;t pas, sans toucher au reste."))
h.append(PageBreak())

# --- Ch 9
h.append(chapitre(9, "Cr&eacute;er vos propres paquets de cartes"))
h.append(P("Le bouton <b>crayon</b> en haut &agrave; droite ouvre &laquo;&nbsp;Mes paquets&nbsp;&raquo;. "
           "Vous pouvez y b&acirc;tir vos propres blessures&nbsp;: contamination chimique, radiations, "
           "morsures, ce que votre sc&eacute;nario demande."))
h.append(etapes([
    ("Cr&eacute;er un paquet", "Donnez-lui un nom. Cochez <b>Afficher sur l'accueil</b> pour qu'il ait son propre bouton rond."),
    ("Ajouter des cartes", "Pour chacune&nbsp;: une gravit&eacute;, un titre, une zone, un protocole de soin."),
    ("Choisir le mat&eacute;riel requis", "Touchez les puces correspondantes. Vous pouvez cr&eacute;er du mat&eacute;riel "
     "qui n'existe pas dans la liste de base &mdash; &laquo;&nbsp;Anti-rad&nbsp;&raquo;, &laquo;&nbsp;S&eacute;rum&nbsp;&raquo;..."),
    ("Enregistrer", "Le paquet appara&icirc;t sur votre accueil, pr&ecirc;t &agrave; l'emploi."),
]))
h.append(Spacer(1, 2*mm))
h.append(P("Partager un paquet avec quelqu'un", "h2"))
h.append(P("Le bouton <b>partage</b> sur une carte de paquet produit un long code commen&ccedil;ant par "
           "<b>TMDECK1</b>. Envoyez-le par SMS ou messagerie&nbsp;; le destinataire utilise "
           "<b>Importer un paquet</b> et colle le code. Il re&ccedil;oit toutes les cartes et le mat&eacute;riel associ&eacute;."))
h.append(Spacer(1, 2*mm))
h.append(P("L'option &laquo;&nbsp;mode extr&ecirc;me&nbsp;&raquo; du paquet", "h2"))
h.append(P("Coch&eacute;e, votre paquet personnel d&eacute;clenche lui aussi la silhouette et la question de "
           "protection, comme le mode Extr&ecirc;me officiel."))
h.append(Spacer(1, 3*mm))
h.append(encadre("Pendant une partie, vos paquets sont mis de c&ocirc;t&eacute;",
    "Quand vous rejoignez une partie, l'organisateur impose sa configuration&nbsp;: vos paquets personnels "
    "disparaissent temporairement et la cr&eacute;ation est bloqu&eacute;e. <b>Ils vous sont rendus int&eacute;gralement "
    "d&egrave;s que vous quittez la partie.</b> Rien n'est perdu."))
h.append(PageBreak())

# --- Ch 10
h.append(chapitre(10, "Jouer &agrave; plusieurs : l'organisateur"))
h.append(P("L'organisateur cr&eacute;e la partie et pilote ce que chaque joueur va tirer. "
           "Le bouton <b>multijoueur</b> se trouve en haut &agrave; droite."))
h.append(etapes([
    ("Ouvrez le menu multijoueur", "Le premier bouton en haut &agrave; droite, avec les deux silhouettes."),
    ("Donnez un nom &agrave; la partie", "Par exemple &laquo;&nbsp;Exercice Alpha&nbsp;&raquo;. C'est ce nom que vos joueurs taperont pour vous rejoindre."),
    ("Indiquez votre pseudo", "Le nom sous lequel vous appara&icirc;trez."),
    ("Laissez la liaison sur &laquo;&nbsp;Serveur Firebase&nbsp;&raquo;",
     "C'est le r&eacute;glage recommand&eacute;. Il fonctionne entre r&eacute;seaux diff&eacute;rents (la 4G d'un joueur "
     "et le WiFi d'un autre) et vous permet de fermer votre page sans couper la partie."),
    ("Appuyez sur CR&Eacute;ER UNE PARTIE", "Le <b>QG</b> s'ouvre&nbsp;: c'est votre tableau de bord."),
]))
h.append(Spacer(1, 2*mm))
h.append(P("Inviter les joueurs", "h2"))
h.append(P("L'onglet <b>Invitation</b> affiche un <b>QR code</b> et un lien. Trois fa&ccedil;ons de faire venir "
           "vos joueurs, de la plus simple &agrave; la plus manuelle&nbsp;:"))
h.append(puces([
    "ils <b>scannent le QR code</b> depuis leur application&nbsp;: c'est imm&eacute;diat&nbsp;;",
    "vous leur envoyez le <b>lien</b> par messagerie&nbsp;;",
    "ils <b>tapent le nom de la partie</b> dans leur menu Rejoindre.",
]))
h.append(Spacer(1, 2*mm))
h.append(encadre("Vous pouvez fermer votre t&eacute;l&eacute;phone",
    ["Avec la liaison Firebase, la partie vit sur le serveur, pas dans votre t&eacute;l&eacute;phone. "
     "Vous pouvez fermer l'application, verrouiller votre &eacute;cran, ou m&ecirc;me red&eacute;marrer votre appareil&nbsp;: "
     "en rouvrant l'application, vous retrouvez votre QG, vos joueurs et votre journal.",
     "C'est la diff&eacute;rence majeure avec l'ancienne liaison pair-&agrave;-pair, o&ugrave; votre page devait "
     "rester ouverte en permanence."],
    coul=VERT, fond=colors.HexColor("#eff6f0")))
h.append(PageBreak())

h.append(P("D&eacute;cider ce que chaque &eacute;quipe va tirer", "h2"))
h.append(P("C'est le c&oelig;ur du r&ocirc;le d'organisateur, dans l'onglet <b>Paquets</b>."))
h.append(etapes([
    ("Choisissez un paquet", "Classique, Avanc&eacute;, Extr&ecirc;me, Explosion, ou l'un de vos paquets personnels."),
    ("Choisissez qui le re&ccedil;oit", "Tout le monde, une &eacute;quipe seulement, ou un joueur pr&eacute;cis."),
    ("Appuyez sur AJOUTER CE PAQUET", "Il appara&icirc;t imm&eacute;diatement sur l'accueil des destinataires."),
]))
h.append(Spacer(1, 1*mm))
h.append(encadre("Le paquet attribu&eacute; remplace le mode",
    ["Un joueur qui re&ccedil;oit &laquo;&nbsp;Classique&nbsp;&raquo; ne tirera <b>que</b> du Classique. "
     "Il ne garde ni le mode de la partie, ni les cartes explosion, ni ses paquets personnels.",
     "Un joueur &agrave; qui vous n'attribuez <b>rien</b> joue le mode en cours, celui que vous avez d&eacute;fini "
     "dans l'onglet &Eacute;diteur."]))
h.append(Spacer(1, 3*mm))
h.append(P("Exemple concret", "h2"))
h.append(P("Vous voulez que les m&eacute;dics exp&eacute;riment&eacute;s de l'&eacute;quipe Rouge affrontent du lourd, "
           "pendant que les d&eacute;butants de l'&eacute;quipe Bleue apprennent&nbsp;:"))
h.append(tableau([
    [Paragraph("Destinataire", S["cellblanc"]), Paragraph("Paquet attribu&eacute;", S["cellblanc"]), Paragraph("R&eacute;sultat", S["cellblanc"])],
    [Paragraph("&Eacute;quipe Bleue", S["cell"]), Paragraph("Classique", S["cell"]), Paragraph("Soins simples, apprentissage en douceur.", S["cell"])],
    [Paragraph("&Eacute;quipe Rouge", S["cell"]), Paragraph("Extr&ecirc;me", S["cell"]), Paragraph("Silhouette, protections, protocoles longs.", S["cell"])],
], [40*mm, 40*mm, 83*mm]))
h.append(PageBreak())

# --- Ch 11
h.append(chapitre(11, "Jouer &agrave; plusieurs : le joueur"))
h.append(P("Beaucoup plus simple&nbsp;: vous n'avez presque rien &agrave; faire."))
h.append(etapes([
    ("R&eacute;glez votre pseudo", "Dans les R&eacute;glages, avant de rejoindre. L'organisateur vous reconna&icirc;tra."),
    ("Ouvrez le menu multijoueur", "Le bouton avec les deux silhouettes, en haut &agrave; droite."),
    ("Appuyez sur REJOINDRE UNE PARTIE", "Puis scannez le QR code de l'organisateur, ou tapez le nom de la partie."),
    ("Choisissez votre &eacute;quipe", "La liste propos&eacute;e est celle cr&eacute;&eacute;e par l'organisateur."),
    ("C'est tout", "Votre accueil se met &agrave; jour avec les paquets qu'on vous a attribu&eacute;s. Jouez normalement."),
]))
h.append(Spacer(1, 2*mm))
h.append(P("Ce qui change une fois en partie", "h2"))
h.append(puces([
    "le bandeau du haut affiche votre <b>&eacute;quipe</b> et le <b>nom de la partie</b>&nbsp;;",
    "un bouton <b>SORTIR</b> appara&icirc;t en haut&nbsp;;",
    "vos <b>r&eacute;glages sont verrouill&eacute;s</b>&nbsp;: c'est l'organisateur qui d&eacute;cide du mode, "
    "du mat&eacute;riel et des quantit&eacute;s&nbsp;;",
    "chacun de vos tirages appara&icirc;t dans le <b>journal</b> de l'organisateur.",
]))
h.append(Spacer(1, 2*mm))
h.append(P("Si vous perdez le r&eacute;seau", "h2"))
h.append(P("L'application se reconnecte toute seule d&egrave;s que le r&eacute;seau revient. Pendant la coupure, "
           "vous <b>conservez vos cartes attribu&eacute;es</b> et pouvez continuer &agrave; tirer&nbsp;: "
           "seuls le journal et les changements d&eacute;cid&eacute;s par l'organisateur attendront le retour du signal."))
h.append(Spacer(1, 3*mm))
h.append(encadre("Le bouton SORTIR est d&eacute;finitif",
    "Quitter la partie efface votre identit&eacute; de session. Si vous revenez, vous serez un nouveau joueur&nbsp;: "
    "l'organisateur devra vous redonner votre &eacute;quipe et, le cas &eacute;ch&eacute;ant, votre grade de co-organisateur. "
    "Pour une simple pause, <b>fermez l'application sans appuyer sur Sortir</b>.",
    coul=ORANG, fond=colors.HexColor("#fdf5ec")))
h.append(PageBreak())

# --- Ch 12
h.append(chapitre(12, "Le QG, onglet par onglet"))
h.append(P("Le QG est le tableau de bord de l'organisateur. Six onglets, chacun avec un r&ocirc;le pr&eacute;cis."))
h.append(Spacer(1, 2*mm))
h.append(tableau([
    [Paragraph("Onglet", S["cellblanc"]), Paragraph("&Agrave; quoi il sert", S["cellblanc"])],
    [Paragraph("<b>Invitation</b>", S["cell"]), Paragraph("Le nom de la partie, le QR code et le lien &agrave; partager. C'est l&agrave; que vous envoyez vos joueurs.", S["cell"])],
    [Paragraph("<b>Joueurs</b>", S["cell"]), Paragraph("La liste des connect&eacute;s. Pour chacun&nbsp;: changer son &eacute;quipe d'un appui, le passer <b>Admin</b>, ou le <b>Kick</b>. Les joueurs hors ligne restent affich&eacute;s en gris&eacute;.", S["cell"])],
    [Paragraph("<b>&Eacute;quipes</b>", S["cell"]), Paragraph("Cr&eacute;er ou supprimer des &eacute;quipes, avec leur couleur. Minimum deux. Supprimer une &eacute;quipe replace automatiquement ses joueurs ailleurs.", S["cell"])],
    [Paragraph("<b>&Eacute;diteur</b>", S["cell"]), Paragraph("R&eacute;gler chaque paquet <b>avant</b> de le distribuer&nbsp;: quantit&eacute;s, mat&eacute;riel, risque de mort. Le mode marqu&eacute; <b>JOU&Eacute;</b> est celui des joueurs sans attribution.", S["cell"])],
    [Paragraph("<b>Paquets</b>", S["cell"]), Paragraph("Attribuer un paquet &agrave; tout le monde, &agrave; une &eacute;quipe ou &agrave; un joueur. La liste du bas montre ce qui est distribu&eacute;, avec une corbeille pour retirer.", S["cell"])],
    [Paragraph("<b>Logs</b>", S["cell"]), Paragraph("Le journal en temps r&eacute;el&nbsp;: qui a rejoint, qui a tir&eacute; quelle blessure, &agrave; quelle heure. T&eacute;l&eacute;chargeable en fichier texte.", S["cell"])],
], [26*mm, 137*mm]))
h.append(Spacer(1, 4*mm))
h.append(P("Le co-organisateur", "h2"))
h.append(P("Passer un joueur <b>Admin</b> lui donne acc&egrave;s au m&ecirc;me QG que vous. Il peut d&eacute;placer "
           "des joueurs, distribuer des paquets, cr&eacute;er des &eacute;quipes. Tr&egrave;s pratique sur un grand "
           "terrain o&ugrave; vous ne pouvez pas &ecirc;tre partout."))
h.append(encadre("Personne ne peut se promouvoir tout seul",
    "Le grade d'administrateur ne peut &ecirc;tre donn&eacute; que par vous ou par un co-organisateur existant, "
    "et cette r&egrave;gle est appliqu&eacute;e <b>par le serveur</b>. M&ecirc;me un joueur qui conna&icirc;trait "
    "parfaitement l'application ne peut pas se l'attribuer, ni prendre l'identit&eacute; de quelqu'un d'autre "
    "en copiant son pseudo.",
    coul=VERT, fond=colors.HexColor("#eff6f0")))
h.append(Spacer(1, 3*mm))
h.append(P("Cl&ocirc;turer la partie", "h2"))
h.append(P("Le bouton rouge en bas du QG pr&eacute;vient tous les joueurs et les d&eacute;connecte. "
           "<b>Pensez &agrave; t&eacute;l&eacute;charger vos logs avant</b> si vous voulez garder une trace de la partie."))
h.append(PageBreak())

# --- Ch 13
h.append(chapitre(13, "Sur le terrain : conseils pratiques"))
h.append(P("Avant la partie", "h2"))
h.append(puces([
    "faites <b>ouvrir l'application une fois avec du r&eacute;seau</b> &agrave; tous les m&eacute;dics, au briefing&nbsp;;",
    "demandez-leur d'<b>installer l'ic&ocirc;ne</b> sur leur &eacute;cran d'accueil&nbsp;;",
    "faites-leur r&eacute;gler leur <b>pseudo</b> avant de rejoindre&nbsp;;",
    "cr&eacute;ez la partie et testez la connexion <b>avec un t&eacute;l&eacute;phone</b> avant l'arriv&eacute;e de tout le monde&nbsp;;",
    "r&eacute;glez vos quantit&eacute;s dans l'onglet <b>&Eacute;diteur</b> avant de distribuer les paquets.",
]))
h.append(P("Pendant la partie", "h2"))
h.append(puces([
    "gardez le QG ouvert sur l'onglet <b>Logs</b> pour suivre l'activit&eacute; en direct&nbsp;;",
    "si un type de soin s'av&egrave;re introuvable sur le terrain, retirez son mat&eacute;riel depuis l'onglet "
    "<b>&Eacute;diteur</b>&nbsp;: le changement s'applique aussit&ocirc;t &agrave; tous les joueurs&nbsp;;",
    "pour durcir en cours de partie, augmentez la probabilit&eacute; du risque de mort&nbsp;: "
    "le changement est imm&eacute;diat chez tous les joueurs&nbsp;;",
    "d&eacute;signez un <b>co-organisateur</b> si le terrain est grand.",
]))
h.append(P("Apr&egrave;s la partie", "h2"))
h.append(puces([
    "<b>t&eacute;l&eacute;chargez les logs</b> avant de cl&ocirc;turer&nbsp;: excellent support de d&eacute;briefing&nbsp;;",
    "cl&ocirc;turez proprement pour lib&eacute;rer le nom de la partie.",
]))
h.append(Spacer(1, 3*mm))
h.append(encadre("Batterie",
    "L'&eacute;cran reste allum&eacute; pendant l'affichage d'une fiche, et la connexion permanente consomme. "
    "Sur une journ&eacute;e compl&egrave;te, pr&eacute;voyez une <b>batterie externe</b> pour l'organisateur "
    "et pour les m&eacute;dics les plus sollicit&eacute;s.",
    coul=ORANG, fond=colors.HexColor("#fdf5ec")))
h.append(PageBreak())

# --- Ch 14
h.append(chapitre(14, "En cas de probl&egrave;me"))
h.append(tableau([
    [Paragraph("Sympt&ocirc;me", S["cellblanc"]), Paragraph("Que faire", S["cellblanc"])],
    [Paragraph("<b>L'application ne s'ouvre pas hors r&eacute;seau</b>", S["cell"]),
     Paragraph("Elle n'a jamais &eacute;t&eacute; ouverte avec du r&eacute;seau sur cet appareil. Reconnectez-vous une fois, laissez-la charger enti&egrave;rement, puis elle fonctionnera hors ligne.", S["cell"])],
    [Paragraph("<b>&laquo;&nbsp;Partie introuvable&nbsp;&raquo;</b>", S["cell"]),
     Paragraph("V&eacute;rifiez l'orthographe exacte du nom aupr&egrave;s de l'organisateur. Les accents et les espaces n'ont pas d'importance, mais les lettres si. Le plus s&ucirc;r reste le QR code.", S["cell"])],
    [Paragraph("<b>&laquo;&nbsp;Aucune carte disponible&nbsp;&raquo;</b>", S["cell"]),
     Paragraph("Toutes les cartes sont soit &agrave; z&eacute;ro, soit bloqu&eacute;es par du mat&eacute;riel manquant. En solo, ouvrez les R&eacute;glages et recochez du mat&eacute;riel. En partie, signalez-le &agrave; l'organisateur&nbsp;: lui seul peut y toucher.", S["cell"])],
    [Paragraph("<b>Un joueur appara&icirc;t en double</b>", S["cell"]),
     Paragraph("Deux joueurs ont le m&ecirc;me pseudo&nbsp;: le second devient automatiquement &laquo;&nbsp;Nom (2)&nbsp;&raquo;. Demandez-lui de changer de pseudo, ou laissez comme &ccedil;a.", S["cell"])],
    [Paragraph("<b>Un joueur reste &laquo;&nbsp;hors ligne&nbsp;&raquo;</b>", S["cell"]),
     Paragraph("Son t&eacute;l&eacute;phone a perdu le r&eacute;seau. Il revient tout seul. S'il est vraiment parti, retirez-le avec le bouton Kick.", S["cell"])],
    [Paragraph("<b>Je ne retrouve plus mes paquets perso</b>", S["cell"]),
     Paragraph("Vous &ecirc;tes en partie&nbsp;: ils sont mis de c&ocirc;t&eacute; et vous seront rendus en quittant. Rien n'est perdu.", S["cell"])],
    [Paragraph("<b>L'affichage semble ancien</b>", S["cell"]),
     Paragraph("Fermez compl&egrave;tement l'application et rouvrez-la avec du r&eacute;seau&nbsp;: elle se met &agrave; jour toute seule.", S["cell"])],
], [46*mm, 117*mm]))
h.append(Spacer(1, 8*mm))
fin = Table([[Paragraph('<font color="white" size="11"><b>Bon jeu, et bons soins.</b></font><br/>'
                        '<font color="#c49708" size="9">Bravo Sierra Events // Frontline</font>', S["pc"])]],
            colWidths=[163*mm])
fin.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NOIR),
                         ("ALIGN", (0,0), (-1,-1), "CENTER"),
                         ("TOPPADDING", (0,0), (-1,-1), 13), ("BOTTOMPADDING", (0,0), (-1,-1), 13)]))
h.append(fin)

# ---------------------------------------------------------------- build
doc = Doc(SORTIE, title="BSE Medical System - Guide d'utilisation",
          author="Bravo Sierra Events", subject="Guide d'utilisation de l'application BSE Medical System")

from reportlab.platypus import NextPageTemplate
final = [NextPageTemplate("std")] + h
doc.build(final)
print("PDF genere :", SORTIE)
print("taille     :", round(os.path.getsize(SORTIE)/1024, 1), "Ko")
