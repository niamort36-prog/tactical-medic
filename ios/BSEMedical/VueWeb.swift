//  VueWeb.swift — BSE MEDICAL SYSTEM
//
//  L'application iOS affiche l'application web dans une WKWebView plein ecran.
//  Comme l'enveloppe Android, elle ne contient aucune regle de jeu : une mise
//  a jour du site est disponible immediatement, sans passer par l'App Store.
//
//  Trois points qui ne vont PAS de soi dans une WKWebView et qui sont traites
//  ici, faute de quoi l'application serait inutilisable sur le terrain :
//
//  1. Le magasin de donnees doit etre PERSISTANT. Par defaut une WKWebView
//     repart a vide : le service worker ne survivrait pas a la fermeture, et
//     l'application ne s'ouvrirait jamais sans reseau.
//  2. La camera doit etre accordee explicitement (scanner de QR code). Sans
//     la methode de delegation plus bas, iOS refuse en silence.
//  3. L'audio des bips doit pouvoir demarrer sans geste supplementaire une
//     fois le premier appui fait, d'ou allowsInlineMediaPlayback.

import SwiftUI
import WebKit
import AVFoundation

struct VueWeb: UIViewRepresentable {

    static let adresse = URL(string: "https://project-bsm-7d32c.web.app/index.html")!

    func makeCoordinator() -> Coordinateur { Coordinateur() }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()

        // Persistant : c'est ce qui permet au service worker du site de garder
        // l'application en memoire de l'appareil et de l'ouvrir hors reseau.
        config.websiteDataStore = .default()

        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []

        let vue = WKWebView(frame: .zero, configuration: config)
        vue.navigationDelegate = context.coordinator
        vue.uiDelegate = context.coordinator

        // Le fond doit etre le noir de la charte : sinon un rebond de
        // defilement laisse apparaitre du blanc.
        vue.isOpaque = false
        vue.backgroundColor = UIColor(red: 7/255, green: 7/255, blue: 7/255, alpha: 1)
        vue.scrollView.backgroundColor = vue.backgroundColor
        vue.scrollView.bounces = false

        // L'application gere son propre retour arriere (bouton Retour Android,
        // fermeture des modales) : le geste de bord ferait doublon.
        vue.allowsBackForwardNavigationGestures = false

        vue.load(URLRequest(url: VueWeb.adresse))
        return vue
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    final class Coordinateur: NSObject, WKNavigationDelegate, WKUIDelegate {

        // Scanner de QR code : iOS exige une autorisation explicite, cote
        // natif, en plus de celle du site.
        func webView(_ webView: WKWebView,
                     requestMediaCapturePermissionFor origin: WKSecurityOrigin,
                     initiatedByFrame frame: WKFrameInfo,
                     type: WKMediaCaptureType,
                     decisionHandler: @escaping (WKPermissionDecision) -> Void) {
            decisionHandler(.prompt)
        }

        // Les liens vers l'exterieur (Discord, Instagram, le site de
        // l'association) s'ouvrent dans Safari, pas dans l'application.
        func webView(_ webView: WKWebView,
                     decidePolicyFor action: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if let url = action.request.url,
               action.navigationType == .linkActivated,
               url.host != VueWeb.adresse.host {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }

        // Premiere ouverture sans reseau : le service worker n'a encore rien
        // en memoire, il n'y a rien a afficher. On le dit, et on reessaie
        // des que l'application revient au premier plan.
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            reessayer(webView)
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            reessayer(webView)
        }

        private func reessayer(_ webView: WKWebView) {
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                webView.load(URLRequest(url: VueWeb.adresse))
            }
        }
    }
}
