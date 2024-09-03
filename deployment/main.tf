# main.tf

provider "aws" {
  region = "us-west-2"
}

# S3 Bucket for Airflow
resource "aws_s3_bucket" "airflow_bucket" {
  bucket = var.s3_bucket_name
}

# S3 Bucket Policy
resource "aws_s3_bucket_policy" "airflow_bucket_policy" {
  bucket = aws_s3_bucket.airflow_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AirflowRole"
        }
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.airflow_bucket.arn}",
          "${aws_s3_bucket.airflow_bucket.arn}/*"
        ]
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

# IAM Role for Airflow
resource "aws_iam_role" "airflow_role" {
  name = "AirflowRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM Policy for S3 Access
resource "aws_iam_policy" "s3_access_policy" {
  name        = "S3AccessPolicy"
  description = "Policy for S3 access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.airflow_bucket.arn,
          "${aws_s3_bucket.airflow_bucket.arn}/*"
        ]
      }
    ]
  })
}

# IAM Policy for Redshift Access
resource "aws_iam_policy" "redshift_access_policy" {
  name        = "RedshiftAccessPolicy"
  description = "Policy for Redshift access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "redshift:DescribeClusters",
          "redshift:GetClusterCredentials",
          "redshift:ExecuteStatement"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Policy for Glue Access
resource "aws_iam_policy" "glue_access_policy" {
  name        = "GlueAccessPolicy"
  description = "Policy for Glue access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:CreateJob",
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:GetJobRuns"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach Policies to IAM Role
resource "aws_iam_role_policy_attachment" "attach_s3_policy" {
  role       = aws_iam_role.airflow_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_redshift_policy" {
  role       = aws_iam_role.airflow_role.name
  policy_arn = aws_iam_policy.redshift_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_glue_policy" {
  role       = aws_iam_role.airflow_role.name
  policy_arn = aws_iam_policy.glue_access_policy.arn
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

# Subnets
resource "aws_subnet" "subnet_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}

resource "aws_subnet" "subnet_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2b"
}

resource "aws_subnet" "subnet_c" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-west-2c"
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

# Route Table
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

# Route Table Association
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.subnet_a.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.subnet_b.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_route_table_association" "c" {
  subnet_id      = aws_subnet.subnet_c.id
  route_table_id = aws_route_table.rt.id
}

# Security Group
resource "aws_security_group" "redshift_sg" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Redshift Serverless
resource "aws_redshiftserverless_namespace" "example" {
  namespace_name = "example-namespace"
  admin_username = var.admin_username
  admin_user_password = var.admin_user_password
}

resource "aws_redshiftserverless_workgroup" "example" {
  workgroup_name = "example-workgroup"
  namespace_name = aws_redshiftserverless_namespace.example.namespace_name
  subnet_ids     = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id, aws_subnet.subnet_c.id]
  security_group_ids = [aws_security_group.redshift_sg.id]
}

# Glue Catalog
resource "aws_glue_catalog_database" "example" {
  name = "example_db"
}

resource "aws_glue_catalog_table" "example" {
  name          = "example_table"
  database_name = aws_glue_catalog_database.example.name
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    "classification" = "parquet"
  }
  storage_descriptor {
    columns {
      name = "example_column"
      type = "string"
    }
    location = "s3://${aws_s3_bucket.airflow_bucket.bucket}/example/"
    input_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
    ser_de_info {
      name = "example"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }
  }
}

# Outputs
output "redshift_endpoint" {
  value = aws_redshiftserverless_workgroup.example.endpoint
}

output "redshift_port" {
  value = aws_redshiftserverless_workgroup.example.port
}

output "redshift_database" {
  value = "example_db"  # Replace with your actual database name if different
} 