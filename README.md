# 🚀 DevOps Project — Flask API on Kubernetes (AWS)

> **Master d'Excellence en Intelligence Artificielle — FSBM, Université Hassan II de Casablanca**
> Projet de fin de module DevOps · 2025–2026

[![CI/CD Pipeline](https://github.com/assan23/devops-project/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/assan23/devops-project/actions)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-✓-blue)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28-blue)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/Terraform-AWS-purple)](https://www.terraform.io/)

---

## 📋 Description

Ce projet démontre la mise en place d'une **infrastructure DevOps complète** :

- **Application** : API REST Flask (Gestionnaire de tâches Todo avec interface web)
- **Conteneurisation** : Docker + Gunicorn (serveur WSGI de production)
- **Orchestration** : Kubernetes avec `livenessProbe` / `readinessProbe`
- **CI/CD** : GitHub Actions (3 jobs : Tests → Build Docker → Déploiement K8s)
- **Infrastructure as Code** : Terraform (AWS EC2 master + worker)
- **Configuration Management** : Ansible (installation Docker, Kubernetes, Flannel)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Actions CI/CD                  │
│   ┌──────────┐   ┌──────────────┐   ┌───────────────┐  │
│   │ 🧪 Test  │──▶│ 🐳 Docker    │──▶│ 🚀 K8s Deploy │  │
│   │ pytest   │   │ Build & Push │   │ Rolling Update│  │
│   └──────────┘   └──────────────┘   └───────────────┘  │
└──────────────────────────────┬──────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Docker Hub        │
                    │  assan23/flask-app   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────▼────────────────────┐
          │          AWS EC2 — Terraform             │
          │  ┌─────────────┐   ┌─────────────────┐  │
          │  │  Master K8s │   │   Worker K8s    │  │
          │  │  t3.medium  │   │   t3.micro      │  │
          │  └──────┬──────┘   └────────┬────────┘  │
          │  Ansible (Docker + K8s + Flannel CNI)    │
          └─────────────────────────────────────────┘
```

---

## 📡 Endpoints de l'API

| Route | Méthode | Description |
|---|---|---|
| `/` | GET | Interface web du gestionnaire de tâches |
| `/about` | GET | Page de présentation du projet |
| `/health` | GET | Healthcheck (utilisé par les probes K8s) |
| `/add` | POST | Ajouter une nouvelle tâche |
| `/toggle/<id>` | POST | Basculer le statut complété/non complété |
| `/delete/<id>` | POST | Supprimer une tâche |
| `/edit/<id>` | GET | Formulaire de modification |
| `/update/<id>` | POST | Enregistrer la modification |
| `/api/tasks` | GET | Liste toutes les tâches (JSON) |
| `/api/tasks/<id>` | GET | Détails d'une tâche (JSON) |
| `/api/stats` | GET | Statistiques globales (JSON) |

---

## 🛠️ Lancer en local

```bash
# 1. Cloner le projet
git clone https://github.com/assan23/devops-project.git
cd devops-project

# 2. Installer les dépendances
pip install -r app/requirements.txt

# 3. Lancer l'application
python app/app.py
```

➡️ Ouvrir http://localhost:5000

---

## 🐳 Lancer avec Docker

```bash
# Build de l'image
docker build -t flask-devops-app ./app

# Lancer le conteneur
docker run -p 5000:5000 flask-devops-app

# Vérifier le healthcheck
curl http://localhost:5000/health
```

---

## ✅ Exécuter les tests

```bash
cd app
python -m pytest test_app.py -v
```

Les tests couvrent :
- ✅ Page d'accueil, `/about`, `/health`
- ✅ API REST (liste, stats, 404)
- ✅ CRUD complet : ajout, toggle, suppression, modification
- ✅ Validation des données (tâche vide ignorée)

---

## ☁️ Déploiement Kubernetes

```bash
# Appliquer les manifests Kubernetes
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Vérifier le déploiement
kubectl get pods -l app=flask-api
kubectl rollout status deployment/flask-api-deployment
```

---

## 🏗️ Infrastructure Terraform (AWS)

```bash
# Initialiser Terraform
terraform init

# Vérifier le plan
terraform plan

# Appliquer (crée master + worker EC2)
terraform apply

# Récupérer les IPs des instances
terraform output
```

> ⚠️ **Sécurité** : Modifier la variable `allowed_cidr` dans `variables.tf`
> pour restreindre l'accès SSH à votre IP fixe avant tout déploiement en production.

---

## ⚙️ Configuration Ansible

```bash
# 1. Mettre à jour les IPs dans ansible/inventory (depuis terraform output)
# 2. Installer Docker sur tous les noeuds
ansible-playbook -i ansible/inventory ansible/install_docker.yml

# 3. Installer Kubernetes sur tous les noeuds
ansible-playbook -i ansible/inventory ansible/install_kubernetes.yml

# 4. Initialiser le master et configurer Flannel (CNI)
ansible-playbook -i ansible/inventory ansible/setup_master.yml
```

---

## 🔒 Sécurité

- Les secrets (clé SSH, `KUBECONFIG`, token Docker Hub) sont stockés dans les **GitHub Actions Secrets**, jamais en dur dans le code.
- Le fichier `ansible/inventory` contient des **placeholders** au lieu d'IPs réelles.
- Le serveur de développement Flask est remplacé par **Gunicorn** dans le Dockerfile de production.
- L'accès SSH AWS est paramétrable via la variable Terraform `allowed_cidr`.

---

## 👥 Auteurs

- Hassan EL HADI
- BERRIMA Meriem
- AMEJOUD Hasnae
- BENTAIB Hajar

---

## 📄 Rapport

Le rapport complet (45 pages) est disponible dans [`Rapport.pdf`](./Rapport.pdf).
