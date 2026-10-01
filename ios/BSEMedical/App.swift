//  App.swift — BSE MEDICAL SYSTEM
//
//  Point d'entree de l'application iOS. Tout l'ecran est occupe par la vue
//  web : l'application n'a ni barre de navigation ni onglet natif, exactement
//  comme la version installee depuis Safari.

import SwiftUI

@main
struct BseMedicalApp: App {
    var body: some Scene {
        WindowGroup {
            VueWeb()
                // La charte est sombre : on l'impose, sinon iOS eclaircit les
                // barres du systeme chez les joueurs en theme clair.
                .preferredColorScheme(.dark)
                // Le bas de l'ecran appartient a la page (barre d'etat des
                // joueurs, selecteur de langue) : elle gere elle-meme ses
                // marges de securite.
                .ignoresSafeArea(edges: .bottom)
                .background(Color(red: 7/255, green: 7/255, blue: 7/255))
        }
    }
}
