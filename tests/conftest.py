import os
import pytest
from airflow.models import DagBag

@pytest.fixture(scope="session")
def project_root_dir():
    """Returns the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

@pytest.fixture(scope="session")
def dags_folder(project_root_dir):
    """Returns the DAGs folder path."""
    return os.path.join(project_root_dir, "dags")

@pytest.fixture(scope="session")
def dagbag(dags_folder):
    """
    Fixture to load the DagBag.
    It's session-scoped for efficiency as DagBag loading can be slow.
    """
    # Temporarily set AIRFLOW_HOME if it's not set, to avoid issues with DagBag loading
    # This is more relevant if tests are run outside a full Airflow environment setup
    original_airflow_home = os.environ.get("AIRFLOW_HOME")
    if not original_airflow_home:
        os.environ["AIRFLOW_HOME"] = os.path.expanduser("~/airflow_test_home") # Dummy home
        if not os.path.exists(os.environ["AIRFLOW_HOME"]):
            os.makedirs(os.environ["AIRFLOW_HOME"])

    dagbag = DagBag(dag_folder=dags_folder, include_examples=False)

    if original_airflow_home is None:
        del os.environ["AIRFLOW_HOME"] # Clean up
    elif original_airflow_home:
        os.environ["AIRFLOW_HOME"] = original_airflow_home # Restore

    return dagbag