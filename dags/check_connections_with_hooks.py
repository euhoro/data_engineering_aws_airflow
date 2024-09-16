from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.hooks.base_hook import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago

from airflow.models import Variable
import logging

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

from botocore.exceptions import ClientError

def check_aws_credentials():
    try:
        # Get the AWS connection
        conn = BaseHook.get_connection('aws_credentials')
        
        # Create an S3 client
        hook = conn.get_hook()
        s3_client = hook.get_client_type('s3')
        
        # Get bucket and prefix from Airflow Variables
        bucket = Variable.get('s3_bucket')
        prefix = Variable.get('s3_prefix', '')  # Use empty string as default if not set
        
        logging.info(f"Listing objects from {bucket}/{prefix}")
        
        # List objects in the bucket
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                logging.info(f"- s3://{bucket}/{obj['Key']}")
        
        logging.info("Bucket listing completed successfully")
    except ClientError as e:
        logging.error(f"An error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# def check_aws_credentials():
#     hook = AwsBaseHook(aws_conn_id='aws_credentials')
#     client = hook.get_client_type('s3')
#     #response = client.get_caller_identity()
#     # return response
#     bucket = Variable.get('s3_bucket')
#     prefix = Variable.get('s3_prefix')
#     logging.info(f"Listing Keys from {bucket}/{prefix}")
#     keys = hook.list_keys(bucket, prefix=prefix)
#     for key in keys:
#         logging.info(f"- s3://{bucket}/{key}")

def check_redshift_connection():
    hook = PostgresHook(postgres_conn_id='redshift')
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT 1;')
    result = cursor.fetchone()
    return result

# Define the DAG
with DAG(
    dag_id='check_connections_dag2',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task to check AWS credentials
    check_aws_credentials_task = PythonOperator(
        task_id='check_aws_credentials',
        python_callable=check_aws_credentials,
    )

    # Task to check Redshift connection
    check_redshift_connection_task = PythonOperator(
        task_id='check_redshift_connection',
        python_callable=check_redshift_connection,
    )

    # Define task dependencies
check_redshift_connection_task >> check_aws_credentials_task 
#check_aws_credentials_task