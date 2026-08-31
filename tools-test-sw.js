/* Banc d'essai du service worker.
       node tools-test-sw.js            teste sw.js
       node tools-test-sw.js autre.js   teste une autre version

   Banc d'essai du service worker : on charge sw.js dans un environnement
   simule et on declenche la requete de navigation avec un reseau qui,
   tour a tour, repond, echoue, renvoie une erreur, ou reste suspendu.
   C'est ce dernier cas qui bloquait l'application sur iPhone. */
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

async function jouer(nom, comportementReseau, attenduMs, attenduMarque) {
    const CACHE = [['./index.html', faireResponse('PAGE EN CACHE', { __marque: 'cache' })]];
    const { ecouteurs } = environnement(comportementReseau, CACHE);
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
    console.log(((okDelai && okSource) ? 'OK    ' : 'ECHEC ') + nom.padEnd(36) + String(ms).padStart(6) + ' ms  ->  ' + marque);
    return okDelai && okSource;
}

(async () => {
    const resultats = [];
    // 1. Reseau normal : la page fraiche gagne, tout de suite.
    resultats.push(await jouer('reseau normal', async () => faireResponse('PAGE FRAICHE', { __marque: 'reseau' }), 0, 'reseau'));
    // 2. Hors ligne franc : echec immediat, le cache prend le relais.
    resultats.push(await jouer('hors ligne (echec immediat)', async () => { throw new Error('offline'); }, 0, 'cache'));
    // 3. Erreur serveur : ne doit jamais remplacer le cache.
    resultats.push(await jouer('serveur en erreur 404', async () => faireResponse('PAS TROUVE', { status: 404, __marque: 'erreur' }), 0, 'cache'));
    // 4. LE CAS DU TERRAIN : le reseau accepte mais ne repond jamais.
    resultats.push(await jouer('reseau suspendu (portail captif)', () => new Promise(() => {}), 2500, 'cache'));
    // 5. Reseau tres lent mais qui finit par repondre : le cache sert d'abord.
    resultats.push(await jouer('reseau lent (5 s)', () => new Promise((r) => setTimeout(() => r(faireResponse('LENTE', { __marque: 'reseau' })), 5000)), 2500, 'cache'));

    const total = resultats.filter(Boolean).length;
    console.log('\n%d / %d scenarios conformes', total, resultats.length);
    process.exit(total === resultats.length ? 0 : 1);
})();
