# SMA PocketTrader AI — Prototype V1

Prototype d'analyse + simulation + contrôle Telegram.

## Ce que fait V1
- analyse de bougies OHLC synthétiques;
- tendance, structure, support/résistance, price action, momentum, volatilité;
- décision CALL / PUT / WAIT;
- score 0–100;
- payout et seuil de rentabilité théorique;
- gestion du risque et limites quotidiennes;
- choix d'expiration candidate;
- journal CSV;
- commandes Telegram;
- simulation uniquement.

## Sécurité
Aucune exécution réelle sur Pocket Option n'est incluse. La couche d'exécution est volontairement verrouillée. Une future exécution réelle devra reposer sur un mécanisme officiellement autorisé par la plateforme.

## Installation
Python 3.11+ recommandé.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/Termux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Commandes Telegram: `/start`, `/status`, `/analyze`, `/simulate`, `/stats`, `/pause`, `/resume`, `/stop`.

Le score V1 n'est pas un taux de réussite prouvé. Le futur Learning Engine devra estimer les performances à partir d'un historique réel et suffisamment large.
