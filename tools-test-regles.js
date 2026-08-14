/* Valide les regles de securite contre la base REELLE, avec deux comptes
   anonymes distincts : A cree la partie (orga), B rejoint (joueur simple). */
const https = require('https');
const KEY = 'AIzaSyDMohnSPAJwkefm9q5hUrLdzLxriS9KyQE';
const DB = 'project-bsm-7d32c-default-rtdb.europe-west1.firebasedatabase.app';
const PARTIE = 'TM32-TESTREGLES';

const req = (opts, body) => new Promise((res) => {
  const r = https.request(opts, (rp) => {
    let d = ''; rp.on('data', c => d += c);
    rp.on('end', () => res({ status: rp.statusCode, body: d }));
  });
  r.on('error', e => res({ status: 0, body: e.message }));
  if (body) r.write(body);
  r.end();
});

const connexionAnonyme = async () => {
  const body = JSON.stringify({ returnSecureToken: true });
  const r = await req({ hostname: 'identitytoolkit.googleapis.com', path: `/v1/accounts:signUp?key=${KEY}`,
    method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': body.length } }, body);
  const j = JSON.parse(r.body);
  return { uid: j.localId, token: j.idToken };
};

const ecrire = (chemin, data, token, methode = 'PUT') => {
  const body = JSON.stringify(data);
  const q = token ? `?auth=${token}` : '';
  return req({ hostname: DB, path: `/${chemin}.json${q}`, method: methode,
    headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) } }, body);
};
const lire = (chemin, token) => req({ hostname: DB, path: `/${chemin}.json${token ? '?auth=' + token : ''}`, method: 'GET' });

const resultats = [];
const verifie = (nom, attendu, reponse) => {
  const autorise = reponse.status >= 200 && reponse.status < 300;
  const ok = (attendu === 'AUTORISE') === autorise;
  resultats.push({ ok, nom, attendu, obtenu: autorise ? 'AUTORISE' : `REFUSE (${reponse.status})` });
};

(async () => {
  const A = await connexionAnonyme();   // orga
  const B = await connexionAnonyme();   // joueur simple
  console.log('orga   :', A.uid);
  console.log('joueur :', B.uid, '\n');

  // Nettoyage prealable via A (admin apres creation) — ignore si absent
  await ecrire(`parties/${PARTIE}`, null, A.token, 'DELETE');

  // 1. Lecture sans authentification
  verifie('Lecture sans authentification', 'REFUSE', await lire(`parties/${PARTIE}`, null));

  // 2. A cree la partie et se declare hote
  verifie('Creation de la partie par l\'orga', 'AUTORISE', await ecrire(`parties/${PARTIE}`, {
    meta: { nom: 'Test regles', hoteUid: A.uid, creeLe: Date.now() },
    config: { mode: 'extreme', deathRisk: false },
    joueurs: { [A.uid]: { nom: 'Orga', teamId: 'orga', enLigne: true } }
  }, A.token));

  // 3. B lit la partie
  verifie('Lecture par un joueur authentifie', 'AUTORISE', await lire(`parties/${PARTIE}/config`, B.token));

  // 4. B inscrit sa propre fiche
  verifie('Joueur inscrit sa propre fiche', 'AUTORISE',
    await ecrire(`parties/${PARTIE}/joueurs/${B.uid}`, { nom: 'Joueur', teamId: 'blue', enLigne: true }, B.token));

  // 5. B tente de se promouvoir co-admin  <-- LA faille de la phase 2
  verifie('Joueur s\'auto-promeut co-admin', 'REFUSE',
    await ecrire(`parties/${PARTIE}/joueurs/${B.uid}`, { nom: 'Joueur', teamId: 'blue', isCoHost: true }, B.token));

  // 6. B tente de reecrire la configuration de la partie
  verifie('Joueur reecrit la configuration', 'REFUSE',
    await ecrire(`parties/${PARTIE}/config`, { mode: 'classique', deathRisk: true }, B.token));

  // 7. B tente d'ecrire la fiche de l'orga
  verifie('Joueur modifie la fiche d\'un autre', 'REFUSE',
    await ecrire(`parties/${PARTIE}/joueurs/${A.uid}`, { nom: 'Pirate', teamId: 'red' }, B.token));

  // 8. B tente de changer l'hote de la partie
  verifie('Joueur s\'attribue meta/hoteUid', 'REFUSE',
    await ecrire(`parties/${PARTIE}/meta/hoteUid`, B.uid, B.token));

  // 9. B ajoute une ligne au journal
  const ajout = await ecrire(`parties/${PARTIE}/logs`, { ts: Date.now(), texte: 'tirage : Hemorragie', auteur: 'Joueur' }, B.token, 'POST');
  verifie('Joueur ajoute une ligne au journal', 'AUTORISE', ajout);
  const idLog = ajout.status < 300 ? JSON.parse(ajout.body).name : 'inexistant';

  // 10. B tente de reecrire une ligne deja inscrite
  verifie('Joueur reecrit une ligne du journal', 'REFUSE',
    await ecrire(`parties/${PARTIE}/logs/${idLog}`, { ts: Date.now(), texte: 'efface' }, B.token));

  // 11. B tente d'effacer tout le journal
  verifie('Joueur efface le journal', 'REFUSE', await ecrire(`parties/${PARTIE}/logs`, null, B.token, 'DELETE'));

  // 12. B tente de supprimer la partie
  verifie('Joueur supprime la partie', 'REFUSE', await ecrire(`parties/${PARTIE}`, null, B.token, 'DELETE'));

  // 13. Champ inconnu refuse
  verifie('Champ inconnu dans une fiche', 'REFUSE',
    await ecrire(`parties/${PARTIE}/joueurs/${B.uid}`, { nom: 'Joueur', porteDerobee: 'oui' }, B.token));

  // 14. Nom demesure refuse
  verifie('Nom de joueur de 200 caracteres', 'REFUSE',
    await ecrire(`parties/${PARTIE}/joueurs/${B.uid}`, { nom: 'x'.repeat(200) }, B.token));

  // 15. L'orga promeut B co-admin
  verifie('Orga promeut un joueur co-admin', 'AUTORISE',
    await ecrire(`parties/${PARTIE}/joueurs/${B.uid}/isCoHost`, true, A.token));

  // 16. Devenu co-admin, B peut maintenant ecrire la configuration
  verifie('Co-admin reecrit la configuration', 'AUTORISE',
    await ecrire(`parties/${PARTIE}/config`, { mode: 'avance', deathRisk: true }, B.token));

  // 17. L'orga exclut B
  verifie('Orga exclut un joueur', 'AUTORISE', await ecrire(`parties/${PARTIE}/joueurs/${B.uid}`, null, A.token, 'DELETE'));

  // 18. Exclu, B ne peut plus ecrire au journal
  verifie('Joueur exclu ecrit au journal', 'REFUSE',
    await ecrire(`parties/${PARTIE}/logs`, { ts: Date.now(), texte: 'revenge' }, B.token, 'POST'));

  // 19. L'orga cloture (supprime) la partie
  verifie('Orga cloture la partie', 'AUTORISE', await ecrire(`parties/${PARTIE}`, null, A.token, 'DELETE'));

  console.log('RESULTATS\n' + '-'.repeat(72));
  resultats.forEach(r => console.log(`${r.ok ? '  OK  ' : ' ECHEC'} | ${r.nom.padEnd(42)} | ${r.obtenu}`));
  const ko = resultats.filter(r => !r.ok);
  console.log('-'.repeat(72));
  console.log(`${resultats.length - ko.length}/${resultats.length} conformes`);
  if (ko.length) { console.log('\nNON CONFORMES :'); ko.forEach(r => console.log(`  ${r.nom} — attendu ${r.attendu}, obtenu ${r.obtenu}`)); process.exit(1); }
})();
