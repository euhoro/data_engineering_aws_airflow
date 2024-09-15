from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

# Define the DAG
with DAG(
    dag_id='check_connections_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task to check AWS credentials
    check_aws_credentials = BashOperator(
        task_id='check_aws_credentials',
        bash_command='aws sts get-caller-identity',
    )

    # Task to check Redshift connection
    check_redshift_connection = PostgresOperator(
        task_id='check_redshift_connection',
        postgres_conn_id='redshift_default',  # Ensure this connection is configured in Airflow
        sql='SELECT 1;',
    )

    # Define task dependencies
    check_aws_credentials >> check_redshift_connection