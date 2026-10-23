FROM python:3.12-slim

# Métadonnées de l'image
LABEL maintainer="Hassan el hadi"
LABEL description="DevOps Todo App - Flask API containerisée"
LABEL version="1.0"

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier uniquement requirements.txt d'abord (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source de l'application
COPY app.py .

# Exposer le port de l'application
EXPOSE 5000

# Healthcheck intégré à Docker (utilisé par Docker Swarm)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Utiliser Gunicorn en production (multi-process, plus robuste que le serveur de dev Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
