provider "aws" {
  region = "us-east-2"  
}

resource "aws_iam_role" "redshift_s3_access_role_team2" {
  name = "redshift-s3-access-role-team2"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "redshift.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_redshift_s3_access_team2" {
  role       = aws_iam_role.redshift_s3_access_role_team2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_security_group" "redshift_sg_team2" {
  name        = "redshift-sg-team2"
  description = "Allow Redshift access"
  vpc_id      = "vpc-0a6676cdce3346e5d" 

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restrict to your IP for security
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_redshift_subnet_group" "redshift_subnet_group_team2" {
  name       = "redshift-subnet-group-team2"
  subnet_ids = ["subnet-0eb61b98a8ca52777", "subnet-0d27852c5f3c3eda9"]  
}

resource "aws_redshift_cluster" "redshift_team2" {
  cluster_identifier = "redshift-cluster-sales-data-team2"
  node_type          = "ra3.xlplus"
  number_of_nodes    = 1
  database_name      = "sales_data_redshift_team2"
  master_username    = "adminuser"
  master_password    = "Adminuser123" 
  iam_roles          = [aws_iam_role.redshift_s3_access_role_team2.arn]
  cluster_subnet_group_name = aws_redshift_subnet_group.redshift_subnet_group_team2.name
  vpc_security_group_ids     = [aws_security_group.redshift_sg_team2.id]
  publicly_accessible        = true
  skip_final_snapshot        = true
  automated_snapshot_retention_period = 1
}

output "redshift_endpoint" {
  value = aws_redshift_cluster.redshift_team2.endpoint
}
