from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.email import EmailOperator # For email alerts

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow_admin',
    'depends_on_past': False,
    'email': ['your_alert_email@example.com'], # Update with your email
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': pendulum.duration(minutes=5),
    'execution_timeout': pendulum.duration(hours=1),
}

def print_hello():
    print("Hello from PythonOperator!")
    return "PythonOperator says hello."

def custom_failure_alert(context):
    dag_run = context.get('dag_run')
    task_instance = context.get('task_instance')
    log_url = task_instance.log_url
    subject = f"[Airflow Alert] DAG {dag_run.dag_id} Failed"
    html_content = f"""
    <h3>DAG Failure Alert</h3>
    <b>DAG:</b> {dag_run.dag_id}<br>
    <b>Task:</b> {task_instance.task_id}<br>
    <b>Execution Date:</b> {dag_run.execution_date}<br>
    <b>Log URL:</b> <a href="{log_url}">Link to logs</a><br>
    <b>Reason:</b> {context.get('exception')}
    """
    # This function can be extended to send alerts via Slack, PagerDuty, etc.
    # For now, it relies on the EmailOperator configured for the task or DAG.
    print(f"Custom failure alert: {subject}")
    # If you want to send an email directly from here (requires SMTP setup):
    # from airflow.utils.email import send_email
    # send_email(to=default_args['email'], subject=subject, html_content=html_content)


with DAG(
    dag_id='example_etl_pipeline_v1',
    default_args=default_args,
    description='An example ETL pipeline DAG for EC2 deployment.',
    schedule='@daily', # Run daily
    start_date=pendulum.datetime(2023, 10, 26, tz="UTC"),
    catchup=False, # Don't run for past missed schedules
    tags=['example', 'etl', 'ec2'],
    doc_md=__doc__,
    on_failure_callback=custom_failure_alert, # DAG level failure callback
) as dag:
    dag.doc_md = """
    ### Example ETL Pipeline DAG
    This DAG demonstrates a simple ETL pipeline with several tasks.
    - It includes BashOperator and PythonOperator.
    - It shows basic task dependencies.
    - Configured for daily execution.
    - Includes email alerting on failure.
    """

    start = EmptyOperator(task_id='start_pipeline')

    extract_data = BashOperator(
        task_id='extract_data',
        bash_command='echo "Extracting data..." && sleep 5 && echo "Data extracted!"',
        doc_md="Simulates extracting data from a source system."
    )

    transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=print_hello,
        doc_md="Simulates transforming the extracted data using Python."
    )

    load_data = BashOperator(
        task_id='load_data',
        bash_command='echo "Loading data into destination..." && sleep 5 && echo "Data loaded!"',
        doc_md="Simulates loading transformed data into a data warehouse or data lake."
    )

    # Example of a task that might fail, to test retries and alerts
    potentially_failing_task = BashOperator(
        task_id='potentially_failing_task',
        bash_command='echo "This task might fail..." && exit 1', # Intentionally failing task
        retries=2, # Override DAG level retries
        on_failure_callback=custom_failure_alert, # Task level failure callback
        doc_md="A task designed to fail to demonstrate retry and alert mechanisms."
    )

    send_success_email = EmailOperator(
        task_id='send_success_email',
        to=default_args['email'],
        subject='Airflow DAG {{ dag.dag_id }} Succeeded',
        html_content="""
            <h3>DAG {{ dag.dag_id }} Succeeded</h3>
            <p>Execution Date: {{ ds }}</p>
            <p>DAG Run ID: {{ run_id }}</p>
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS, # Only run if all upstream tasks succeed
        doc_md="Sends a success notification email."
    )
    
    end = EmptyOperator(
        task_id='end_pipeline',
        trigger_rule=TriggerRule.ALL_DONE, # Run regardless of upstream success or failure
        doc_md="Marks the end of the pipeline execution."
    )

    # Define task dependencies
    start >> extract_data >> transform_data >> load_data
    load_data >> [send_success_email, potentially_failing_task] # Parallel execution
    [send_success_email, potentially_failing_task] >> end