from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table="",
                 create_script="",                 
                 populate_script="",
                 append_or_delete_load="",                 
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.create_script = create_script        
        self.populate_script = populate_script
        self.append_or_delete_load = append_or_delete_load        

    def execute(self, context):
        self.log.info('LoadDimensionOperator')
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        if self.append_or_delete_load:
            self.log.info("Drop table {}".format(self.table))
            redshift.run(f"DROP TABLE IF EXISTS {self.table}")

            self.log.info("create table {}".format(self.table))
            redshift.run(self.create_script)
        
        self.log.info("populate table {}".format(self.table))        
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        redshift.run(self.populate_script)             