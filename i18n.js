/* =========================================================
   BSE MEDICAL SYSTEM — TRADUCTIONS
   Charge avant l'application. Fournit window.I18N et le
   raccourci window.t().

   Comment ca marche
   -----------------
   Le francais est la langue de reference : ce sont ses textes
   qui servent de CLE pour tout le vocabulaire des cartes
   (zones, gravites, materiel, titres, protocoles, bilans).
   Les donnees de jeu ne sont donc JAMAIS traduites sur place —
   DB_REGLES garde ses chaines francaises, qui restent les cles
   internes utilisees par la logique de tirage, par Firebase et
   par les paquets enregistres. Seul l'affichage passe par une
   table de correspondance. Changer de langue ne peut donc pas
   casser une partie en cours ni un paquet deja sauvegarde.

   Les textes d'interface, eux, ont des cles nommees (ui.*).

   Ajouter une langue : ajouter son entree dans BSE_LANGUES,
   son drapeau dans le sprite SVG de index.html (symbol id
   « f-xx »), et son catalogue plus bas. Une cle absente
   retombe sur le francais, jamais sur du vide.
   ========================================================= */

(function () {
    'use strict';

    var CLE_STOCKAGE = 'bse-langue';

    // L'ordre est celui du menu deroulant.
    var LANGUES = [
        { code: 'fr', nom: 'Français', drapeau: 'f-fr' },
        { code: 'en', nom: 'English',       drapeau: 'f-gb' },
        { code: 'de', nom: 'Deutsch',       drapeau: 'f-de' },
        { code: 'es', nom: 'Español',  drapeau: 'f-es' },
        { code: 'it', nom: 'Italiano',      drapeau: 'f-it' },
        { code: 'zh', nom: '中文',  drapeau: 'f-cn' },
        { code: 'ja', nom: '日本語', drapeau: 'f-jp' }
    ];

    // Tables indexees par le texte francais d'origine.
    var TABLES = ['zone', 'grav', 'mat', 'membre', 'titre', 'soin', 'bilan'];

    var CAT = {};
    var courante = 'fr';

    function cherche(cat, cle) {
        if (!cat) return undefined;
        if (cat.ui && cat.ui[cle] !== undefined) return cat.ui[cle];
        var i = cle.indexOf('.');
        if (i > 0) {
            var prefixe = cle.slice(0, i);
            if (TABLES.indexOf(prefixe) >= 0) {
                var table = cat[prefixe];
                if (table && table[cle.slice(i + 1)] !== undefined) return table[cle.slice(i + 1)];
            }
        }
        return undefined;
    }

    // {nom} dans le texte est remplace par params.nom.
    function interpole(texte, params) {
        if (!params) return texte;
        return String(texte).replace(/\{(\w+)\}/g, function (tout, nom) {
            return params[nom] !== undefined ? params[nom] : tout;
        });
    }

    /* Traduit une cle. Ordre de repli : langue courante, puis
       francais, puis — pour les tables — le texte francais porte
       par la cle elle-meme (« zone.Torse » donne « Torse »).
       Une cle inconnue ressort telle quelle plutot que vide :
       un texte en trop se voit, un texte manquant ne se voit pas. */
    function t(cle, params) {
        if (cle === null || cle === undefined) return '';
        var v = cherche(CAT[courante], cle);
        if (v === undefined) v = cherche(CAT.fr, cle);
        if (v === undefined) {
            var i = cle.indexOf('.');
            v = (i > 0 && TABLES.indexOf(cle.slice(0, i)) >= 0) ? cle.slice(i + 1) : cle;
        }
        return interpole(v, params);
    }

    // Raccourcis pour le vocabulaire des cartes.
    function tab(prefixe) {
        return function (valeur, params) {
            if (valeur === null || valeur === undefined || valeur === '') return valeur;
            return t(prefixe + '.' + valeur, params);
        };
    }

    /* Traduit un protocole compose (« Bandage + Morphine ») dont
       la phrase complete n'est pas au catalogue : chaque terme est
       traduit separement. Sert de filet pour les paquets crees par
       les joueurs, dont le texte reste evidemment tel qu'ecrit. */
    function tSoin(texte) {
        if (!texte) return texte;
        var direct = cherche(CAT[courante], 'soin.' + texte);
        if (direct !== undefined) return direct;
        if (courante === 'fr') return texte;
        var morceaux = String(texte).split(' + ');
        if (morceaux.length < 2) return texte;
        var traduits = morceaux.map(function (m) {
            var terme = m.trim();
            var v = cherche(CAT[courante], 'mat.' + terme);
            if (v === undefined) v = cherche(CAT[courante], 'soin.' + terme);
            return v === undefined ? terme : v;
        });
        return traduits.join(' + ');
    }

    function appliquerDOM(racine) {
        var r = racine || document;
        r.querySelectorAll('[data-i18n]').forEach(function (el) {
            el.textContent = t(el.getAttribute('data-i18n'));
        });
        r.querySelectorAll('[data-i18n-html]').forEach(function (el) {
            el.innerHTML = t(el.getAttribute('data-i18n-html'));
        });
        r.querySelectorAll('[data-i18n-ph]').forEach(function (el) {
            el.setAttribute('placeholder', t(el.getAttribute('data-i18n-ph')));
        });
        r.querySelectorAll('[data-i18n-title]').forEach(function (el) {
            el.setAttribute('title', t(el.getAttribute('data-i18n-title')));
        });
        r.querySelectorAll('[data-i18n-aria]').forEach(function (el) {
            el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria')));
        });
    }

    function detecter() {
        var sauve = null;
        try { sauve = localStorage.getItem(CLE_STOCKAGE); } catch (e) {}
        if (sauve && CAT[sauve]) return sauve;
        var nav = (navigator.language || navigator.userLanguage || 'fr').slice(0, 2).toLowerCase();
        return CAT[nav] ? nav : 'fr';
    }

    function definir(code, silencieux) {
        if (!CAT[code]) code = 'fr';
        courante = code;
        try { localStorage.setItem(CLE_STOCKAGE, code); } catch (e) {}
        document.documentElement.setAttribute('lang', code);
        appliquerDOM();
        // L'application redessine ses ecrans dynamiques (fiches, listes,
        // menus deroulants) : ils sont construits en JS, hors data-i18n.
        if (!silencieux && typeof window.onLangueChangee === 'function') {
            try { window.onLangueChangee(code); } catch (e) { console.warn('onLangueChangee', e); }
        }
    }

    window.BSE_I18N = CAT;
    window.I18N = {
        langues: function () { return LANGUES.slice(); },
        langue: function () { return courante; },
        infos: function (code) {
            var c = code || courante;
            for (var i = 0; i < LANGUES.length; i++) if (LANGUES[i].code === c) return LANGUES[i];
            return LANGUES[0];
        },
        definir: definir,
        appliquerDOM: appliquerDOM,
        // Appele une fois les catalogues charges (fin de ce fichier).
        demarrer: function () { definir(detecter(), true); },
        t: t,
        zone: tab('zone'),
        grav: tab('grav'),
        mat: tab('mat'),
        membre: tab('membre'),
        titre: tab('titre'),
        bilan: tab('bilan'),
        soin: tSoin
    };
    // Expose sous le nom « tr » : « t » est deja pris comme variable locale
    // dans une trentaine d'endroits de l'application (equipes, onglets...).
    window.tr = t;
})();


/* =========================================================
   FRANCAIS — catalogue de reference.
   Les tables zone/grav/mat/membre/titre/soin/bilan sont
   absentes : en francais la cle EST le texte.
   ========================================================= */
window.BSE_I18N.fr = {
ui: {
    /* --- En-tete --- */
    'hdr.multijoueur': 'Multijoueur',
    'hdr.quitter': 'Quitter la partie',
    'hdr.sortir': 'Sortir',
    'hdr.paquets': 'Mes paquets',
    'hdr.reglages': 'Réglages',
    'hdr.bseLien': 'Bravo Sierra Events — ouvrir le site',
    'hdr.bseAria': 'Ouvrir le site de Bravo Sierra Events',
    'social.discord': 'Bravo Sierra Events sur Discord',
    'social.instagram': 'Bravo Sierra Events sur Instagram',
    'social.youtube': 'Bravo Sierra Events sur YouTube',
    'social.facebook': 'Bravo Sierra Events sur Facebook',
    'statut.solo': 'Solo',
    'statut.organisateur': 'Organisateur',
    'statut.coadmin': 'Co-admin',
    'statut.reconnexion': '{nom} · Reconnexion à la partie…',
    'paquet.balistique': 'Balistique',
    'paquet.explosion': 'Explosion',

    /* --- Accueil --- */
    'jeu.titre': 'Diagnostic médical',
    'jeu.sous': 'Cliquez pour lancer le diagnostic',
    'jeu.paquetActif': 'Paquet actif',
    'jeu.chargement': 'Chargement...',
    'jeu.cartes': '{n} cartes',

    /* --- Bilan MARCH --- */
    'march.titre': 'Bilan MARCH',
    'march.m': 'Massive bleeding',
    'march.a': 'Airways',
    'march.r': 'Respiration',
    'march.c': 'Circulation',
    'march.h': 'Head / Hypothermia',
    'march.analyse': 'Analyse en cours…',

    /* --- Silhouette --- */
    'sil.titre': 'Zone touchée ?',
    'sil.sous': 'Touchez la partie du corps atteinte',
    'sil.miroir': '(vue en miroir : son bras droit est à votre gauche)',

    /* --- Fiche de triage --- */
    'fiche.mort': 'Mort au combat',
    'fiche.mortSous': 'Temps écoulé — hémorragie fatale',
    'fiche.fermer': 'Fermer le dossier',
    'fiche.label': 'Fiche de triage',
    'fiche.zone': 'Zone touchée',
    'fiche.bilan': 'Bilan',
    'fiche.protocole': 'Protocole de soin',
    'fiche.hemorragie': 'Hémorragie active — urgence vitale',
    'fiche.nouveau': 'Nouveau diagnostic',
    'fiche.soigner': 'Soins effectués (sauver)',
    'fiche.stabilise': 'PATIENT STABILISÉ !',
    'fiche.protPortee': 'Protection balistique portée : {reponse}',
    'fiche.avecProtection': ' avec protection portée',

    /* --- Boutons communs --- */
    'btn.annuler': 'Annuler',
    'btn.valider': 'Valider',
    'btn.fermer': 'Fermer',
    'btn.retour': 'Retour',
    'btn.copier': 'Copier',
    'btn.ouvrir': 'Ouvrir',
    'btn.oui': 'Oui',
    'btn.non': 'Non',

    /* --- QG de l'organisateur --- */
    'qg.titre': 'QG',
    'qg.partie': 'Partie',
    'qg.enLigne': 'En ligne',
    'qg.ongletInvitation': 'Invitation',
    'qg.ongletJoueurs': 'Joueurs',
    'qg.ongletEquipes': 'Équipes',
    'qg.ongletEditeur': 'Éditeur',
    'qg.ongletPaquets': 'Paquets',
    'qg.ongletLogs': 'Logs',
    'qg.codeAide': 'Code de la partie — à dicter aux joueurs',
    'qg.lienAide': 'Lien de connexion (partage ou QR)',
    'qg.qrGeneration': 'Génération...',
    'qg.qrAide': 'Les joueurs scannent le QR code ou tapent le nom de la partie dans le menu Rejoindre.',
    'qg.joueurs': 'JOUEURS',
    'qg.equipes': 'ÉQUIPES DE LA PARTIE',
    'qg.nomEquipePh': 'Nom équipe',
    'qg.couleurEquipePh': '#hex couleur',
    'qg.ajouterEquipe': '+ ÉQUIPE',
    'qg.editeur': 'ÉDITEUR DE PAQUETS',
    'qg.editeurAide': 'Ajustez les quantités, le matériel et le risque de mort pour tous vos paquets avant de les distribuer.',
    'qg.paquetsAttribues': 'PAQUETS ATTRIBUÉS',
    'qg.paquetsAide1': 'Choisissez ce que chaque joueur va tirer : Classique, Avancé, Extrême, Explosion ou l’un de vos paquets perso. Le paquet attribué <b>remplace</b> le tirage du mode chez le destinataire — il ne verra que celui-là, avec les quantités réglées dans l’Éditeur.',
    'qg.paquetsAide2': 'Un joueur sans aucune attribution joue le <b>mode en cours</b> défini dans l’Éditeur.',
    'qg.toutLeMonde': 'Tout le monde',
    'qg.uneEquipe': 'Une équipe seulement',
    'qg.unJoueur': 'Un joueur seulement',
    'qg.ajouterPaquet': 'Ajouter ce paquet',
    'qg.journal': 'JOURNAL TEMPS RÉEL',
    'qg.journalAide': 'Les événements d’un joueur s’affichent avec le nom et la couleur de son équipe.',
    'qg.telechargerLogs': 'Télécharger les logs (.txt)',
    'qg.effacerAffichage': 'Effacer l’affichage',
    'qg.cloturer': 'Clôturer la partie (éjecter les joueurs)',
    'qg.retourSession': 'Retour accueil (garder la session)',

    /* --- Reglages --- */
    'reg.titre': 'Réglages système',
    'reg.profil': 'Profil multijoueur',
    'reg.pseudo': 'Votre pseudo de joueur',
    'reg.pseudoPh': 'Ex : Doc',
    'reg.mode': 'Mode de jeu',
    'reg.hardcore': 'Option hardcore',
    'reg.activerMort': 'Activer le risque de mort',
    'reg.proba': 'Probabilité',
    'reg.probaSous': 'sur une blessure éligible',
    'reg.delaiMin': 'Délai mini',
    'reg.delaiMinSous': 'avant le décès',
    'reg.delaiMax': 'Délai maxi',
    'reg.etendreGraves': 'Étendre aux blessures Graves',
    'reg.explosion': 'Explosion',
    'reg.activerExplosion': 'Activer les cartes explosion',
    'reg.materiel': 'Matériel requis',
    'reg.cartesActives': 'Cartes actives',
    'reg.catalogue': 'Catalogue',
    'reg.oeilAide': 'L’œil de chaque ligne ouvre le catalogue du mode à la carte concernée.',
    'reg.aide': 'Aide',
    'reg.aideTexte': 'Le guide d’utilisation complet, à lire au briefing. Il reste consultable hors ligne une fois ouvert.',
    'reg.guide': 'Guide d’utilisation (PDF)',

    /* --- Selecteur de langue --- */
    'lang.titre': 'Langue',
    'lang.choisir': 'Choisir la langue',

    /* --- Mes paquets --- */
    'bld.titre': 'Mes paquets',
    'bld.sous': 'Créez vos propres paquets de cartes et affichez-les sur l’accueil.',
    'bld.creer': '+ Créer un paquet',
    'bld.importer': 'Importer un paquet',
    'bld.edition': 'Édition du paquet',
    'bld.nom': 'Nom du paquet',
    'bld.nomPh': 'Ex : Blessures chimiques',
    'bld.afficherAccueil': 'Afficher sur l’accueil',
    'bld.modeExtreme': 'Mode extrême',
    'bld.modeExtremeSous': '(silhouette : zone touchée + protection)',
    'bld.icone': 'Icône du bouton',
    'bld.iconeAide': 'Elle identifie le paquet sur l’écran d’accueil et chez les joueurs à qui vous l’attribuez.',
    'bld.cartes': 'Cartes',
    'bld.ajouterCarte': '+ Ajouter une carte',
    'bld.enregistrer': 'Enregistrer',
    'bld.supprimerPaquet': 'Supprimer le paquet',

    /* --- Edition d'une carte --- */
    'ce.titreEcran': 'Carte',
    'ce.gravite': 'Gravité',
    'ce.titre': 'Titre',
    'ce.titrePh': 'Ex : Fracture',
    'ce.zone': 'Zone touchée',
    'ce.zonePh': 'Ex : Bras',
    'zoneOpt.tete': 'Tête',
    'zoneOpt.torse': 'Torse',
    'zoneOpt.teteTorse': 'Tête ou torse',
    'zoneOpt.brasD': 'Bras droit',
    'zoneOpt.brasG': 'Bras gauche',
    'zoneOpt.bras': 'Les deux bras',
    'zoneOpt.jambeD': 'Jambe droite',
    'zoneOpt.jambeG': 'Jambe gauche',
    'zoneOpt.jambes': 'Les deux jambes',
    'zoneOpt.membres': 'Les quatre membres',
    'zoneOpt.libre': 'Zone personnalisée…',
    'zoneOpt.aideGroupe': 'Une seule carte suffit : la zone exacte est tirée au sort, et en mode Extrême c’est celle touchée sur la silhouette.',
    'zoneOpt.aideLibre': 'Écrivez la zone de votre choix. Elle s’affiche telle quelle, et la carte peut sortir sur n’importe quelle zone en mode Extrême.',
    'ce.protocole': 'Protocole / effet',
    'ce.protocolePh': 'Ex : Attelle + Morphine',
    'ce.matos': 'Matériel requis',
    'ce.matosAide': 'Touchez une puce pour la sélectionner. Le matériel ajouté ici n’est proposé que dans ce paquet (✕ pour le retirer).',
    'ce.nouveauMatosPh': 'Nouveau matériel (ex : Anti-rad)',
    'ce.valider': 'Valider la carte',

    /* --- Modales --- */
    'mod.apercu': 'Aperçu',
    'multi.titre': 'Menu multijoueur',
    'multi.nomPartie': 'Nom de la partie (hôte)',
    'multi.nomPartiePh': 'Ex : Exercice Alpha',
    'multi.pseudoHote': 'Pseudo de l’hôte',
    'multi.pseudoHotePh': 'Ex : Orga',
    'multi.liaison': 'Liaison entre appareils',
    'multi.firebase': 'Serveur Firebase (recommandé)',
    'multi.peer': 'Pair-à-pair (ancien)',
    'multi.aideFirebase': 'Passe par le serveur : fonctionne entre réseaux différents (4G / WiFi), et vous pouvez fermer votre page sans couper la partie.',
    'multi.aidePeer': 'Connexion directe entre appareils. Nécessite souvent un relais TURN, et votre page doit rester ouverte.',
    'multi.creer': 'Créer une partie (hôte)',
    'multi.rejoindre': 'Rejoindre une partie',
    'multi.scanner': 'Scanner le QR code',
    'multi.codePh': 'Nom de la partie ou lien',
    'multi.connexion': 'Connexion',
    'multi.testerReseau': 'Tester le réseau',
    'multi.turn': 'Relais réseau (TURN) — optionnel',
    'multi.turnAide': 'Nécessaire si le test indique ❌ TURN et que vos joueurs sont sur d’autres réseaux (4G, autre WiFi). Créez un compte gratuit sur <b>metered.ca</b> (50 Go/mois), ajoutez un « TURN server » et collez ses identifiants ici. Ils seront transmis automatiquement aux joueurs via le lien / QR code d’invitation.',
    'multi.turnUrlPh': 'URL (ex : turn:standard.relay.metered.ca:443)',
    'multi.turnUserPh': 'Username',
    'multi.turnPassPh': 'Password / credential',
    'multi.turnSave': 'Enregistrer le relais',
    'multi.statut': 'Connexion...',

    'join.titre': 'Rejoindre la partie',
    'join.etabli': 'Connexion établie.',
    'join.pseudo': 'Votre pseudo',
    'join.equipe': 'Votre équipe',

    'prot.question': 'Protection balistique portée ?',
    'prot.casque': 'Casque balistique porté ?',
    'prot.gilet': 'Gilet pare-balles porté ?',

    'share.titre': 'Partager le paquet',

    'leave.titre': 'Quitter la partie ?',
    'leave.texte': 'Vous quitterez la session multijoueur et reviendrez au menu principal.',
    'leave.oui': 'Oui, quitter',

    /* --- Modes et paquets --- */
    'mode.classique': 'Classique',
    'mode.avance': 'Avancé',
    'mode.extreme': 'Extrême',
    'mode.explosion': 'Explosion',
    'mode.perso': 'Perso',
    'mode.plusExplosion': ' + explosion',
    'reg.modeClassique': 'CLASSIQUE',
    'reg.modeAvance': 'AVANCÉ',
    'reg.modeExtreme': 'EXTRÊME (silhouette)',
    'reg.custom': '{nom} (Custom)',
    'reg.aucunMateriel': 'Aucun matériel requis pour ce mode ou cette sélection.',
    'reg.voirCarte': 'Voir la carte',
    'reg.packExplosion': 'Pack explosion',
    'reg.verrouille': 'Paramètres verrouillés par l’hôte',

    /* --- Catalogue des cartes --- */
    'cat.titre': 'Catalogue — {mode}',
    'cat.sectionMode': 'Mode',
    'cat.sectionPerso': 'Paquet perso',
    'cat.sectionExplosion': 'Explosion',
    'cat.protPortee': 'protection portée',
    'cat.sansProt': 'sans protection',
    'cat.matos': 'Matos :',
    'cat.aucuneCarte': 'Aucune carte pour ce mode.',
    'carte.membreAleatoire': 'membre aléatoire',

    /* --- Boutons communs (suite) --- */
    'btn.modifier': 'Modifier',
    'btn.partager': 'Partager',
    'btn.supprimer': 'Supprimer',

    /* --- Mes paquets (dynamique) --- */
    'bld.nouveauPaquet': 'Nouveau paquet',
    'bld.sansNom': 'Paquet sans nom',
    'bld.sansTitre': 'Sans titre',
    'bld.masque': 'Masqué',
    'bld.surAccueil': 'Sur l’accueil',
    'bld.aucunPaquet': 'Aucun paquet personnalisé pour le moment.',
    'bld.aucunPaquetAide': 'Appuyez sur « + CRÉER UN PAQUET » pour commencer.',
    'bld.aucuneCarte': 'Aucune carte dans ce paquet.',
    'bld.aucuneCarteAide': 'Appuyez sur « + AJOUTER UNE CARTE ».',
    'bld.nMateriel': '{n} matériel(s)',
    'bld.enPartieTitre': 'Partie en cours.',
    'bld.enPartieTexte': 'Vous jouez les paquets attribués par l’organisateur. Vos paquets personnels sont mis de côté et vous seront rendus dès que vous quitterez la partie.',
    'bld.bloqueEnPartie': 'Impossible pendant une partie : la configuration vient de l’organisateur et votre paquet serait effacé.\n\nQuittez la partie pour retrouver et modifier vos paquets personnels.',
    'bld.confirmSupprCarte': 'Supprimer la carte « {nom} » ?',
    'bld.confirmSupprPaquet': 'Supprimer le paquet « {nom} » et toutes ses cartes ?',
    'ce.donnezTitre': 'Donnez un titre à la carte.',
    'ce.confirmRetirerMatos': 'Retirer « {nom} » de ce paquet ? Il sera aussi retiré des cartes qui l’utilisent.',

    /* --- Partage de paquets --- */
    'share.exportTitre': 'Partager « {nom} »',
    'share.exportAide': 'Envoyez ce code à un autre joueur (SMS, WhatsApp, mail...). Il l’importera via « IMPORTER UN PAQUET » dans Mes paquets.',
    'share.copierCode': 'COPIER LE CODE',
    'share.importAide': 'Collez ici le code de partage reçu (il commence par TMDECK1).',
    'share.importer': 'IMPORTER',
    'share.codeCopie': 'Code copié !',
    'share.codeInvalide': 'Code invalide ou incomplet. Vérifiez qu’il a été copié en entier.',
    'share.paquetImporte': 'Paquet importé',
    'share.importeOk': 'Paquet « {nom} » importé ({n} cartes) !',

    /* --- Icones de paquet --- */
    'icone.cartes': 'Cartes',
    'icone.blesse': 'Blessé',
    'icone.souffle': 'Souffle',
    'icone.balle': 'Balle',
    'icone.reticule': 'Réticule',
    'icone.lame': 'Lame',
    'icone.grenade': 'Grenade',
    'icone.bombe': 'Bombe',
    'icone.explosion': 'Explosion',
    'icone.feu': 'Feu',
    'icone.decharge': 'Décharge',
    'icone.froid': 'Froid',
    'icone.biohazard': 'Biohazard',
    'icone.radiation': 'Radiation',
    'icone.toxique': 'Toxique',
    'icone.masqueGaz': 'Masque à gaz',
    'icone.zombie': 'Zombie',
    'icone.creature': 'Créature',
    'icone.robot': 'Robot',
    'icone.crane': 'Crâne',
    'icone.seringue': 'Seringue',
    'icone.cachets': 'Cachets',
    'icone.perfusion': 'Perfusion',
    'icone.pouls': 'Pouls',
    'icone.fracture': 'Fracture',
    'icone.trousse': 'Trousse',
    'icone.protection': 'Protection',

    /* --- QG (dynamique) --- */
    'qg.ligneMode': 'Mode : {nom}',
    'qg.lignePerso': 'Perso : {nom}',
    'qg.joue': 'JOUÉ',
    'qg.minEquipes': '(min. 2 équipes)',
    'qg.horsLigne': 'hors ligne',
    'qg.reviendra': 'Reviendra automatiquement…',
    'qg.retirer': 'Retirer',
    'qg.admin': 'Admin',
    'qg.kick': 'Kick',
    'qg.retirerPaquet': 'Retirer ce paquet',
    'qg.cibleEquipe': 'Équipe {nom}',
    'qg.cibleJoueur': 'Joueur {nom}',
    'qg.aucunPaquetDistribue': 'Aucun paquet distribué.',
    'qg.aucunPaquetDistribueAide': 'Les joueurs n’ont que le tirage Balistique.',
    'qg.paquetVide': 'Ce paquet est vide pour la configuration actuelle.',
    'qg.dejaAttribueCible': '« {nom} » est déjà attribué à cette cible.',
    'qg.dejaAttribueTous': '« {nom} » est déjà attribué à tout le monde : inutile de le redonner à une équipe ou à un joueur.',
    'qg.indiquezNomEquipe': 'Indiquez un nom d’équipe.',
    'qg.deuxEquipesMini': 'Il faut au moins deux équipes.',
    'qg.choisirEquipe': 'Choisissez une équipe.',
    'qg.choisirJoueur': 'Choisissez un joueur (connecté).',
    'qg.aucunLog': 'Aucun log à télécharger.',
    'qg.logEntete': 'journal de partie',
    'qg.logExporte': 'Exporté le',
    'qg.confirmCloture': 'Clôturer la partie ? Tous les joueurs seront avertis et déconnectés.',
    'qg.confirmClotureTous': 'Clôturer la partie pour tout le monde ?',
    'qg.qrIndisponible': 'QR indisponible.',
    'qg.qrIndisponibleAide': 'Partagez le lien ou le nom de la partie.',
    'qg.qrAlt': 'QR code d’invitation',

    /* --- Journal de partie --- */
    'log.partieOuverte': 'Partie ouverte : {code}',
    'log.aRejoint': '{nom} a rejoint',
    'log.sEstReconnecte': '{nom} s’est reconnecté',
    'log.quitteLaPartie': '{nom} quitte la partie',
    'log.joueurDeconnecte': '{nom} déconnecté (en attente de reconnexion)',
    'log.pseudoDejaPris': 'Pseudo « {demande} » déjà utilisé : ce joueur devient « {retenu} »',
    'log.sessionDemarree': 'Session hôte démarrée : {code}',
    'log.sessionReprise': 'Session reprise : {code}',
    'log.configModifiee': '{nom} (co-admin) a modifié la configuration',
    'log.ajoutRefuse': 'Ajout refusé ({nom}) : {raison}',
    'log.tirage': '{nom} · tirage : {carte} [{gravite}] · {source}',
    'log.coadmin': '{nom} · co-admin : {valeur}',
    'log.retireDeLaPartie': 'Retiré de la partie : {nom}',
    'log.partieCloturee': 'Partie clôturée.',
    'log.partieClotureePar': 'Partie clôturée par {nom} (co-admin).',
    'qg.logEquipeAjoutee': 'Équipe ajoutée : {nom}',
    'qg.logEquipeSupprimee': 'Équipe supprimée, joueurs réassignés.',
    'qg.logPaquetDistribue': 'Paquet distribué : {nom} → {cible}',
    'qg.logRemplaceParTous': '{nom} : {n} attribution(s) ciblée(s) remplacée(s) par « tout le monde »',

    /* --- Multijoueur (etats) --- */
    'multi.joueur': 'Joueur',
    'multi.orga': 'Orga',
    'multi.ouverture': 'Ouverture de la partie...',
    'multi.ouvertureImpossible': 'Ouverture impossible.',
    'multi.creation': 'Création de la partie...',
    'multi.reprise': 'Reprise de la partie...',
    'multi.recherche': 'Recherche de la partie...',
    'multi.connexionReseau': 'Connexion réseau en cours...',
    'multi.recuperation': 'Récupération des données...',
    'join.partieNommee': 'Partie « {nom} »',

    /* --- Test reseau --- */
    'net.testEnCours': 'Test en cours (~15 s)...',
    'net.ligneSignalisation': 'Mise en relation (serveur PeerJS)',
    'net.ligneStun': 'STUN — connexion directe possible',
    'net.ligneTurn': 'TURN — relais si le direct est bloqué',
    'net.aucunRelais': '(aucun relais configuré)',
    'net.relaisEnregistre': 'Relais enregistré. Il sera utilisé pour les prochaines connexions et transmis aux joueurs via le lien / QR code.',
    'net.relaisEfface': 'Relais effacé.',
    'net.verdictOk': 'Tout est opérationnel : la connexion devrait marcher, même entre réseaux différents (4G ↔ box).',
    'net.verdictSansTurn': 'Pas de relais TURN : la connexion peut échouer entre réseaux différents ou si la box isole ses appareils. Configurez un relais ci-dessous (Relais réseau), il sera transmis aux joueurs par le QR code.',
    'net.verdictStunBloque': 'STUN bloqué alors qu’Internet fonctionne : c’est presque toujours le NAVIGATEUR qui bloque l’UDP de WebRTC.<br>• <b>Opera / Opera GX</b> : désactivez le VPN intégré, puis dans les réglages cherchez « WebRTC » et choisissez « Utiliser l’UDP sans proxy ».<br>• Sinon : VPN, antivirus ou pare-feu. Testez dans Chrome ou Edge pour confirmer.<br>• Un relais TURN configuré passe aussi par TCP 443 et contourne souvent ce blocage.',
    'net.verdictWebrtcOff': 'WebRTC est entièrement désactivé dans ce navigateur (aucun candidat réseau). Vérifiez les réglages de confidentialité du navigateur ou essayez-en un autre.',
    'net.verdictPasDeSignalisation': 'Serveur de mise en relation injoignable : vérifiez l’accès Internet.',

    /* --- Messages --- */
    'msg.paquetIndisponible': 'Ce paquet n’est plus disponible.',
    'msg.aucunPaquetMode': 'Aucun paquet de cartes pour ce mode. Vérifiez les réglages ou le paquet personnalisé.',
    'msg.aucuneCarteMateriel': 'Aucune carte disponible. Vérifiez que vous avez le matériel requis (Réglages).',
    'msg.aucuneCarteZone': 'Aucune carte disponible pour cette zone{etat}.\n\nVérifiez les quantités et le matériel disponible dans les Réglages.',
    'msg.avecProtection': ' avec protection portée',
    'msg.sansProtection': ' sans protection',
    'msg.lienCopie': 'Lien d’invitation copié.',
    'msg.codeCopie': 'Code de la partie copié :',
    'msg.partiePasOuverte': 'La partie n’est pas encore ouverte.',
    'msg.scannerIndisponible': 'Scanner QR indisponible (librairie non chargée — vérifiez la connexion Internet).',
    'msg.peerIndisponible': 'Multijoueur indisponible (librairie PeerJS non chargée — vérifiez la connexion Internet).',
    'msg.firebaseIndisponible': 'Le multijoueur Firebase n’est pas disponible (bibliothèque absente).',
    'msg.droitsOrga': 'Modification refusée : vous n’avez pas les droits d’organisateur sur cette partie.',
    'msg.devenuCoOrga': 'Vous êtes co-organisateur : le QG de la partie est accessible via le bouton multijoueur, en haut à droite.',
    'msg.gradeRetire': 'Grade admin retiré.',
    'msg.retireDeLaPartie': 'Vous avez été retiré de la partie.',
    'msg.exclu': 'Vous avez été exclu de la partie.',
    'msg.orgaACloture': 'L’organisateur a clôturé la partie.',
    'msg.partieTerminee': 'La partie est terminée.',
    'msg.nomPartiePris': 'Une partie porte déjà ce nom et appartient à quelqu’un d’autre. Choisissez un autre nom.',
    'msg.nomPartieDejaPris': 'Ce nom de partie est déjà utilisé (ou l’ancienne session n’a pas encore expiré). Attendez une minute ou changez de nom.',
    'msg.partieIntrouvable': 'Partie introuvable. Vérifiez le nom auprès de l’organisateur.',
    'msg.partieIntrouvableHote': 'La partie est introuvable. Vérifiez que l’Hôte n’a pas fermé sa page web ou annulé la partie.',
    'msg.partieCloturee': 'Cette partie est clôturée.',
    'msg.erreurPeer': 'Erreur PeerJS',
    'msg.repriseImpossible': 'Reprise de la partie « {nom} » impossible pour le moment ({raison}). Nouvel essai au prochain retour sur la page, ou recréez la partie avec le même nom pour retrouver vos joueurs.',
    'msg.dejaHote': 'Vous hébergez déjà une partie sur cet appareil. Quittez l’ancienne partie via l’interface Hôte pour pouvoir en rejoindre une autre en tant que joueur.',
    'msg.indiquezNomPartie': 'Indiquez le nom de la partie ou scannez le QR code.',
    'msg.indiquezPseudo': 'Indiquez un pseudo : c’est le nom sous lequel l’organisateur vous verra dans la partie.',
    'msg.delaiDepasse': 'Délai dépassé : la liaison avec l’Hôte n’a pas pu s’établir. Vérifiez que sa page est ouverte, puis lancez « Tester le réseau » dans le menu multijoueur : si TURN est en échec, l’hôte doit configurer un relais (« Relais réseau ») — il sera transmis automatiquement par son QR code.',
    'msg.hoteIntrouvable': 'Connexion impossible : hôte introuvable ou réseau instable.',
    'msg.connexionImpossible': 'Connexion impossible.',
    'msg.connexionPerdue': 'Connexion perdue. Réessayez de rejoindre la partie.',
    'msg.connexionPerdueHote': 'Connexion à l’hôte perdue.',
    'msg.reconnexionImpossible': 'Reconnexion impossible : la partie semble terminée ou l’hôte injoignable.',
    'msg.connecte': 'Connecté à la partie !',
    'msg.pseudoRemplace': 'Ce pseudo était déjà pris dans la partie. Vous y apparaissez sous : {nom}',
    'msg.changementEquipe': 'Changement d’équipe'
}
};
