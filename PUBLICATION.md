# Publier BSE Medical System sur les boutiques

Ce dossier contient deux enveloppes natives autour de l'application web
existante. Aucune des deux ne contient de règle de jeu : elles affichent le
site `project-bsm-7d32c.web.app` en plein écran.

**Conséquence importante :** une modification de l'application web reste
disponible immédiatement, sans passer par une boutique. Seule l'enveloppe
elle-même — nom, icône, numéro de version — demande une nouvelle publication.
En pratique, on ne republie presque jamais.

---

## Android — prêt à envoyer

### Ce qui est déjà fait

| | |
|---|---|
| Projet | `android/` — *Trusted Web Activity*, la méthode officielle de Google |
| Identifiant | `com.bravosierraevents.bsemedical` |
| Version | 1.0.0 (`versionCode` 1) |
| Compilé pour | Android 16 (API 36), fonctionne à partir d'Android 5 |
| Clé de signature | `android/bse-medical-upload.jks`, créée, **non versionnée** |
| Paquet signé | `android/app/build/outputs/bundle/release/app-release.aab` (3,6 Mo) |
| Pour essayer avant | `android/app/build/outputs/apk/release/app-release.apk` |
| Visuels de la fiche | `android/boutique/` — icône 512 et bannière 1024×500 |

Pour recompiler après une modification :

```bash
cd android && ./gradlew :app:bundleRelease
```

### ⚠️ La clé de signature

`android/bse-medical-upload.jks` et `android/keystore.properties` ne sont ni
versionnés ni sauvegardés ailleurs. **Copiez-les dès maintenant** sur une clé
USB ou dans un gestionnaire de mots de passe. Sans eux, plus aucune mise à
jour de l'enveloppe n'est possible sans passer par une procédure de
réinitialisation chez Google.

### Les étapes qui vous reviennent

1. **Compte développeur Google Play** — 25 € une seule fois, à vie.
   À créer vous-même sur `play.google.com/console`.

2. **Choisissez bien le type de compte.** Un compte **personnel** créé
   aujourd'hui impose de réunir **12 testeurs pendant 14 jours consécutifs**
   avant toute publication publique. Un compte **organisation** (au nom de
   l'association) en est dispensé, mais réclame un numéro D-U-N-S, gratuit et
   obtenu en quelques jours. Pour un club d'airsoft, le compte organisation
   évite un mois de blocage.

3. **Créez l'application** dans la console, puis envoyez `app-release.aab`.

4. **Récupérez la deuxième empreinte — l'étape qu'on oublie.**
   Google resigne votre paquet avec sa propre clé. L'empreinte déjà publiée
   dans `.well-known/assetlinks.json` est celle de *votre* clé, qui ne vaut
   que pour l'APK installé à la main. Il faut y ajouter celle de Google :

   Console Play → *Test et version* → *Intégrité de l'application* →
   *Certificat de clé de signature d'application* → copiez le **SHA-256**.

   Ajoutez-le dans `.well-known/assetlinks.json` à côté de l'existant, puis
   redéployez le site. **Tant que ce n'est pas fait, l'application téléchargée
   depuis le Play Store s'ouvre avec la barre d'adresse du navigateur** — elle
   fonctionne, mais elle ne ressemble plus à une application.

   Vérification une fois en ligne :
   `https://developers.google.com/digital-asset-links/tools/generator`

5. **Fiche de la boutique** : icône et bannière sont dans `android/boutique/`.
   Il faut aussi 2 à 8 captures d'écran de téléphone, un texte court
   (80 caractères) et un texte long.

6. **Formulaire « Sécurité des données »** — à remplir honnêtement. Ce que
   l'application collecte réellement :
   - un identifiant Firebase anonyme, créé par l'appareil, rattaché à aucun
     compte ni adresse e-mail ;
   - le pseudo choisi par le joueur et son équipe, uniquement pendant une
     partie en ligne ;
   - le journal de la partie (tirages, soins), effacé à la clôture.

   Aucune publicité, aucun traceur, aucune revente, aucune localisation.

7. **Politique de confidentialité** : les deux boutiques l'exigent, sous forme
   d'une page web publique. Elle n'existe pas encore — voir plus bas.

---

## iOS — faisable, mais deux obstacles réels

### Obstacle 1 : un Mac est obligatoire

Apple n'autorise la compilation et l'envoi d'une application iOS que depuis
macOS avec Xcode. **Cela ne se contourne pas depuis Windows.** Trois sorties :

- un Mac emprunté, le temps d'un envoi (quelques heures suffisent) ;
- un Mac dans le nuage : **Codemagic** ou **GitHub Actions** (coureurs macOS)
  compilent et envoient sans posséder de machine — c'est l'option la plus
  réaliste ici, et elle peut rester gratuite sur de petits volumes ;
- l'achat d'un Mac, difficile à justifier pour cet usage.

### Obstacle 2 : la règle 4.2 d'Apple

Apple refuse les applications qui ne sont « qu'un site web empaqueté ». Le
risque de rejet est **réel, sans être automatique** : ce qui fait pencher la
balance, c'est l'utilité propre et le fonctionnement hors réseau — deux points
que l'application a pour elle. Si un rejet tombe, l'argument à avancer est le
fonctionnement complet en mode avion, le mode multijoueur local et l'usage
professionnel sur le terrain.

Compter **99 € par an**, tant que l'application reste publiée.

### Ce qui est déjà écrit

| | |
|---|---|
| Projet | `ios/` — SwiftUI + WKWebView plein écran |
| Identifiant | `com.bravosierraevents.bsemedical` |
| iOS minimum | 15.0 |
| Points traités | magasin de données persistant (hors réseau), autorisation caméra pour le scanner de QR, liens externes ouverts dans Safari, barre d'état et fond à la charte |

**À savoir : ce code n'a jamais été compilé.** Je n'ai pas de compilateur Swift
sur cette machine — c'est du code écrit avec soin, pas du code vérifié. Prévoir
un aller-retour de mise au point au premier passage sur Mac.

### Sur le Mac

```bash
brew install xcodegen
cd ios && xcodegen generate
open BSEMedical.xcodeproj
```

Puis renseigner l'équipe de développement dans *Signing & Capabilities*,
choisir *Any iOS Device*, et *Product → Archive*.

---

## Ce qui reste à faire avant de pouvoir publier

1. **Une politique de confidentialité**, obligatoire des deux côtés. Je peux en
   rédiger une page factuelle à partir de ce que l'application fait réellement
   (liste au point 6 plus haut) et la mettre en ligne sur le site — à faire
   relire par quelqu'un de l'association avant publication.
2. Les **captures d'écran** des fiches de boutique.
3. Le **choix du type de compte Google Play**, qui décide d'un mois d'attente.

---

## Faut-il vraiment passer par les boutiques ?

À poser franchement : l'application s'installe déjà sur l'écran d'accueil des
deux systèmes, fonctionne hors réseau et se met à jour toute seule. Les
boutiques apportent la visibilité, la confiance d'un lien officiel, et une
installation en un geste au lieu d'une explication au briefing.

Elles coûtent 25 € une fois côté Google, 99 € par an côté Apple, plus le délai
de validation. Si le but est seulement d'équiper les joueurs d'un événement,
le QR code vers le site reste plus rapide. Si le but est de faire connaître
BSE Medical System au-delà du club, la boutique a du sens — et dans ce cas,
commencer par Android seul est le choix raisonnable.
