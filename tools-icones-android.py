# -*- coding: utf-8 -*-
"""Icones de l'application Android, tirees de la charte BSE.

   Un lanceur Android recadre librement l'icone (cercle, carre arrondi,
   goutte...) : seul le disque central de 66 dp sur les 108 dp de la toile
   est garanti visible. Le cadre dore de l'icone web, lui, touche presque le
   bord : tel quel il serait rogne. On redessine donc la croix seule, a la
   bonne echelle, sur un fond uni — c'est exactement ce que demande le
   format « icone adaptative ».

   Relancer apres toute modification de la charte :  python tools-icones-android.py
"""
import io, os
from PIL import Image, ImageDraw

OR    = (196, 151, 8, 255)     # dore BSE, releve sur icons/icon-512.png
FOND  = (7, 7, 7, 255)         # noir de l'application
RES   = os.path.join('android', 'app', 'src', 'main', 'res')
BOUTIQUE = os.path.join('android', 'boutique')

# Densites Android : dossier -> facteur par rapport au mdpi
DENSITES = [('mdpi', 1), ('hdpi', 1.5), ('xhdpi', 2), ('xxhdpi', 3), ('xxxhdpi', 4)]


def croix(dessin, cote, taille, epaisseur, couleur):
    """Croix grecque centree sur une toile carree de `cote` pixels."""
    c = cote / 2.0
    d, e = taille / 2.0, epaisseur / 2.0
    dessin.rectangle([c - e, c - d, c + e, c + d], fill=couleur)   # barre verticale
    dessin.rectangle([c - d, c - e, c + d, c + e], fill=couleur)   # barre horizontale


def icone_complete(cote):
    """Le dessin d'origine : fond noir, cadre dore, croix. Pour les lanceurs
       anciens (avant Android 8) et pour la fiche de la boutique."""
    im = Image.new('RGBA', (cote, cote), FOND)
    d = ImageDraw.Draw(im)
    marge = cote * 61 / 512.0          # memes proportions que l'icone web
    trait = max(1, int(round(cote * 6 / 512.0)))
    d.rectangle([marge, marge, cote - marge - 1, cote - marge - 1], outline=OR, width=trait)
    croix(d, cote, cote * 256 / 512.0, cote * 84 / 512.0, OR)
    return im


def premier_plan(cote):
    """Couche avant de l'icone adaptative : la croix seule, sur du vide.
       52 % de la toile, donc bien a l'interieur du disque garanti (61 %)."""
    im = Image.new('RGBA', (cote, cote), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    croix(d, cote, cote * 0.52, cote * 0.52 / 3.05, OR)
    return im


def ecrire(im, chemin):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    im.save(chemin)
    print('  ', chemin, im.size)


def rond(im):
    """Variante ronde demandee par certains lanceurs."""
    cote = im.size[0]
    masque = Image.new('L', (cote, cote), 0)
    ImageDraw.Draw(masque).ellipse([0, 0, cote - 1, cote - 1], fill=255)
    sortie = Image.new('RGBA', (cote, cote), (0, 0, 0, 0))
    sortie.paste(im, (0, 0), masque)
    return sortie


print('Icones de lancement')
for nom, f in DENSITES:
    c48 = int(round(48 * f))          # icone de lanceur classique
    c108 = int(round(108 * f))        # toile de l'icone adaptative
    ecrire(icone_complete(c48), os.path.join(RES, 'mipmap-' + nom, 'ic_launcher.png'))
    ecrire(rond(icone_complete(c48)), os.path.join(RES, 'mipmap-' + nom, 'ic_launcher_round.png'))
    ecrire(premier_plan(c108), os.path.join(RES, 'mipmap-' + nom, 'ic_launcher_foreground.png'))

print('Ecran de demarrage')
# Le logo BSE MEDICAL, centre sur le noir de l'application. Affiche par
# Chrome pendant que la page se charge : sans lui, l'ouverture clignote blanc.
logo = Image.open(os.path.join('icons', 'logo-bse-medical@2x.png')).convert('RGBA')
for nom, f in DENSITES:
    largeur = int(round(220 * f))     # 220 dp de large, lisible sur tout ecran
    hauteur = int(round(largeur * logo.size[1] / float(logo.size[0])))
    ecrire(logo.resize((largeur, hauteur), Image.LANCZOS),
           os.path.join(RES, 'drawable-' + nom, 'splash.png'))

print('Fiche de la boutique')
# Google Play refuse la transparence sur l'icone de la fiche.
fiche = Image.new('RGB', (512, 512), FOND[:3])
fiche.paste(icone_complete(512), (0, 0), icone_complete(512))
ecrire(fiche, os.path.join(BOUTIQUE, 'icone-512.png'))

# Banniere de la fiche : 1024 x 500, le logo centre sur le noir.
banniere = Image.new('RGB', (1024, 500), FOND[:3])
l = int(640)
h = int(round(l * logo.size[1] / float(logo.size[0])))
banniere.paste(logo.resize((l, h), Image.LANCZOS), ((1024 - l) // 2, (500 - h) // 2),
               logo.resize((l, h), Image.LANCZOS))
ecrire(banniere, os.path.join(BOUTIQUE, 'banniere-1024x500.png'))

print('\nTermine.')
