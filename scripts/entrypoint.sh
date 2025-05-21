#!/usr/bin/env bash
set -eo pipefail

AIRFLOW_HOME="${AIRFLOW_HOME:-/opt/airflow}"
COMMAND="$1"

# Set AIRFLOW_CONFIG to use the mounted airflow.cfg if it exists
if [ -f "${AIRFLOW_HOME}/airflow.cfg" ]; then
  export AIRFLOW__CORE__AIRFLOW_CONFIG="${AIRFLOW_HOME}/airflow.cfg"
fi

# Install custom python packages if requirements.txt is present in a specific location
# This is already handled in the Dockerfile build stage, but could be used for dynamic installs
# if [ -e "/opt/airflow/requirements/requirements.txt" ]; then
#   echo "Installing custom requirements..."
#   pip install --user -r "/opt/airflow/requirements/requirements.txt"
# fi

# Wait for PostgreS and Redis (optional, as docker-compose handles depends_on with healthchecks)
# wait_for_port() {
#   local name="$1" host="$2" port="$3"
#   local j=0
#   while ! nc -z "$host" "$port" >/dev/null 2>&1 < /dev/null; do
#     j=$((j+1))
#     if [ $j -ge 30 ]; then
#       echo >&2 "$(date) - $host:$port still not reachable, giving up"
#       exit 1
#     fi
#     echo "$(date) - waiting for $name... $j/30"
#     sleep 5
#   done
# }

# if [ "$COMMAND" != "version" ] && [ "$COMMAND" != "bash" ] && [ "$COMMAND" != "python" ]; then
#   POSTGRES_HOST=$(echo "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" | cut -d@ -f2 | cut -d/ -f1 | cut -d: -f1)
#   POSTGRES_PORT=$(echo "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" | cut -d@ -f2 | cut -d/ -f1 | cut -d: -f2)
#   REDIS_HOST=$(echo "$AIRFLOW__CELERY__BROKER_URL" | cut -d@ -f2 | cut -d/ -f1 | cut -d: -f1)
#   REDIS_PORT=$(echo "$AIRFLOW__CELERY__BROKER_URL" | cut -d@ -f2 | cut -d/ -f1 | cut -d: -f2)
#   wait_for_port "Postgres" "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"
#   wait_for_port "Redis" "$REDIS_HOST" "${REDIS_PORT:-6379}"
# fi

# Execute the given command (webserver, scheduler, worker, etc.)
exec airflow "$@"