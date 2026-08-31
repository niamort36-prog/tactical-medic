/* =========================================================
   BSE MEDICAL SYSTEM — SERVICE WORKER
   Objectif : l'application doit s'ouvrir et fonctionner en solo
   sans aucun reseau (terrain sans couverture). Tout ce dont
   l'application a besoin est mis en cache a la premiere visite.

   index.html se met a jour tout seul (reseau d'abord). En revanche,
   si un fichier de APP_SHELL change — bibliotheque de vendor/, image,
   icone — il faut incrementer CACHE_VERSION : c'est la seule chose qui
   remplace ces fichiers sur les telephones deja equipes.
   ========================================================= */

const CACHE_VERSION = 'bse-medic-v7';

/* Delai laisse au reseau avant de servir le cache.
   Sur un telephone, « pas de reseau » est rarement une coupure franche : le
   WiFi du terrain repond mais ne mene nulle part, la 4G est a une barre, ou
   iOS relance l'application avant d'avoir retabli la connexion. Un fetch sans
   limite reste alors suspendu tres longtemps et l'application ne se lance pas
   du tout. Passe ce delai on sert la version en cache ; le telechargement
   continue en arriere-plan et servira au lancement suivant. */
const DELAI_RESEAU = 2500;

function avecDelai(promesse, ms) {
    return new Promise((tenir, rejeter) => {
        const minuteur = setTimeout(() => rejeter(new Error('delai reseau depasse')), ms);
        promesse.then(
            (v) => { clearTimeout(minuteur); tenir(v); },
            (e) => { clearTimeout(minuteur); rejeter(e); }
        );
    });
}

// Tout ce qui compose l'application. Chemins relatifs : l'application
// fonctionne aussi bien a la racine d'un domaine que dans un sous-dossier.
const APP_SHELL = [
    './',
    './index.html',
    './manifest.webmanifest',
    './i18n.js',
    './lang-en.js',
    './lang-de.js',
    './lang-es.js',
    './lang-it.js',
    './lang-zh.js',
    './lang-ja.js',
    './vendor/peerjs.min.js',
    './vendor/qrcode.min.js',
    './vendor/html5-qrcode.min.js',
    './vendor/firebase-app-compat.js',
    './vendor/firebase-auth-compat.js',
    './vendor/firebase-database-compat.js',
    './fond-topo.png',
    './picto-blesse.png',
    './btn-explosion.png',
    './silhouette.png',
    './icons/icon-192.png',
    './icons/icon-512.png',
    './icons/apple-touch-icon.png',
    './icons/favicon-32.png',
    './icons/logo-bse.png',
    './icons/logo-bse-medical.png',
    './icons/logo-bse-medical@2x.png',
    './icons/logo-bse@2x.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil((async () => {
        const cache = await caches.open(CACHE_VERSION);
        // addAll echoue en bloc si un seul fichier manque : on tolere les
        // absences pour qu'une image renommee ne casse pas l'installation.
        await Promise.all(APP_SHELL.map(url =>
            cache.add(new Request(url, { cache: 'reload' })).catch(err =>
                console.warn('[SW] non mis en cache :', url, err)
            )
        ));
        await self.skipWaiting();
    })());
});

self.addEventListener('activate', (event) => {
    event.waitUntil((async () => {
        const noms = await caches.keys();
        await Promise.all(noms.map(n => n === CACHE_VERSION ? null : caches.delete(n)));
        await self.clients.claim();
    })());
});

self.addEventListener('fetch', (event) => {
    const req = event.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);
    // On ne touche a rien d'externe : signalisation PeerJS, STUN/TURN,
    // secours QR en ligne... doivent passer directement au reseau.
    if (url.origin !== self.location.origin) return;

    // La page elle-meme : reseau d'abord, pour recuperer une mise a jour
    // des qu'il y a du reseau ; le cache prend le relais hors ligne.
    const estCatalogue = /\/(i18n|lang-[a-z]{2})\.js$/.test(url.pathname);
    if (req.mode === 'navigate' || url.pathname.endsWith('/index.html') || estCatalogue) {
        const cle = estCatalogue ? req : './index.html';
        const reseau = (async () => {
            const cache = await caches.open(CACHE_VERSION);
            const reponse = await fetch(req);
            // Une page d'erreur du serveur ne doit jamais remplacer la version
            // en cache : sinon l'application hors ligne servirait un 404.
            if (reponse && reponse.ok) cache.put(cle, reponse.clone());
            return reponse;
        })();
        // Le telechargement se poursuit meme si on a deja repondu par le cache.
        event.waitUntil(reseau.catch(() => {}));
        event.respondWith((async () => {
            try {
                const reponse = await avecDelai(reseau, DELAI_RESEAU);
                if (reponse && reponse.ok) return reponse;
                throw new Error('reponse ' + (reponse && reponse.status));
            } catch (e) {
                const cache = await caches.open(CACHE_VERSION);
                const enCache = (await cache.match(cle)) || (estCatalogue ? null : await cache.match('./'));
                if (enCache) return enCache;
                // Rien en cache : le reseau reste la seule chance, on l'attend.
                try { return await reseau; } catch (e2) {}
                return new Response(estCatalogue ? '' : 'Application indisponible hors ligne.',
                                    { status: estCatalogue ? 504 : 503,
                                      headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
            }
        })());
        return;
    }

    // Le reste (bibliotheques, images, icones) : cache d'abord, c'est
    // immediat et ca fonctionne sans reseau. Le cache est renouvele au
    // changement de CACHE_VERSION.
    event.respondWith((async () => {
        const cache = await caches.open(CACHE_VERSION);
        const enCache = await cache.match(req);
        if (enCache) return enCache;
        try {
            const reponse = await fetch(req);
            if (reponse && reponse.ok) cache.put(req, reponse.clone());
            return reponse;
        } catch (e) {
            return new Response('', { status: 504 });
        }
    })());
});
