# IoT Virtual Weather Station (MQTT + Plotly)
## Description
Ce projet simule une station météo virtuelle connectée à un broker MQTT public. Un script Python génère des données de capteur (température, humidité, pression, qualité de l’air), les publie périodiquement vers le cloud via MQTT, puis affiche un dashboard temps réel avec Plotly (courbes + jauge). Le système illustre également le contrôle inverse (downlink) : des commandes MQTT permettent de changer le mode de fonctionnement (normal / éco) et le seuil d’alerte de température, ce qui reproduit un flux complet capteur → cloud → dashboard + commande descendante.
## Fichiers
- `weather_station_sim.py` : script Python principal (capteur virtuel + MQTT + dashboard Plotly).
- `README.md` : ce fichier.
- `images/` (optionnel) : captures d’écran du dashboard et de la console pour le rapport.
## Prérequis
- Python 3.x
- Google Colab ou environnement local (VS Code, terminal, etc.)
- Librairies Python : `pip install paho-mqtt plotly`
## Exécution dans Google Colab
1. Créer un nouveau notebook Colab.  
2. Ajouter une cellule au début avec :
   `!pip install paho-mqtt plotly`  
3. Ajouter en dessous une nouvelle cellule et y copier le contenu complet de `weather_station_sim.py`.  
4. Exécuter la cellule contenant le script :  
   - connexion au broker MQTT public `broker.hivemq.com` (port 1883),  
   - envoi régulier de mesures sur `virtual_weather_station/telemetry`,  
   - mise à jour du dashboard Plotly à chaque nouvelle mesure (courbes température / humidité + jauge de qualité de l’air).  
5. Pour arrêter la simulation : bouton stop sur Colab ou Ctrl+C en local.
## Fonctionnalités
- Simulation de capteur météo virtuel : température (°C), humidité (%), pression (hPa), indice de qualité de l’air (0–100) simulés.
- Dashboard interactif (Plotly) : courbe de température (axe Y gauche) et courbe d’humidité (axe Y droit) en fonction du temps, historique des 30 dernières mesures, jauge affichant la dernière valeur de qualité de l’air (vert / jaune / rouge).
- Commande descendante (downlink) via MQTT : abonnement au topic `virtual_weather_station/control`, possibilité de changer le mode (`normal` / `eco`) et de modifier le seuil d’alerte de température (°C). Quand la température dépasse le seuil, un message d’alerte apparaît dans la console.
## Configuration
Paramètres principaux en haut du script :
- `MQTT_HOST` : adresse du broker MQTT (par défaut `broker.hivemq.com`).
- `MQTT_PORT` : port du broker MQTT (par défaut `1883`).
- `DATA_TOPIC` : topic de télémétrie (`virtual_weather_station/telemetry`).
- `CONTROL_TOPIC` : topic de commande descendante (`virtual_weather_station/control`).
- `CLIENT_ID` : identifiant MQTT de la station virtuelle.
- `PUBLISH_INTERVAL_NORMAL` : intervalle d’envoi en mode normal (secondes).
- `PUBLISH_INTERVAL_ECO` : intervalle d’envoi en mode éco (secondes).
- `TEMP_ALERT_THRESHOLD` : seuil initial d’alerte de température (°C).


