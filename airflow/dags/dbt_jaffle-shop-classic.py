from pathlib import Path
from datetime import datetime
from cosmos import DbtDag, ProjectConfig, ProfileConfig
from cosmos import ExecutionConfig

jaffle_shop_path = Path("/opt/airflow/dags/repo/airflow/dbt/jaffle-shop-classic")
dbt_executable = Path("/home/airflow/.local/bin/dbt")

venv_execution_config = ExecutionConfig(
    dbt_executable_path=str(dbt_executable),
)


dbt_profile_example = DbtDag(
    # dbt/cosmos-specific parameters
    project_config=ProjectConfig(
        dbt_project_path=jaffle_shop_path,
        env_vars={
            "TRINO_HOST": "trino.trino.svc.cluster.local",
            "TRINO_PORT": "8080",
            "TRINO_USER": "dbt",
        },
    ),
    profile_config=ProfileConfig(
        # these map to dbt/jaffle_shop/profiles.yml
        profile_name="trino",
        target_name="dev",
        profiles_yml_filepath=jaffle_shop_path / "profiles.yml",
    ),
    execution_config=venv_execution_config,
    # normal dag parameters
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    dag_id="dbt_jaffle-shop-classic_example",
    tags=["dbt"],
)
