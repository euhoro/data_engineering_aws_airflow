# Get available Availability Zones in the region
data "aws_availability_zones" "available" {}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "redshift-vpc"
  }
}

# Subnets (dynamically select availability zones)
resource "aws_subnet" "subnet_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]  # Use first available zone
  map_public_ip_on_launch = true

  tags = {
    Name = "redshift-subnet-a"
  }
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]  # Use second available zone
  map_public_ip_on_launch = true

  tags = {
    Name = "redshift-subnet-b"
  }
}

resource "aws_subnet" "subnet_c" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = data.aws_availability_zones.available.names[2]  # Use third available zone
  map_public_ip_on_launch = true

  tags = {
    Name = "redshift-subnet-c"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "redshift-igw"
  }
}

# Route Table
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "redshift-route-table"
  }
}

# Route Table Associations
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
  name        = "redshift-sg"
  description = "Allow inbound traffic for Redshift"
  vpc_id      = aws_vpc.main.id

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

  tags = {
    Name = "redshift-sg"
  }
}

# Redshift Serverless
resource "aws_redshiftserverless_namespace" "example" {
  namespace_name      = "example-namespace"
  admin_username      = var.admin_username
  admin_user_password = var.admin_user_password
}

resource "aws_redshiftserverless_workgroup" "example" {
  workgroup_name        = "example-workgroup"
  namespace_name        = aws_redshiftserverless_namespace.example.namespace_name
  subnet_ids            = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id, aws_subnet.subnet_c.id]
  security_group_ids    = [aws_security_group.redshift_sg.id]
  publicly_accessible   = true
  base_capacity         = 8  # Adjust as needed
  enhanced_vpc_routing  = false
}


# Outputs
output "redshift_endpoint" {
  value = aws_redshiftserverless_workgroup.example.endpoint
}

output "redshift_port" {
  value = aws_redshiftserverless_workgroup.example.port
}

output "redshift_database" {
  value = aws_redshiftserverless_namespace.example.namespace_name
}
