# 🚖 AngnéWa

AngnéWa est une plateforme de transport collaboratif conçue pour faciliter les trajets en Guinée.  
Elle permet aux chauffeurs de publier leurs trajets et aux passagers de réserver facilement.

## 🔧 Fonctionnalités

- Inscription des chauffeurs avec vérification par code
- Publication de trajets
- Réservation de places avec notification au chauffeur
- Suivi des trajets publiés
- Statistiques des trajets
- Interface responsive avec Bootstrap

## 🚀 Exécuter le projet en local

### Prérequis

- Python 3.11+ ou 3.13
- Git
- pip
- virtualenv *(optionnel mais recommandé)*

### Installation

```bash
git clone https://github.com/siradjo/angnewa.git
cd angnewa
python -m venv venv
venv\Scripts\activate   # sous Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
