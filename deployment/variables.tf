# variables.tf

variable "admin_username" {
  description = "The admin username for Redshift"
  type        = string
}

variable "admin_user_password" {
  description = "The admin user password for Redshift"
  type        = string
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
  default     = "my-unique-airflow-bucket-12345"  # Ensure this name is unique
}