/* Banc d'essai du service worker.
       node tools-test-sw.js            teste sw.js
       node tools-test-sw.js autre.js   teste une autre version

   On charge sw.js dans un environnement simule et on declenche la requete
   de navigation avec un reseau qui, tour a tour, repond, echoue, renvoie une
   erreur, ou reste suspendu. Ce qu'on verifie :
     - l'application s'ouvre INSTANTANEMENT des qu'elle est en cache, quel que
       soit l'etat du reseau (c'est le reseau suspendu qui la bloquait sur
       iPhone, et le simple fait de l'attendre qui la ralentissait) ;
     - une reponse d'erreur ne remplace jamais la version en cache ;
     - la version fraiche est bien rangee en cache pour l'ouverture suivante. */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SRC = path.join(__dirname, 'sw.js');
const code = fs.readFileSync(process.argv[2] || SRC, 'utf8');

function faireResponse(corps, init) {
    init = init || {};
    return { corps, status: init.status === undefined ? 200 : init.status,
             ok: (init.status === undefined ? 200 : init.status) < 400,
             clone() { return faireResponse(corps, init); },
             __marque: init.__marque };
}

function environnement(comportementReseau, contenuCache) {
    const cache = new Map(contenuCache);
    const ecouteurs = {};
    const self = {
        addEventListener: (nom, fn) => { (ecouteurs[nom] = ecouteurs[nom] || []).push(fn); },
        location: { origin: 'https://exemple.test' },
        skipWaiting: async () => {},
        clients: { claim: async () => {} },
    };
    const sandbox = {
        self, console,
        setTimeout, clearTimeout,
        URL,
        Response: function (corps, init) { return faireResponse(corps, init); },
        Request: function (url, opts) { return { url, mode: 'navigate', method: 'GET', ...opts }; },
        fetch: comportementReseau,
        caches: {
            open: async () => ({
                match: async (cle) => cache.get(typeof cle === 'string' ? cle : cle.url),
                put: async (cle, rep) => { cache.set(typeof cle === 'string' ? cle : cle.url, rep); },
                add: async () => {}, keys: async () => [],
            }),
            keys: async () => [], delete: async () => true,
        },
    };
    vm.createContext(sandbox);
    vm.runInContext(code, sandbox);
    return { ecouteurs, cache, sandbox };
}

// opt.cacheVide : premiere visite, rien n'est encore enregistre.
// opt.cacheAttendu : marque attendue dans le cache une fois le reseau retombe.
async function jouer(nom, comportementReseau, attenduMs, attenduMarque, opt) {
    opt = opt || {};
    const CACHE = opt.cacheVide ? [] : [['./index.html', faireResponse('PAGE EN CACHE', { __marque: 'cache' })]];
    const { ecouteurs, cache } = environnement(comportementReseau, CACHE);
    const req = { url: 'https://exemple.test/', mode: 'navigate', method: 'GET' };
    let promesse = null;
    const event = { request: req, respondWith: (p) => { promesse = p; }, waitUntil: (p) => { if (p && p.catch) p.catch(() => {}); } };
    const t0 = Date.now();
    ecouteurs.fetch.forEach((fn) => fn(event));
    // Chien de garde : sans lui, un service worker qui ne repond jamais
    // fait simplement mourir le processus, sans rien dire.
    const rep = await Promise.race([
        promesse,
        new Promise((r) => setTimeout(() => r({ __marque: 'JAMAIS DE REPONSE' }), 8000)),
    ]);
    const ms = Date.now() - t0;
    const marque = rep.__marque || rep.corps;
    const okDelai = attenduMs === null ? true : Math.abs(ms - attenduMs) <= 700;
    const okSource = marque === attenduMarque || String(marque).includes(attenduMarque);
    // Le telechargement de fond continue apres la reponse : on lui laisse le
    // temps d'aboutir avant de regarder ce qui a ete range en cache.
    let okCache = true, dansCache = '';
    if (opt.cacheAttendu) {
        await new Promise((r) => setTimeout(r, 200));
        const c = cache.get('./index.html');
        dansCache = c ? (c.__marque || c.corps) : '(vide)';
        okCache = dansCache === opt.cacheAttendu;
    }
    const ok = okDelai && okSource && okCache;
    console.log((ok ? 'OK    ' : 'ECHEC ') + nom.padEnd(38) + String(ms).padStart(5) + ' ms  ->  '
                + marque + (opt.cacheAttendu ? '   [cache : ' + dansCache + ']' : ''));
    return ok;
}

(async () => {
    const resultats = [];
    const fraiche = async () => faireResponse('PAGE FRAICHE', { __marque: 'reseau' });
    // 1. Reseau normal : ouverture immediate depuis le cache, et la version
    //    fraiche est rangee pour la prochaine ouverture.
    resultats.push(await jouer('reseau normal', fraiche, 0, 'cache', { cacheAttendu: 'reseau' }));
    // 2. Hors ligne franc.
    resultats.push(await jouer('hors ligne (echec immediat)', async () => { throw new Error('offline'); }, 0, 'cache'));
    // 3. Erreur serveur : ne doit jamais remplacer le cache.
    resultats.push(await jouer('serveur en erreur 404', async () => faireResponse('PAS TROUVE', { status: 404, __marque: 'erreur' }), 0, 'cache',
                               { cacheAttendu: 'cache' }));
    // 4. LE CAS DU TERRAIN : le reseau accepte mais ne repond jamais.
    //    C'est lui qui empechait l'application de se lancer sur iPhone.
    resultats.push(await jouer('reseau suspendu (portail captif)', () => new Promise(() => {}), 0, 'cache'));
    // 5. Reseau tres lent : l'ouverture ne l'attend pas une seconde.
    resultats.push(await jouer('reseau lent (5 s)', () => new Promise((r) => setTimeout(() => r(faireResponse('LENTE', { __marque: 'reseau' })), 5000)), 0, 'cache'));
    // 6. Toute premiere visite : rien en cache, le reseau est la seule source.
    resultats.push(await jouer('premiere visite (cache vide)', fraiche, 0, 'reseau', { cacheVide: true }));
    // 7. Premiere visite sans reseau : il faut le dire, pas rester suspendu.
    resultats.push(await jouer('premiere visite hors ligne', async () => { throw new Error('offline'); }, 0, 'indisponible hors ligne', { cacheVide: true }));

    const total = resultats.filter(Boolean).length;
    console.log('\n%d / %d scenarios conformes', total, resultats.length);
    process.exit(total === resultats.length ? 0 : 1);
})();
