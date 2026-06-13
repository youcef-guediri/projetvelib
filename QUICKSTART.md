# 🚀 Guide de Démarrage Rapide

Ce guide vous permet de lancer le dashboard Vélib' en quelques minutes.

## ⚡ Installation Express

### 1. Prérequis
- Python 3.11+ installé
- Terminal/PowerShell ouvert

### 2. Installation (3 commandes)

```bash
# 1. Créer un environnement virtuel
python -m venv .venv

# 2. Activer l'environnement (Windows)
.venv\Scripts\activate
# OU pour Linux/Mac:
# source .venv/bin/activate

# 3. Installer les dépendances
python -m pip install -r requirements.txt
```

### 3. Lancement

```bash
python main.py
```

### 4. Accès

Ouvrez votre navigateur à l'adresse : **http://127.0.0.1:8050**

---

## 🎯 Vérification Rapide

Si tout fonctionne, vous devriez voir :
- ✅ Dans le terminal : "Dashboard running on http://127.0.0.1:8050"
- ✅ Dans le navigateur : La page d'accueil avec les statistiques

---

## ❌ Problèmes Courants

### Erreur : "Module not found"
```bash
# Réinstaller les dépendances
python -m pip install -r requirements.txt --upgrade
```

### Erreur : "Port already in use"
```bash
# Modifier le port dans config.py
DASHBOARD_PORT = 8051  # Au lieu de 8050
```

### Erreur : "No data files found"
```bash
# Vérifier que les fichiers CSV sont présents
ls data/raw/
# Doit afficher: station_information.csv et station_statut.csv
```

---

## 📚 Documentation Complète

Pour plus de détails, consultez le [README.md](README.md) complet.

---

## 🆘 Support

En cas de problème :
1. Vérifier les logs dans le terminal
2. Consulter le README.md
3. Vérifier que Python 3.11+ est installé : `python --version`