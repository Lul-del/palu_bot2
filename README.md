# PaluBot 🦟

Bot Telegram de lutte contre le paludisme — triage, rappels, centres de santé.

## Déploiement sur Render (Web Service)

### 1. Variables d'environnement à configurer sur Render

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Token du bot Telegram (obtenu via @BotFather) |
| `SAMU_NUMBER` | Numéro d'urgence local (défaut : 166) |
| `WEBHOOK_URL` | URL publique de ton service Render, ex: `https://palubot.onrender.com` |

### 2. Commandes Render

- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Type** : Web Service

### 3. Après le déploiement

Une fois déployé, Render te donne une URL du type `https://palubot.onrender.com`.
Copie cette URL dans la variable d'environnement `WEBHOOK_URL` et redéploie.
Le bot enregistrera automatiquement son webhook au démarrage.

### 4. Développement local

```bash
cp .env.example .env
# Remplis .env avec ton token
pip install -r requirements.txt
uvicorn main:app --reload
```

> En local, utilise [ngrok](https://ngrok.com) pour exposer le port et renseigner le WEBHOOK_URL.
