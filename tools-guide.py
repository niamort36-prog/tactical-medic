# -*- coding: utf-8 -*-
"""Guide d'utilisation BSE Medical System — un PDF par langue.

   Le texte vit dans guide-<code>.py (un dictionnaire TEXTES) ; ce
   fichier ne s'occupe que de la mise en page. Relancer apres toute
   evolution de l'application :  python tools-guide.py
"""
import os
import importlib.util
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
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


# Une entree par langue : code, police normale, police grasse.
# Helvetica ne contient aucun ideogramme : le chinois et le japonais
# passent par les polices CID fournies avec reportlab. Elles n'ont pas de
# variante grasse, on reutilise donc la meme fonte pour <b> — le gras ne
# se voit pas en CJK, mais rien ne casse.
LANGUES = [
    ("fr", "Helvetica", "Helvetica-Bold"),
    ("en", "Helvetica", "Helvetica-Bold"),
    ("de", "Helvetica", "Helvetica-Bold"),
    ("es", "Helvetica", "Helvetica-Bold"),
    ("it", "Helvetica", "Helvetica-Bold"),
    ("zh", "STSong-Light", "STSong-Light"),
    ("ja", "HeiseiKakuGo-W5", "HeiseiKakuGo-W5"),
]

def charger_textes(code):
    chemin = os.path.join(REPO, "guide-%s.py" % code)
    spec = importlib.util.spec_from_file_location("guide_" + code, chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TEXTES

def preparer_police(normale, grasse):
    """Enregistre une police CID si besoin et declare la famille, sans quoi
       reportlab refuse les balises <b> et <i>."""
    if normale == "Helvetica":
        return
    if normale not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(UnicodeCIDFont(normale))
    pdfmetrics.registerFontFamily(normale, normal=normale, bold=grasse,
                                  italic=normale, boldItalic=grasse)


def generer(code, REGULIER, GRAS):
    T = charger_textes(code)
    SORTIE = os.path.join(REPO, "guide-bse-medical-system-%s.pdf" % code)
    preparer_police(REGULIER, GRAS)

    def st(nom, **kw):
        base = dict(name=nom, fontName=REGULIER, fontSize=10.2, leading=15.2,
                    textColor=NOIR, alignment=TA_LEFT, spaceAfter=6)
        base.update(kw)
        return ParagraphStyle(**base)

    S = {
        "titre":    st("titre", fontName=GRAS, fontSize=27, leading=31, textColor=colors.white, alignment=TA_CENTER, spaceAfter=4),
        "stitre":   st("stitre", fontSize=11, leading=15, textColor=ORC, alignment=TA_CENTER, spaceAfter=0),
        "h1":       st("h1", fontName=GRAS, fontSize=16.5, leading=20, textColor=NOIR, spaceAfter=3, spaceBefore=0),
        "h1num":    st("h1num", fontName=GRAS, fontSize=9, leading=11, textColor=OR, spaceAfter=1),
        "h2":       st("h2", fontName=GRAS, fontSize=11.6, leading=15, textColor=NOIR, spaceBefore=9, spaceAfter=3),
        "p":        st("p"),
        "pc":       st("pc", alignment=TA_CENTER),
        "petit":    st("petit", fontSize=8.8, leading=12.4, textColor=GRIS),
        "puce":     st("puce", spaceAfter=3),
        "encadre":  st("encadre", fontSize=9.6, leading=13.8),
        "cell":     st("cell", fontSize=9.2, leading=12.6, spaceAfter=0),
        "cellb":    st("cellb", fontName=GRAS, fontSize=9.2, leading=12.6, spaceAfter=0),
        "cellblanc":st("cellblanc", fontName=GRAS, fontSize=9.2, leading=12.6, textColor=colors.white, spaceAfter=0),
        "somm":     st("somm", fontSize=10.5, leading=17, spaceAfter=0),
    }

    def P(txt, s="p"): return Paragraph(txt, S[s])

    def puces(items, style="puce"):
        return ListFlowable([Paragraph(i, S[style]) for i in items],
                            bulletType="bullet", start="\u2022", leftIndent=13,
                            bulletFontSize=8, bulletOffsetY=1, spaceAfter=6)

    def encadre(titre, corps, coul=ORC, fond=colors.HexColor("#fdf7e3")):
        inner = [Paragraph(titre, ParagraphStyle("bt", parent=S["encadre"], fontName=GRAS,
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
            [Paragraph(T["g001"], S["cell"]),
             Paragraph(T["g002"], S["cell"])],
            ligne("", T["g003"], NOIR, True),
            ligne(T["g004"], T["m01"]),
            ligne(T["m02"], T["g005"], OR),
            ligne(T["m03"], T["g006"]),
            ligne(T["g007"], T["g008"], NOIR, True),
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
            c.setFont(REGULIER, 7.4); c.setFillColor(GRIS)
            c.drawString(23*mm, A4[1]-11*mm, T["g009"])
            c.setStrokeColor(GRISC); c.setLineWidth(0.4)
            c.line(23*mm, A4[1]-13.5*mm, A4[0]-23*mm, A4[1]-13.5*mm)
            c.line(23*mm, 15*mm, A4[0]-23*mm, 15*mm)
            c.setFont(REGULIER, 7.6); c.setFillColor(GRIS)
            c.drawString(23*mm, 11*mm, T["g010"])
            c.setFont(GRAS, 8.4); c.setFillColor(NOIR)
            c.drawRightString(A4[0]-23*mm, 11*mm, str(c.getPageNumber() - 1))

    def chapitre(num, titre):
        return KeepTogether([Spacer(1, 2*mm),
                             P(T["chapitre"] + " " + str(num) + T.get("chapitre_apres", ""), "h1num"), P(titre, "h1"),
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
    h.append(P(T["g011"], "titre"))
    h.append(Spacer(1, 3*mm))
    h.append(P(T["g012"], "stitre"))
    h.append(Spacer(1, 22*mm))
    bandeau = Table([[Paragraph(T["g013"], S["pc"])]],
                    colWidths=[110*mm])
    bandeau.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#2a2a26")),
                                 ("BOX", (0,0), (-1,-1), 0.7, ORC),
                                 ("ALIGN", (0,0), (-1,-1), "CENTER"),
                                 ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9)]))
    bandeau.hAlign = "CENTER"
    h += [bandeau, Spacer(1, 9*mm)]
    h.append(Paragraph(T["g014"], S["pc"]))
    h.append(Spacer(1, 45*mm))
    h.append(Paragraph(T["g015"], S["pc"]))
    h.append(PageBreak())

    # --- Sommaire
    h.append(P("Sommaire", "h1"))
    h.append(Table([[""]], colWidths=[163*mm], rowHeights=[1.6],
                   style=TableStyle([("BACKGROUND", (0,0), (-1,-1), ORC)])))
    h.append(Spacer(1, 6*mm))
    somm = [
        ("1", T["g016"], "2"),
        ("2", T["g017"], "3"),
        ("3", T["g018"], "4"),
        ("4", T["g019"], "5"),
        ("5", T["g020"], "6"),
        ("6", T["g021"], "7"),
        ("7", T["g022"], "8"),
        ("8", T["g023"], "9"),
        ("9", T["g024"], "11"),
        ("10", T["g025"], "12"),
        ("11", T["g026"], "14"),
        ("12", T["g027"], "15"),
        ("13", T["g028"], "16"),
        ("14", T["g029"], "17"),
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
    h.append(encadre(T["g030"],
        T["g031"]))
    h.append(PageBreak())

    # --- Ch 1
    h.append(chapitre(1, T["g032"]))
    h.append(P(T["g033"]))
    h.append(P(T["g034"]))
    h.append(Spacer(1, 3*mm))
    h.append(P(T["g035"], "h2"))
    h.append(etapes([
        (T["g036"], T["g037"]),
        (T["g038"], T["g039"]),
        (T["g040"], T["g041"]),
        (T["g042"], T["g043"]),
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(encadre(T["g044"],
        T["g045"]))
    h.append(PageBreak())

    # --- Ch 2
    h.append(chapitre(2, T["g046"]))
    h.append(P(T["g047"]))
    h.append(etapes([
        (T["g048"],
         T["g049"]),
        (T["g050"],
         T["g051"]),
        (T["g052"],
         T["g053"]),
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(encadre(T["g054"],
        [T["g055"],
         T["g056"]],
        coul=ROUGE, fond=colors.HexColor("#fdf1ef")))
    h.append(Spacer(1, 3*mm))
    h.append(P(T["g057"], "h2"))
    h.append(P(T["g058"]))
    h.append(puces([
        T["g059"],
        T["g060"],
        T["g061"],
        T["g062"],
        T["m07"],
    ]))
    h.append(PageBreak())

    # --- Ch 3
    h.append(chapitre(3, T["g063"]))
    h.append(P(T["g064"]))
    h.append(etapes([
        (T["g065"], T["g066"]),
        (T["g067"], T["g068"]),
        (T["g069"], T["g070"]),
        (T["g071"],
         T["g072"]),
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g073"], "h2"))
    h.append(P(T["g074"]))
    march = [[Paragraph(f'<font color="#a8800a"><b>{l}</b></font>', S["cellb"]), Paragraph(t, S["cell"])]
             for l, t in [("M", T["g075"]),
                          ("A", T["g076"]),
                          ("R", T["g077"]),
                          ("C", T["g078"]),
                          ("H", T["g079"])]]
    tm = Table(march, colWidths=[10*mm, 153*mm])
    tm.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0),
                            ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3)]))
    h += [tm, Spacer(1, 4*mm)]
    h.append(encadre(T["g080"],
        T["g081"]))
    h.append(PageBreak())

    # --- Ch 4
    h.append(chapitre(4, T["g082"]))
    h.append(P(T["g083"]))
    h.append(Spacer(1, 2*mm))
    h.append(maquette_fiche())
    h.append(Spacer(1, 5*mm))
    h.append(P(T["g084"], "h2"))
    h.append(tableau([
        [Paragraph(T["g085"], S["cellblanc"]), Paragraph(T["g086"], S["cellblanc"])],
        [Paragraph(T["g087"], S["cell"]), Paragraph(T["g088"], S["cell"])],
        [Paragraph("<b>" + T["m04"] + "</b>", S["cell"]), Paragraph(T["g089"], S["cell"])],
        [Paragraph(T["g090"], S["cell"]), Paragraph(T["g091"], S["cell"])],
        [Paragraph("<b>" + T["m05"] + "</b>", S["cell"]), Paragraph(T["g092"], S["cell"])],
        [Paragraph("<b>" + T["m06"] + "</b>", S["cell"]), Paragraph(T["g093"], S["cell"])],
        [Paragraph(T["g094"], S["cell"]), Paragraph(T["g095"], S["cell"])],
    ], [38*mm, 125*mm]))
    h.append(Spacer(1, 4*mm))
    h.append(encadre(T["g096"],
        [T["g097"],
         T["g098"]],
        coul=ROUGE, fond=colors.HexColor("#fdf1ef")))
    h.append(PageBreak())

    # --- Ch 5
    h.append(chapitre(5, T["g099"]))
    h.append(P(T["g100"]))
    h.append(Spacer(1, 2*mm))
    def pastille(txt, coul):
        t = Table([[Paragraph(f'<font color="white" size="9"><b>{txt}</b></font>', S["cell"])]], colWidths=[24*mm])
        t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), coul), ("ALIGN", (0,0), (-1,-1), "CENTER"),
                               ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
        return t
    h.append(tableau([
        [Paragraph(T["g101"], S["cellblanc"]), Paragraph(T["g102"], S["cellblanc"])],
        [pastille(T["g103"], DECES), Paragraph(T["g104"], S["cell"])],
        [pastille("CRITIQUE", ROUGE), Paragraph(T["g105"], S["cell"])],
        [pastille("GRAVE", ORANG), Paragraph(T["g106"], S["cell"])],
        [pastille(T["g107"], VERT), Paragraph(T["g108"], S["cell"])],
        [pastille(T["g109"], VIOL), Paragraph(T["g110"], S["cell"])],
    ], [30*mm, 133*mm]))
    h.append(Spacer(1, 5*mm))
    h.append(P(T["g111"], "h2"))
    h.append(P(T["g112"]))
    h.append(PageBreak())

    # --- Ch 6
    h.append(chapitre(6, T["g113"]))
    h.append(P(T["g114"]))
    h.append(Spacer(1, 2*mm))
    h.append(tableau([
        [Paragraph("Mode", S["cellblanc"]), Paragraph("Cartes", S["cellblanc"]), Paragraph("Pour qui", S["cellblanc"])],
        [Paragraph("<b>Classique</b>", S["cell"]), Paragraph("8", S["cell"]),
         Paragraph(T["g115"], S["cell"])],
        [Paragraph(T["g116"], S["cell"]), Paragraph("10", S["cell"]),
         Paragraph(T["g117"], S["cell"])],
        [Paragraph(T["g118"], S["cell"]), Paragraph("17", S["cell"]),
         Paragraph(T["g119"], S["cell"])],
        [Paragraph("<b>Explosion</b>", S["cell"]), Paragraph("14", S["cell"]),
         Paragraph(T["g120"], S["cell"])],
    ], [30*mm, 18*mm, 115*mm]))
    h.append(Spacer(1, 5*mm))
    h.append(P(T["g121"], "h2"))
    h.append(P(T["g122"]))
    h.append(encadre(T["g123"],
        T["g124"]))
    h.append(PageBreak())

    # --- Ch 7
    h.append(chapitre(7, T["g125"]))
    h.append(P(T["g126"]))
    h.append(etapes([
        (T["g127"], T["g128"]),
        (T["g129"],
         T["g130"]),
        (T["g131"],
         T["g132"]),
        (T["g133"], T["g134"]),
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g135"], "h2"))
    h.append(P(T["g136"]))
    h.append(Spacer(1, 1*mm))
    h.append(tableau([
        [Paragraph(T["g137"], S["cellblanc"]), Paragraph(T["g138"], S["cellblanc"]), Paragraph(T["g139"], S["cellblanc"])],
        [Paragraph(T["g140"], S["cell"]),
         Paragraph(T["g141"], S["cell"]),
         Paragraph(T["g142"], S["cell"])],
        [Paragraph("<b>" + T["m01"] + "</b>", S["cell"]),
         Paragraph(T["g143"], S["cell"]),
         Paragraph(T["g144"], S["cell"])],
        [Paragraph(T["g145"], S["cell"]),
         Paragraph(T["g146"], S["cell"]),
         Paragraph(T["g147"], S["cell"])],
    ], [30*mm, 62*mm, 71*mm]))
    h.append(Spacer(1, 4*mm))
    h.append(encadre(T["g148"],
        T["g149"]))
    h.append(PageBreak())

    # --- Ch 8
    h.append(chapitre(8, T["g150"]))
    h.append(P(T["g151"]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g152"], "h2"))
    h.append(P(T["g153"]))
    h.append(P("Mode de jeu", "h2"))
    h.append(P(T["g154"]))
    h.append(P(T["g155"], "h2"))
    h.append(P(T["g156"]))
    h.append(tableau([
        [Paragraph(T["g157"], S["cellblanc"]), Paragraph("Effet", S["cellblanc"])],
        [Paragraph(T["g158"], S["cell"]), Paragraph(T["g159"], S["cell"])],
        [Paragraph(T["g160"], S["cell"]), Paragraph(T["g161"], S["cell"])],
        [Paragraph(T["g162"], S["cell"]), Paragraph(T["g163"], S["cell"])],
        [Paragraph(T["g164"], S["cell"]), Paragraph(T["g165"], S["cell"])],
    ], [32*mm, 131*mm]))
    h.append(PageBreak())

    h.append(P(T["g166"], "h2"))
    h.append(P(T["g167"]))
    h.append(P(T["g168"]))
    h.append(encadre(T["g169"],
        [T["g170"],
         T["g171"],
         T["g172"]]))
    h.append(Spacer(1, 3*mm))
    h.append(P(T["g173"], "h2"))
    h.append(P(T["g174"]))
    h.append(puces([
        T["g175"],
        T["g176"],
        T["g177"],
        T["g178"],
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(encadre(T["g179"],
        T["g180"]))
    h.append(PageBreak())

    # --- Ch 9
    h.append(chapitre(9, T["g181"]))
    h.append(P(T["g182"]))
    h.append(etapes([
        (T["g183"], T["g184"]),
        (T["g185"], T["g186"]),
        (T["g187"], T["g188"]),
        (T["g189"], T["g190"]),
        ("Enregistrer", T["g191"]),
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g192"], "h2"))
    h.append(P(T["g193"]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g194"], "h2"))
    h.append(P(T["g195"]))
    h.append(Spacer(1, 3*mm))
    h.append(encadre(T["g196"],
        T["g197"]))
    h.append(PageBreak())

    # --- Ch 10
    h.append(chapitre(10, T["g198"]))
    h.append(P(T["g199"]))
    h.append(etapes([
        (T["g200"], T["g201"]),
        (T["g202"], T["g203"]),
        (T["g204"], T["g205"]),
        (T["g206"],
         T["g207"]),
        (T["g208"], T["g209"]),
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g210"], "h2"))
    h.append(P(T["g211"]))
    h.append(puces([
        T["g212"],
        T["g213"],
        T["g214"],
        T["g215"],
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(encadre(T["g216"],
        [T["g217"],
         T["g218"]],
        coul=VERT, fond=colors.HexColor("#eff6f0")))
    h.append(PageBreak())

    h.append(P(T["g219"], "h2"))
    h.append(P(T["g220"]))
    h.append(etapes([
        (T["g221"], T["g222"]),
        (T["g223"], T["g224"]),
        (T["g225"], T["g226"]),
    ]))
    h.append(Spacer(1, 1*mm))
    h.append(encadre(T["g227"],
        [T["g228"],
         T["g229"]]))
    h.append(Spacer(1, 3*mm))
    h.append(P(T["g230"], "h2"))
    h.append(P(T["g231"]))
    h.append(tableau([
        [Paragraph("Destinataire", S["cellblanc"]), Paragraph(T["g232"], S["cellblanc"]), Paragraph(T["g233"], S["cellblanc"])],
        [Paragraph(T["g234"], S["cell"]), Paragraph("Classique", S["cell"]), Paragraph(T["g235"], S["cell"])],
        [Paragraph(T["g236"], S["cell"]), Paragraph(T["g237"], S["cell"]), Paragraph(T["g238"], S["cell"])],
    ], [40*mm, 40*mm, 83*mm]))
    h.append(PageBreak())

    # --- Ch 11
    h.append(chapitre(11, T["g239"]))
    h.append(P(T["g240"]))
    h.append(P(T["g241"], "h2"))
    h.append(etapes([
        (T["g242"], T["g243"]),
        (T["g244"], T["g245"]),
        ("C'est tout", T["g246"]),
    ]))
    h.append(P(T["g247"], "h2"))
    h.append(etapes([
        (T["g248"], T["g249"]),
        (T["g250"], T["g251"]),
        (T["g252"], T["g253"]),
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g254"], "h2"))
    h.append(puces([
        T["g255"],
        T["g256"],
        T["g257"],
        T["g258"],
    ]))
    h.append(Spacer(1, 2*mm))
    h.append(P(T["g259"], "h2"))
    h.append(P(T["g260"]))
    h.append(Spacer(1, 3*mm))
    h.append(encadre(T["g261"],
        T["g262"],
        coul=ORANG, fond=colors.HexColor("#fdf5ec")))
    h.append(PageBreak())

    # --- Ch 12
    h.append(chapitre(12, T["g263"]))
    h.append(P(T["g264"]))
    h.append(Spacer(1, 2*mm))
    h.append(tableau([
        [Paragraph("Onglet", S["cellblanc"]), Paragraph(T["g265"], S["cellblanc"])],
        [Paragraph("<b>Invitation</b>", S["cell"]), Paragraph(T["g266"], S["cell"])],
        [Paragraph("<b>Joueurs</b>", S["cell"]), Paragraph(T["g267"], S["cell"])],
        [Paragraph(T["g268"], S["cell"]), Paragraph(T["g269"], S["cell"])],
        [Paragraph(T["g270"], S["cell"]), Paragraph(T["g271"], S["cell"])],
        [Paragraph("<b>Paquets</b>", S["cell"]), Paragraph(T["g272"], S["cell"])],
        [Paragraph("<b>Logs</b>", S["cell"]), Paragraph(T["g273"], S["cell"])],
    ], [26*mm, 137*mm]))
    h.append(Spacer(1, 4*mm))
    h.append(P(T["g274"], "h2"))
    h.append(P(T["g275"]))
    h.append(encadre(T["g276"],
        T["g277"],
        coul=VERT, fond=colors.HexColor("#eff6f0")))
    h.append(Spacer(1, 3*mm))
    h.append(P(T["g278"], "h2"))
    h.append(P(T["g279"]))
    h.append(PageBreak())

    # --- Ch 13
    h.append(chapitre(13, T["g280"]))
    h.append(P(T["g281"], "h2"))
    h.append(puces([
        T["g282"],
        T["g283"],
        T["g284"],
        T["g285"],
        T["g286"],
    ]))
    h.append(P(T["g287"], "h2"))
    h.append(puces([
        T["g288"],
        T["g289"],
        T["g290"],
        T["g291"],
    ]))
    h.append(P(T["g292"], "h2"))
    h.append(puces([
        T["g293"],
        T["g294"],
    ]))
    h.append(Spacer(1, 3*mm))
    h.append(encadre("Batterie",
        T["g295"],
        coul=ORANG, fond=colors.HexColor("#fdf5ec")))
    h.append(PageBreak())

    # --- Ch 14
    h.append(chapitre(14, T["g296"]))
    h.append(tableau([
        [Paragraph(T["g297"], S["cellblanc"]), Paragraph("Que faire", S["cellblanc"])],
        [Paragraph(T["g298"], S["cell"]),
         Paragraph(T["g299"], S["cell"])],
        [Paragraph(T["g300"], S["cell"]),
         Paragraph(T["g301"], S["cell"])],
        [Paragraph(T["g302"], S["cell"]),
         Paragraph(T["g303"], S["cell"])],
        [Paragraph(T["g304"], S["cell"]),
         Paragraph(T["g305"], S["cell"])],
        [Paragraph(T["g306"], S["cell"]),
         Paragraph(T["g307"], S["cell"])],
        [Paragraph(T["g308"], S["cell"]),
         Paragraph(T["g309"], S["cell"])],
        [Paragraph(T["g310"], S["cell"]),
         Paragraph(T["g311"], S["cell"])],
    ], [46*mm, 117*mm]))
    h.append(Spacer(1, 8*mm))
    fin = Table([[Paragraph(T["g312"], S["pc"])]],
                colWidths=[163*mm])
    fin.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NOIR),
                             ("ALIGN", (0,0), (-1,-1), "CENTER"),
                             ("TOPPADDING", (0,0), (-1,-1), 13), ("BOTTOMPADDING", (0,0), (-1,-1), 13)]))
    h.append(fin)

    # ---------------------------------------------------------------- build
    doc = Doc(SORTIE, title=T["g313"],
              author=T["g314"], subject=T["g315"])

    from reportlab.platypus import NextPageTemplate
    final = [NextPageTemplate("std")] + h
    doc.build(final)
    print(T["g316"], SORTIE)
    print(T["g317"], round(os.path.getsize(SORTIE)/1024, 1), "Ko")

for code, normale, grasse in LANGUES:
    if not os.path.exists(os.path.join(REPO, "guide-%s.py" % code)):
        print("  (pas de textes pour", code, "- ignore)")
        continue
    generer(code, normale, grasse)
