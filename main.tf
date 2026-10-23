provider "aws" {
  region = var.region
}

# ============================================================
# Security Groups
# ============================================================

resource "aws_security_group" "k8s_sg" {
  name        = "k8s-cluster-sg"
  description = "Security group pour le cluster Kubernetes (environnement de lab)"

  # SSH - restreint à une IP spécifique en production
  # IMPORTANT : remplacer 0.0.0.0/0 par votre IP fixe avant toute utilisation en production
  ingress {
    description = "SSH (lab uniquement - restreindre en production)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  # HTTP - accès à l'application Flask via NodePort
  ingress {
    description = "HTTP - Application Flask"
    from_port   = 30001
    to_port     = 30001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Communication interne du cluster Kubernetes (API Server)
  ingress {
    description = "Kubernetes API Server"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Trafic interne entre les noeuds du cluster
  ingress {
    description = "Trafic interne cluster"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  egress {
    description = "Tout le trafic sortant autorisé"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "k8s-cluster-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ============================================================
# Instances EC2
# ============================================================

resource "aws_instance" "master" {
  ami                    = var.ami_id
  instance_type          = var.master_instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.k8s_sg.id]

  # Stockage racine suffisant pour le master Kubernetes
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name        = "kubernetes-master"
    Role        = "master"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_instance" "worker" {
  ami                    = var.ami_id
  instance_type          = var.worker_instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.k8s_sg.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name        = "kubernetes-worker"
    Role        = "worker"
    Environment = var.environment
    Project     = var.project_name
  }
}
