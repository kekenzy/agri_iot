# RDS DB Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-db"
  
  engine         = "postgres"
  engine_version = "13.21"
  instance_class = var.db_instance_class
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  parameter_group_name = aws_db_parameter_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.project_name}-db-final-snapshot"
  
  deletion_protection = true
  
  tags = {
    Name = "${var.project_name}-db"
  }
}

# RDS DB Parameter Group
resource "aws_db_parameter_group" "main" {
  family = "postgres13"
  name   = "${var.project_name}-db-parameter-group"
  
  parameter {
    name  = "log_connections"
    value = "1"
  }
  
  parameter {
    name  = "log_disconnections"
    value = "1"
  }
  
  parameter {
    name  = "log_statement"
    value = "all"
  }
  
  tags = {
    Name = "${var.project_name}-db-parameter-group"
  }
}

# RDS DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# Secrets Manager - Database URL
# resource "aws_secretsmanager_secret" "database_url" {
#   name = "${var.project_name}/database-url"
#   
#   tags = {
#     Name = "${var.project_name}-database-url"
#   }
# }

# resource "aws_secretsmanager_secret_version" "database_url" {
#   secret_id = aws_secretsmanager_secret.database_url.id
#   secret_string = jsonencode({
#     DATABASE_URL = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}:5432/${var.db_name}"
#   })
# }

# Secrets Manager - Django Secret Key
# resource "aws_secretsmanager_secret" "secret_key" {
#   name = "${var.project_name}/secret-key"
#   
#   tags = {
#     Name = "${var.project_name}-secret-key"
#   }
# }

# resource "aws_secretsmanager_secret_version" "secret_key" {
#   secret_id = aws_secretsmanager_secret.secret_key.id
#   secret_string = random_password.secret_key.result
# }

# Random password for Django secret key
resource "random_password" "secret_key" {
  length  = 50
  special = true
} 