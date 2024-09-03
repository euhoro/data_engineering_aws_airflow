# data_engineering_aws_airflow
data_engineering_aws_airflow
# data_engineering_aws_airflow
data_engineering_aws_airflow

Project: Data Pipelines with Airflow
A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow.

They have decided to bring you into the project and expect you to create high grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

This project will introduce you to the core concepts of Apache Airflow. To complete the project, you will need to create your own custom operators to perform tasks such as staging the data, filling the data warehouse, and running checks on the data as the final step.

We have provided you with a project template that takes care of all the imports and provides four empty operators that need to be implemented into functional pieces of a data pipeline. The template also contains a set of tasks that need to be linked to achieve a coherent and sensible data flow within the pipeline.

You'll be provided with a helpers class that contains all the SQL transformations. Thus, you won't need to write the ETL yourselves, but you'll need to execute it with your custom operators.

can you include this graph in the read.me file ? 

Sure! Here is how you can include the graph in your README.md file using a code block:
dot
digraph DAG {
node [shape=box, style=filled, color=green, fontcolor=black];
Begin_execution [fillcolor=lightgreen];
Stage_events [fillcolor=darkgreen];
Stage_songs [fillcolor=darkgreen];
Load_songplays_fact_table [fillcolor=lightcoral];
Load_song_dim_table [fillcolor=lightgreen];
Load_user_dim_table [fillcolor=lightgreen];
Load_artist_dim_table [fillcolor=lightgreen];
Load_time_dim_table [fillcolor=lightgreen];
Run_data_quality_checks [fillcolor=lightgreen];
End_execution [fillcolor=lightgreen];
Begin_execution -> Stage_events;
Begin_execution -> Stage_songs;
Stage_events -> Load_songplays_fact_table;
Stage_songs -> Load_songplays_fact_table;
Load_songplays_fact_table -> Load_song_dim_table;
Load_songplays_fact_table -> Load_user_dim_table;
Load_songplays_fact_table -> Load_artist_dim_table;
Load_songplays_fact_table -> Load_time_dim_table;
Load_song_dim_table -> Run_data_quality_checks;
Load_user_dim_table -> Run_data_quality_checks;
Load_artist_dim_table -> Run_data_quality_checks;
Load_time_dim_table -> Run_data_quality_checks;
Run_data_quality_checks -> End_execution;
}
.
## Mermaid Graph

```mermaid
graph TD
    Begin_execution["Begin execution"] --> Stage_events["Stage events"]
    Begin_execution --> Stage_songs["Stage songs"]
    Stage_events --> Load_songplays_fact_table["Load songplays fact table"]
    Stage_songs --> Load_songplays_fact_table
    Load_songplays_fact_table --> Load_song_dim_table["Load song dim table"]
    Load_songplays_fact_table --> Load_user_dim_table["Load user dim table"]
    Load_songplays_fact_table --> Load_artist_dim_table["Load artist dim table"]
    Load_songplays_fact_table --> Load_time_dim_table["Load time dim table"]
    Load_song_dim_table --> Run_data_quality_checks["Run data quality checks"]
    Load_user_dim_table --> Run_data_quality_checks
    Load_artist_dim_table --> Run_data_quality_checks
    Load_time_dim_table --> Run_data_quality_checks
    Run_data_quality_checks --> End_execution["End execution"]
```
