
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.secrets.metastore import MetastoreBackend
from airflow.hooks.S3_hook import S3Hook

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                 aws_iam_role="",
                 table="",
                 create_script="",
                 populate_script="",
                 #aws_iam_role="",#"arn:aws:iam::876193940005:role/my-redshift-service-role",
                 redshift_conn_id="",
                 s3_bucket="",
                 s3_data_loc="",
                 aws_credentials_id="",
                 region="",
                 json_metadata="",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.aws_iam_role = aws_iam_role
        self.table = table
        self.create_script = create_script
        self.populate_script = populate_script       
        self.redshift_conn_id = redshift_conn_id
        self.s3_bucket = s3_bucket
        self.s3_data_loc = s3_data_loc
        self.aws_credentials_id = aws_credentials_id
        self.region = region
        self.json_metadata=json_metadata

    def execute(self, context):
        metastoreBackend = MetastoreBackend()
        aws_connection=metastoreBackend.get_connection(self.aws_credentials_id)
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info("Drop table {}".format(self.table))
        redshift.run(f"DROP TABLE IF EXISTS {self.table}")

        self.log.info("create table {}".format(self.table))
        redshift.run(self.create_script)

        self.log.info("Copying data from S3 to Redshift")
        s3_path = "s3://{}/{}".format(self.s3_bucket, self.s3_data_loc)
        formatted_populate_script = self.populate_script.format(s3_path, 
                                                                aws_connection.login,
                                                                aws_connection.password,
                                                                self.json_metadata,
                                                                self.region)
        redshift.run(formatted_populate_script)
