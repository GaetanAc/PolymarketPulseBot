# Polymarket Discord Trade Notifier 🚀

Un bot Python qui **surveille les traders sur Polymarket** et envoie des notifications sur Discord dès qu’un trade notable est détecté.  
Il priorise les liens vers le marché (via `slug`) et fournit toutes les informations clés du trade.

---

## Fonctionnalités principales

- Surveillance en temps réel des traders définis.
- Notifications Discord détaillées pour chaque trade :
  - Nom du trader
  - Montant investi en USDC
  - Direction (Buy / Sell)
  - Prix d’exécution / Odds
  - Marché concerné avec lien direct
- Filtrage automatique des trades trop petits (< 5 USDC).
- Liens prioritaires vers le marché via `slug`, fallback vers PolygonScan si nécessaire.
- Gestion des erreurs et déconnexions de l’API Polymarket.

---

## Prérequis

- Python 3.10 ou supérieur
- Une **webhook Discord** pour recevoir les notifications
- Une **Alchemy RPC URL** pour interroger la blockchain Polygon
- Installer les dépendances Python

```bash
pip install aiohttp python-dotenv
```
Installation et configuration

Cloner le dépôt :

Installation et configuration
```
git clone https://github.com/votre-utilisateur/PolymarketPulseBot.git
cd polymarket-discord-notifier
```
Créer un fichier .env à la racine avec vos variables :

```
DISCORD_WEBHOOK=https://discord.com/api/webhooks/xxx/yyy
ALCHEMY_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/votre_clef
```
Modifier la liste des traders à surveiller dans le fichier Python (TRADERS_TO_WATCH) :
```
TRADERS_TO_WATCH = [
    "0x6a72f61820b26b1fe4d956e17b6dc2a1ea3033ee",   # Exemple : kch123
    "0xdc876e6873772d38716fda7f2452a78d426d7ab6",  # Exemple : 432614799197
]
```
Ajuster la fréquence de sondage si nécessaire :

```
POLL_INTERVAL = 1  # en secondes
```
Utilisation

Lancer le bot :

```
PolymarketPulseBot.py
```

Le bot :

  Affiche dans la console les trades détectés.

  Envoie automatiquement les notifications sur Discord.

  Priorise les liens vers le marché via slug et fournit un fallback vers PolygonScan si nécessaire.


Contribution : 

  Les contributions sont les bienvenues !

Vous pouvez proposer :

  Ajout de nouvelles fonctionnalités (ex : filtrage par montant, multi-serveurs Discord)

  Optimisation des requêtes API

  Amélioration des messages Discord (embeds, mentions, etc.)


Notes : 

  Le bot utilise l’API publique de Polymarket et peut être limité si trop de requêtes sont envoyées.

  Vérifier que le webhook Discord et l’Alchemy RPC URL sont actifs avant de lancer le bot.

  Les trades inférieurs à 5 USDC sont ignorés pour éviter le spam.

