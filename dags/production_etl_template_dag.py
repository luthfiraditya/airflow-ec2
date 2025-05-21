from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.email import EmailOperator
# from airflow.providers.amazon.aws.operators.s3 import S3ListOperator # Example for S3
# from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator # Example for Snowflake
# from airflow.providers.great_expectations.operators.great_expectations import GreatExpectationsOperator # Example for Great Expectations

# --- Configuration ---
ETL_OWNER = 'data_engineering_team'
ALERT_EMAILS = ['data.alerts@example.com', 'etl.support@example.com'] # TODO: Update with your alert emails
ETL_SCHEDULE = '@daily' # TODO: Adjust schedule as needed (e.g., '0 5 * * *' for 5 AM UTC daily)
ETL_START_DATE = pendulum.datetime(2023, 1, 1, tz="UTC") # TODO: Set appropriate start date

# --- Default Arguments ---
default_args = {
    'owner': ETL_OWNER,
    'depends_on_past': False,
    'email': ALERT_EMAILS,
    'email_on_failure': True, # Send email on task failure
    'email_on_retry': False,  # Do not send email on task retry
    'retries': 2,
    'retry_delay': pendulum.duration(minutes=5),
    'execution_timeout': pendulum.duration(hours=2), # Max time for a task to run
    # 'sla': pendulum.duration(hours=1), # Example: Expected time for a task to complete
}

# --- Custom Callbacks ---
def custom_on_failure_callback(context):
    """
    Custom callback function to execute on DAG or task failure.
    Can be used for enhanced alerting (Slack, PagerDuty, etc.).
    """
    dag_run = context.get('dag_run')
    task_instance = context.get('task_instance')
    log_url = task_instance.log_url
    exception = context.get('exception')

    subject = f"[Airflow ETL Alert] DAG {dag_run.dag_id} Failed on Task {task_instance.task_id}"
    html_content = f"""
    <h3>ETL Pipeline Failure Alert</h3>
    <b>DAG:</b> {dag_run.dag_id}<br>
    <b>Task:</b> {task_instance.task_id}<br>
    <b>Execution Date:</b> {dag_run.execution_date}<br>
    <b>Log URL:</b> <a href="{log_url}">Link to Task Logs</a><br>
    <b>Reason:</b> {exception}
    <br><br>
    Please investigate the failure.
    """
    print(f"Custom failure alert: {subject}")
    # Example: Send email directly (ensure SMTP is configured in Airflow)
    # from airflow.utils.email import send_email
    # send_email(to=ALERT_EMAILS, subject=subject, html_content=html_content)

    # TODO: Add integration with other alerting systems if needed (e.g., Slack, PagerDuty)


def custom_on_success_callback(context):
    """
    Custom callback function to execute on DAG success.
    """
    dag_run = context.get('dag_run')
    subject = f"[Airflow ETL Notification] DAG {dag_run.dag_id} Succeeded"
    html_content = f"""
    <h3>ETL Pipeline Success Notification</h3>
    <b>DAG:</b> {dag_run.dag_id}<br>
    <b>Execution Date:</b> {dag_run.execution_date}<br>
    <br>
    The ETL pipeline completed successfully.
    """
    print(f"Custom success alert: {subject}")
    # Example: Send email directly
    # from airflow.utils.email import send_email
    # send_email(to=ALERT_EMAILS, subject=subject, html_content=html_content)


# --- Python Callables for Tasks (Examples) ---
def extract_source_data_callable(**kwargs):
    """
    Placeholder for Python logic to extract data from a source.
    This could involve API calls, database queries, reading files, etc.
    """
    print("Starting data extraction...")
    # TODO: Implement your data extraction logic here.
    # Example:
    # api_client = YourApiClient()
    # data = api_client.fetch_data(date=kwargs['ds'])
    # save_to_staging(data, f"/staging/raw_data_{kwargs['run_id']}.json")
    print(f"Data extraction for {kwargs['ds']} completed.")
    return "Path to extracted data or metadata"

def transform_data_callable(extracted_data_path: str, **kwargs):
    """
    Placeholder for Python logic to transform data.
    """
    print(f"Starting data transformation for data at: {extracted_data_path}")
    # TODO: Implement your data transformation logic here.
    # Example:
    # raw_data = load_from_staging(extracted_data_path)
    # transformed_data = perform_cleaning(raw_data)
    # transformed_data = perform_enrichment(transformed_data)
    # save_to_staging(transformed_data, f"/staging/transformed_data_{kwargs['run_id']}.parquet")
    print(f"Data transformation for {kwargs['ds']} completed.")
    return "Path to transformed data or metadata"

def load_data_to_dwh_callable(transformed_data_path: str, **kwargs):
    """
    Placeholder for Python logic to load data into a Data Warehouse.
    """
    print(f"Starting data load to DWH from: {transformed_data_path}")
    # TODO: Implement your data loading logic here.
    # Example:
    # transformed_data = load_from_staging(transformed_data_path)
    # dwh_connector = YourDWHConnector()
    # dwh_connector.load_data(table_name='fact_table', data=transformed_data, load_date=kwargs['ds'])
    print(f"Data load to DWH for {kwargs['ds']} completed.")

def data_quality_check_callable(data_path: str, expectations_suite_name: str, **kwargs):
    """
    Placeholder for data quality checks.
    Could use libraries like Great Expectations, Pandas Profiling, or custom checks.
    """
    print(f"Performing data quality checks on {data_path} using suite {expectations_suite_name}...")
    # TODO: Implement your data quality check logic.
    # Example with Great Expectations (requires setup):
    # from great_expectations.data_context import BaseDataContext
    # from great_expectations.data_context.types.base import DataContextConfig, FilesystemStoreBackendDefaults
    #
    # data_context_config = DataContextConfig(
    #     store_backend_defaults=FilesystemStoreBackendDefaults(root_directory="/opt/airflow/great_expectations")
    # )
    # context = BaseDataContext(project_config=data_context_config)
    # result = context.run_checkpoint(
    #     checkpoint_name="your_checkpoint_name", # Define in your GE project
    #     batch_request={
    #         "datasource_name": "your_datasource_name",
    #         "data_connector_name": "your_data_connector_name",
    #         "data_asset_name": "your_data_asset_name",
    #         "data_connector_query": {"path": data_path} # Adjust based on connector
    #     },
    #     expectation_suite_name=expectations_suite_name
    # )
    # if not result["success"]:
    #     raise ValueError(f"Data quality check failed for {data_path}. Validation result: {result}")
    print(f"Data quality checks for {data_path} passed.")
    return True # Or raise an exception if checks fail

def cleanup_staging_callable(**kwargs):
    """
    Placeholder for cleaning up temporary staging files or resources.
    """
    print(f"Cleaning up staging area for run_id: {kwargs['run_id']}...")
    # TODO: Implement your cleanup logic.
    # Example:
    # delete_files_from_staging(pattern=f"/staging/*_{kwargs['run_id']}.*")
    print("Staging area cleanup completed.")

# --- DAG Definition ---
with DAG(
    dag_id='production_etl_template_v1', # TODO: Rename DAG with a descriptive name
    default_args=default_args,
    description='A template for production-ready ETL pipelines.',
    schedule=ETL_SCHEDULE,
    start_date=ETL_START_DATE,
    catchup=False, # Set to True if you need to backfill, False otherwise
    tags=['template', 'etl', 'production'],
    doc_md="""
    ### Production ETL Pipeline Template
    This DAG serves as a template for building robust ETL pipelines.
    It includes stages for extraction, transformation, loading, data quality checks, and notifications.
    **Remember to replace placeholder logic with your specific implementations.**
    """,
    on_failure_callback=custom_on_failure_callback, # DAG level failure callback
    # on_success_callback=custom_on_success_callback, # Optional: DAG level success callback
) as dag:

    start_pipeline = EmptyOperator(
        task_id='start_pipeline',
        doc_md="Marks the beginning of the ETL pipeline."
    )

    # --- EXTRACT STAGE ---
    extract_source_data = PythonOperator(
        task_id='extract_source_data',
        python_callable=extract_source_data_callable,
        # op_kwargs={'source_system': 'api_xyz'}, # Example of passing static params
        doc_md="Extracts data from the source system(s)."
    )

    # --- DATA QUALITY (RAW) STAGE ---
    # Example: Using a PythonOperator for custom DQC
    raw_data_quality_check = PythonOperator(
        task_id='raw_data_quality_check',
        python_callable=data_quality_check_callable,
        op_kwargs={
            'data_path': "{{ ti.xcom_pull(task_ids='extract_source_data') }}", # Pull path from upstream
            'expectations_suite_name': 'raw_data_expectations' # TODO: Define your GE suite or DQC logic
        },
        doc_md="Performs data quality checks on the raw extracted data."
    )
    # Example: Using GreatExpectationsOperator (requires provider and GE setup)
    # raw_data_quality_check_ge = GreatExpectationsOperator(
    #     task_id='raw_data_quality_check_ge',
    #     expectation_suite_name='raw_data_expectations', # TODO: Define in your GE project
    #     batch_request={ # TODO: Configure your batch request
    #         'datasource_name': 'my_staging_datasource',
    #         'data_connector_name': 'default_inferred_data_connector_name',
    #         'data_asset_name': "{{ ti.xcom_pull(task_ids='extract_source_data').split('/')[-1] }}", # Example
    #         'data_connector_query': {'path': "{{ ti.xcom_pull(task_ids='extract_source_data') }}"}
    #     },
    #     data_context_root_dir='/opt/airflow/great_expectations', # TODO: Adjust path
    #     fail_task_on_validation_failure=True,
    # )

    # --- TRANSFORM STAGE ---
    transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data_callable,
        op_kwargs={'extracted_data_path': "{{ ti.xcom_pull(task_ids='extract_source_data') }}"},
        doc_md="Transforms raw data into the desired format and structure."
    )

    # --- DATA QUALITY (TRANSFORMED) STAGE ---
    transformed_data_quality_check = PythonOperator(
        task_id='transformed_data_quality_check',
        python_callable=data_quality_check_callable,
        op_kwargs={
            'data_path': "{{ ti.xcom_pull(task_ids='transform_data') }}",
            'expectations_suite_name': 'transformed_data_expectations' # TODO: Define your GE suite or DQC logic
        },
        doc_md="Performs data quality checks on the transformed data."
    )

    # --- LOAD STAGE ---
    load_data_to_dwh = PythonOperator(
        task_id='load_data_to_data_warehouse',
        python_callable=load_data_to_dwh_callable,
        op_kwargs={'transformed_data_path': "{{ ti.xcom_pull(task_ids='transform_data') }}"},
        doc_md="Loads transformed and validated data into the Data Warehouse."
    )
    # Example: Loading to Snowflake
    # load_to_snowflake_example = SnowflakeOperator(
    #     task_id='load_to_snowflake_example',
    #     snowflake_conn_id='your_snowflake_conn_id', # TODO: Define Airflow connection
    #     sql="COPY INTO my_target_table FROM @my_s3_stage/{{ ti.xcom_pull(task_ids='transform_data').split('/')[-1] }};",
    #     # params={'load_date': '{{ ds }}'},
    #     doc_md="Example: Loads data into Snowflake using a COPY command."
    # )

    # --- NOTIFICATION & CLEANUP STAGE ---
    send_success_notification = EmailOperator(
        task_id='send_success_notification',
        to=ALERT_EMAILS,
        subject='[Airflow ETL Notification] DAG {{ dag.dag_id }} Succeeded',
        html_content="""
            <h3>ETL Pipeline: {{ dag.dag_id }} Succeeded</h3>
            <p><b>Execution Date:</b> {{ ds }}</p>
            <p><b>DAG Run ID:</b> {{ run_id }}</p>
            <p>All tasks completed successfully.</p>
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS, # Only if all upstream tasks succeeded
        doc_md="Sends a success notification email upon successful pipeline completion."
    )

    cleanup_staging_area = PythonOperator(
        task_id='cleanup_staging_area',
        python_callable=cleanup_staging_callable,
        trigger_rule=TriggerRule.ALL_DONE, # Run regardless of upstream success or failure
        doc_md="Cleans up temporary files and resources from the staging area."
    )

    end_pipeline = EmptyOperator(
        task_id='end_pipeline',
        trigger_rule=TriggerRule.ALL_DONE, # Ensures this runs even if some branches fail
        doc_md="Marks the end of the ETL pipeline execution."
    )

    # --- Define Task Dependencies ---
    start_pipeline >> extract_source_data >> raw_data_quality_check
    raw_data_quality_check >> transform_data >> transformed_data_quality_check
    transformed_data_quality_check >> load_data_to_dwh

    load_data_to_dwh >> send_success_notification # Success path
    load_data_to_dwh >> cleanup_staging_area    # Always run cleanup after load attempt

    # Ensure end_pipeline runs after notifications and cleanup
    [send_success_notification, cleanup_staging_area] >> end_pipeline

    # If you have tasks that should run even if load_data_to_dwh fails, but after DQC:
    # transformed_data_quality_check >> [load_data_to_dwh, some_other_task_on_dqc_success]
    # load_data_to_dwh.set_downstream(cleanup_staging_area, trigger_rule=TriggerRule.ALL_DONE)
    # load_data_to_dwh.set_downstream(send_success_notification, trigger_rule=TriggerRule.ALL_SUCCESS)