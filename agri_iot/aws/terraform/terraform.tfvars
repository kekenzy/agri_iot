# AWS設定
aws_region = "ap-northeast-1"
project_name = "agri-iot"
environment = "production"

# ネットワーク設定
vpc_cidr = "10.0.0.0/16"
public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]

# データベース設定
db_username = "agri_user"
db_password = "agri_password"
db_name = "agri_db"
db_instance_class = "db.t3.micro"

# ドメイン設定（必要に応じて変更）
domain_name = "your-domain.com"
certificate_arn = "" 