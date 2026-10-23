output "master_public_ip" {
  description = "Adresse IP publique du noeud master Kubernetes"
  value       = aws_instance.master.public_ip
}

output "worker_public_ip" {
  description = "Adresse IP publique du noeud worker Kubernetes"
  value       = aws_instance.worker.public_ip
}

output "application_url" {
  description = "URL d'accès à l'application Flask via le NodePort Kubernetes"
  value       = "http://${aws_instance.master.public_ip}:30001"
}

output "ssh_master_command" {
  description = "Commande SSH pour se connecter au master (remplacer le nom de la clé si nécessaire)"
  value       = "ssh -i ${var.key_name}.pem ubuntu@${aws_instance.master.public_ip}"
  sensitive   = false
}
