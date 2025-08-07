from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialisation d'environ
env = environ.Env(
    DEBUG=(bool, True)
)

# Chargement du fichier .env
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

# Sécurité
SECRET_KEY = env('SECRET_KEY', default='django-insecure-fake-key-dev')
DEBUG = env('DEBUG')
# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
# ALLOWED_HOSTS = ['angnewa.onrender.com', 'localhost', '127.0.0.1']
#ALLOWED_HOSTS = ['angnewa.onrender.com']
ALLOWED_HOSTS = ['*']

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'angnewa.urls'

# Templates
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / "templates"],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'angnewa.wsgi.application'

# Base de données (SQLite en local, PostgreSQL en production)
if env('DATABASE_URL', default=None):
    DATABASES = {
        'default': env.db(),  # lit la variable DATABASE_URL automatiquement
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Ajouté pour Render ou production

# Fichiers média (upload)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'core.Utilisateur'

# Sécurité HTTPS (production uniquement)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600  # à augmenter si besoin
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
