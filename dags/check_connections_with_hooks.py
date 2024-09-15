from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

def check_aws_credentials():
    hook = AwsBaseHook(aws_conn_id='aws_credentials', client_type='sts')
    client = hook.get_client_type('sts')
    response = client.get_caller_identity()
    return response

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
    check_aws_credentials_task >> check_redshift_connection_task