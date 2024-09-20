from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id = "",
                 tables_list = "",
                 sql_quality_tests="",
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.tables_list = tables_list
        self.sql_quality_tests=sql_quality_tests

    def execute(self, context):
        self.log.info('DataQualityOperator')
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        # Iterate over sql test and tables
        for i, test in enumerate(self.sql_quality_tests):
            sql_test = test['test_sql']
            expected_result = test['expected_result']
            
            for table in self.tables_list:
                sql_query = sql_test.format(table)
                result = redshift_hook.run(sql_query)
                
                self.log.info(f"Checking the following data quality: {sql_query}")

                if len(result) < 1 or len(result[0]) < 1:
                    raise ValueError(f"Data quality check failed. {table} returned no results")
                    
                num_records = result[0][0]
                
                # Any record check
                if expected_result == -1:
                    if num_records < 1:
                        raise ValueError(f"Data quality check failed. {table} contained {num_records} rows")
                    
                    logging.info(f"Data quality on table {table} check passed with {num_records} records")


        