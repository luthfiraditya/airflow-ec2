#!/usr/bin/env bash
set -eo pipefail

AIRFLOW_HOME="${AIRFLOW_HOME:-/opt/airflow}"

# Function to check if user exists
user_exists() {
    airflow users list | grep -q "$1"
}

echo "Starting Airflow initialization..."

# Initialize/Upgrade the database
echo "Initializing/Upgrading Airflow database..."
airflow db upgrade
echo "Database initialization/upgrade complete."

# Create Admin User if it does not exist
if ! user_exists "$_AIRFLOW_WWW_USER_USERNAME"; then
    echo "Creating Airflow admin user: $_AIRFLOW_WWW_USER_USERNAME"
    airflow users create \
        --username "$_AIRFLOW_WWW_USER_USERNAME" \
        --firstname "${_AIRFLOW_WWW_USER_FIRSTNAME:-Admin}" \
        --lastname "${_AIRFLOW_WWW_USER_LASTNAME:-User}" \
        --role "${_AIRFLOW_WWW_USER_ROLE:-Admin}" \
        --email "$_AIRFLOW_WWW_USER_EMAIL" \
        --password "$_AIRFLOW_WWW_USER_PASSWORD"
    echo "Admin user $_AIRFLOW_WWW_USER_USERNAME created."
else
    echo "Admin user $_AIRFLOW_WWW_USER_USERNAME already exists."
fi

# Optional: Set AIRFLOW_UID to match host user for volume permissions
# This is useful if dags, logs, plugins are mounted from the host
if [ -n "$AIRFLOW_UID" ] && [ "$AIRFLOW_UID" != "$(id -u airflow)" ]; then
    echo "Changing airflow user UID to $AIRFLOW_UID and GID to 0 (root group)"
    # Ensure the target UID isn't already taken by a critical system user
    if ! getent passwd "$AIRFLOW_UID" > /dev/null && [ "$AIRFLOW_UID" -ge 1000 ]; then
        usermod -u "$AIRFLOW_UID" airflow || echo "Warning: Failed to change UID for airflow user. Check for conflicts."
        # Change GID to 0 (root) to allow access to files created by root-owned Docker daemon
        groupmod -g 0 airflow || echo "Warning: Failed to change GID for airflow group."
    else
        echo "Warning: AIRFLOW_UID $AIRFLOW_UID is already in use or is a system UID (<1000). Skipping UID change."
    fi
fi

# Ensure correct ownership of mounted directories if AIRFLOW_UID is set
# This is important if the host UID is different from the container's default airflow UID
if [ -n "$AIRFLOW_UID" ]; then
    echo "Ensuring ownership of /opt/airflow/{dags,logs,plugins} for UID $AIRFLOW_UID GID 0..."
    chown -R "${AIRFLOW_UID}:0" "${AIRFLOW_HOME}/dags" "${AIRFLOW_HOME}/logs" "${AIRFLOW_HOME}/plugins" || echo "Warning: Failed to chown some directories."
fi

echo "Airflow initialization process finished."