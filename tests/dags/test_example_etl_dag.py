import pytest
from airflow.utils.dag_cycle_tester import check_cycle

DAG_ID = "example_etl_pipeline_v1"

def test_dag_loaded(dagbag):
    """Test that the example_etl_pipeline_v1 DAG is loaded correctly and has no import errors."""
    dag = dagbag.get_dag(dag_id=DAG_ID)
    assert dag is not None, f"DAG {DAG_ID} not found in DagBag."
    assert not dagbag.import_errors.get(dag.filepath if dag else ''), \
        f"DAG {DAG_ID} has import errors: {dagbag.import_errors.get(dag.filepath if dag else '')}"

def test_dag_tasks(dagbag):
    """Test the number of tasks and their IDs in the DAG."""
    dag = dagbag.get_dag(dag_id=DAG_ID)
    assert dag is not None
    
    expected_task_ids = {
        "start_pipeline",
        "extract_data",
        "transform_data",
        "load_data",
        "potentially_failing_task",
        "send_success_email",
        "end_pipeline",
    }
    actual_task_ids = {task.task_id for task in dag.tasks}
    assert actual_task_ids == expected_task_ids, \
        f"Task IDs do not match. Expected: {expected_task_ids}, Got: {actual_task_ids}"
    assert len(dag.tasks) == len(expected_task_ids), \
        f"Expected {len(expected_task_ids)} tasks, but found {len(dag.tasks)}."

def test_dag_dependencies(dagbag):
    """Test specific task dependencies."""
    dag = dagbag.get_dag(dag_id=DAG_ID)
    assert dag is not None

    start_task = dag.get_task("start_pipeline")
    extract_task = dag.get_task("extract_data")
    transform_task = dag.get_task("transform_data")
    load_task = dag.get_task("load_data")
    potentially_failing_task = dag.get_task("potentially_failing_task")
    send_success_email_task = dag.get_task("send_success_email")
    end_task = dag.get_task("end_pipeline")

    assert extract_task in start_task.downstream_list
    assert transform_task in extract_task.downstream_list
    assert load_task in transform_task.downstream_list
    
    assert potentially_failing_task in load_task.downstream_list
    assert send_success_email_task in load_task.downstream_list
    
    assert end_task in potentially_failing_task.downstream_list
    assert end_task in send_success_email_task.downstream_list

def test_dag_no_cycles(dagbag):
    """Test that the DAG does not contain cycles."""
    dag = dagbag.get_dag(dag_id=DAG_ID)
    assert dag is not None
    check_cycle(dag) # This will raise an AirflowDagCycleException if a cycle is found

def test_dag_default_args(dagbag):
    """Test that default arguments are set correctly."""
    dag = dagbag.get_dag(dag_id=DAG_ID)
    assert dag is not None
    assert dag.default_args['owner'] == 'airflow_admin'
    assert dag.default_args['email_on_failure'] is True
    assert dag.default_args['retries'] == 1

# To run tests:
# 1. Ensure pytest and necessary Airflow components are installed in your environment.
# 2. Navigate to the project root directory (d:/insignia/luthfi/office_work/adhi_karya/airflow-ec2-setup).
# 3. Run: pytest