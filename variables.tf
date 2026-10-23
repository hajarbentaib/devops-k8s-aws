variable "region" {
  description = "Région AWS pour le déploiement du cluster"
  type        = string
  default     = "eu-north-1"
}

variable "ami_id" {
  description = "AMI Ubuntu 22.04 LTS pour la région eu-north-1"
  type        = string
  default     = "ami-0028b2c25f5ca28ed"
}

variable "master_instance_type" {
  description = "Type d'instance pour le noeud master Kubernetes (2 vCPU minimum recommandé)"
  type        = string
  default     = "t3.medium"
}

variable "worker_instance_type" {
  description = "Type d'instance pour les noeuds worker Kubernetes"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Nom de la paire de clés SSH AWS (doit exister dans la région)"
  type        = string
  default     = "devops-key"
}

variable "allowed_cidr" {
  description = "CIDR autorisé pour l'accès SSH. Remplacer par votre IP en production (ex: '203.0.113.10/32')"
  type        = string
  default     = "0.0.0.0/0"  # Lab uniquement - à restreindre en production
}

variable "environment" {
  description = "Environnement de déploiement"
  type        = string
  default     = "lab"
}

variable "project_name" {
  description = "Nom du projet pour le tagging des ressources AWS"
  type        = string
  default     = "devops-flask-k8s"
}
