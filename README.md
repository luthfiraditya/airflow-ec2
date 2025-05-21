# Production-Grade Apache Airflow on EC2 with Docker

This project provides a scaffolding for deploying Apache Airflow 2.x on an AWS EC2 instance using Docker and Docker Compose. It's designed with production readiness and data engineering best practices in mind.

## Features

-   **Apache Airflow 2.x**: Utilizes a recent stable version of Airflow.
-   **Docker & Docker Compose**: For containerized and orchestrated deployment.
-   **CeleryExecutor**: For scalable task execution.
-   **PostgreSQL Backend**: For robust metadata storage (can be RDS or Docker).
-   **Redis Broker**: For Celery message queuing.
-   **Persistent Volumes**: For DAGs, logs, and plugins.
-   **Modular Structure**: `dags/`, `plugins/`, `config/`, `scripts/`, `tests/`.
-   **Environment-based Configuration**: Uses `.env` for sensitive settings.
-   **RBAC Enabled**: With admin user bootstrapped via script.
-   **Makefile**: For easy management (build, start, stop, etc.).
-   **Sample DAG**: Includes an example ETL pipeline with alerting.
-   **Linting & Formatting**: Pre-commit hooks for Black, Flake8, isort.
-   **Optional Nginx Reverse Proxy**: Stub for TLS/HTTPS termination.
-   **Healthchecks**: For Airflow services.

## Prerequisites

-   **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
-   **Docker Compose**: Usually comes with Docker Desktop. If not, [install Docker Compose](https://docs.docker.com/compose/install/).
-   **Git**: For cloning the repository.
-   **AWS Account & EC2 Instance**: An EC2 instance (Ubuntu 22.04 or Amazon Linux 2 recommended) with Docker and Docker Compose installed.
-   **(Optional) AWS CLI**: If integrating with AWS services like SSM or S3 for logs.
-   **(Optional) Make**: For using the `Makefile`. On Windows, you can use `make` via WSL or Git Bash.

## Local Setup (Development & Testing)

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd airflow-ec2-setup
    ```

2.  **Configure Environment Variables:**
    Copy the `.env.example` (if provided) or create `.env` from the template:
    ```bash
    cp .env.example .env # or manually create .env
    ```
    Edit `d:/insignia/luthfi/office_work/adhi_karya/airflow-ec2-setup/.env` and fill in the required values:
    -   `AIRFLOW_FERNET_KEY`: Generate one using `make fernet-key` or:
        ```bash
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        ```
    -   Update SMTP settings if you want email alerts.
    -   (Linux/macOS) Set `AIRFLOW_UID=$(id -u)` in `.env` if you want container file ownership to match your host user. This helps avoid permission issues with mounted volumes. For Windows/WSL, find your WSL user's UID.

3.  **Build and Start Airflow Services:**
    ```bash
    make up
    ```
    This command will:
    -   Build the custom Airflow Docker image.
    -   Start all services (PostgreSQL, Redis, Airflow Webserver, Scheduler, Worker, Triggerer) in detached mode.
    -   The `airflow-init` service will run once to initialize the database and create the admin user specified in `.env`.

4.  **Access Airflow UI:**
    Open your browser and go to `http://localhost:8080` (or the port specified in `AIRFLOW_WEBSERVER_HOST_PORT` in `.env`).
    Log in with the admin credentials defined in `.env` (default: `admin`/`admin`).

5.  **Managing Services:**
    -   Stop services: `make stop`
    -   Stop and remove containers, networks, volumes: `make down`
    -   View logs: `make logs` or `make logs-webserver`
    -   Access Airflow CLI (e.g., in webserver container): `make shell`
        ```bash
        # Inside the container
        airflow dags list
        airflow tasks test example_etl_pipeline_v1 extract_data 2023-01-01
        ```

## EC2 Deployment

1.  **Launch and Configure EC2 Instance:**
    -   Choose an AMI (e.g., Ubuntu Server 22.04 LTS, Amazon Linux 2).
    -   Instance type: `t3.medium` or larger is recommended for production (at least 2 vCPUs, 4GB RAM).
    -   Security Group:
        -   Allow SSH (port 22) from your IP.
        -   Allow HTTP (port 80) and HTTPS (port 443) from the internet (or your specific IP range) if using Nginx.
        -   If not using Nginx and accessing Airflow directly, allow the `AIRFLOW_WEBSERVER_HOST_PORT` (default 8080).
    -   Attach an IAM Role (Recommended): Create an IAM role with policies for any AWS services Airflow might need to access (e.g., S3 for logs/dags, SSM for parameters, RDS).

2.  **Install Docker and Docker Compose on EC2:**
    Follow the official Docker documentation for your chosen Linux distribution.
    -   [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
    -   [Install Docker Engine on Amazon Linux 2](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html#install_docker)
    -   Ensure your EC2 user is part of the `docker` group to run Docker commands without `sudo`:
        ```bash
        sudo usermod -aG docker $(whoami)
        newgrp docker # Apply group changes without logging out/in
        ```

3.  **Transfer Project Files to EC2:**
    Use `scp` or `rsync` to copy your `airflow-ec2-setup` project directory to the EC2 instance.
    ```bash
    # Example using rsync (from your local machine)
    rsync -avz -e "ssh -i /path/to/your-key.pem" --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' ./ ubuntu@your-ec2-ip:/home/ubuntu/airflow-ec2-setup/
    ```

4.  **Set up `.env` on EC2:**
    SSH into your EC2 instance. Navigate to the project directory.
    Create or copy your `.env` file with production settings. **Ensure `AIRFLOW_FERNET_KEY` is securely set.**
    Consider using AWS Systems Manager Parameter Store for sensitive variables and fetching them at runtime or into the `.env` file.

5.  **Build and Run on EC2:**
    ```bash
    cd /home/ubuntu/airflow-ec2-setup # Or your project path
    make up
    ```

6.  **Access Airflow UI:**
    -   If using Nginx (ports 80/443): `http://your-ec2-public-ip` or `https://your-ec2-public-ip` (after SSL setup).
    -   If accessing Airflow webserver directly: `http://your-ec2-public-ip:8080`.

## Security Considerations

-   **Fernet Key**: Keep `AIRFLOW_FERNET_KEY` secret and backed up.
-   **Database Credentials**: Use strong, unique passwords for PostgreSQL. Consider using AWS RDS for PostgreSQL for managed security and backups. If using RDS, update `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` in `.env` and remove the `postgres` service from `docker-compose.yml`.
-   **Network Security**: Restrict access to ports using EC2 Security Groups.
-   **HTTPS/TLS**:
    -   The provided Nginx setup is a stub. For production HTTPS:
        1.  Obtain an SSL certificate (e.g., from Let's Encrypt using Certbot, or AWS Certificate Manager).
        2.  Update `config/nginx/default.conf.template` with your domain and certificate paths.
        3.  Mount your certificate and key into the Nginx container via volumes in `docker-compose.yml`.
        4.  Generate `dhparam.pem`:
            ```bash
            sudo openssl dhparam -out ./config/nginx/dhparam.pem 2048 # Run on EC2 in project dir
            ```
        5.  Uncomment the HTTPS server block in `config/nginx/default.conf.template`.
-   **Secrets Management**:
    -   The `.env` file is simple but not ideal for highly sensitive production secrets.
    -   **AWS SSM Parameter Store**: Store secrets in SSM and fetch them into the container's environment at startup. This requires `awscli` in the Docker image and an IAM role with `ssm:GetParameters` permission for the EC2 instance.
    -   **HashiCorp Vault**: Another robust option for secrets management.

## Logging

-   **Container Logs**: View with `make logs` or `docker-compose logs -f <service_name>`.
-   **Task Logs**: Stored in the `./logs` directory by default, which is mounted into the containers.
-   **Remote Logging**: For better persistence and centralized log management in production, configure remote logging (e.g., to AWS S3).
    1.  Ensure `apache-airflow-providers-amazon` is in `requirements.txt`.
    2.  Set the following environment variables in `.env` (or directly in `docker-compose.yml`):
        ```env
        AIRFLOW__LOGGING__REMOTE_LOGGING=True
        AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=aws_default # Or your specific AWS connection ID
        AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://your-airflow-logs-bucket/path/to/logs
        AIRFLOW__LOGGING__ENCRYPT_S3_LOGS=False # Set to True if SSE is desired
        ```
    3.  Create an Airflow connection named `aws_default` (or the ID you specified) with your AWS credentials, or ensure the EC2 instance has an IAM role with S3 write permissions to the bucket.
        -   **Permissions needed for IAM role/user**: `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on the specified bucket and prefix.
    4.  Update `config/airflow.cfg` if you prefer to set these there (though environment variables usually take precedence).

## Customizing and Extending

-   **Adding DAGs**: Place your Python DAG files in the `dags/` directory. Airflow will automatically discover them.
-   **Adding Plugins**: Place custom operators, hooks, sensors, or UI elements in the `plugins/` directory.
-   **Python Dependencies**: Add new Python packages to `requirements.txt` and rebuild the Airflow image:
    ```bash
    make build
    make up # To apply changes
    ```
-   **Airflow Configuration**: Modify `config/airflow.cfg` or set environment variables (prefixed with `AIRFLOW__SECTION__KEY`) in `.env` or `docker-compose.yml`.

## Development Best Practices

-   **Linting and Formatting**: Use pre-commit hooks for consistent code style.
    ```bash
    pip install pre-commit
    pre-commit install
    ```
    Now, `black`, `flake8`, and `isort` will run on `git commit`.
-   **Testing DAGs**:
    -   Write unit tests for your DAGs and custom logic. Place tests in the `tests/` directory.
    -   Run tests using `pytest`:
        ```bash
        # Ensure pytest is installed in your local environment
        pip install pytest apache-airflow  # Install airflow locally for testing context if needed
        make test
        # or
        pytest tests/
        ```
    -   Use `airflow dags test <dag_id> <execution_date>` for integration testing.
    -   Use `airflow tasks test <dag_id> <task_id> <execution_date>` to test individual tasks.

## Extending for CI/CD

This setup can be integrated into a CI/CD pipeline (e.g., Jenkins, GitLab CI, GitHub Actions).

1.  **Build Docker Image**: Your CI/CD pipeline should build the Airflow Docker image using the `Dockerfile`.
    ```bash
    docker build -t your-registry/your-airflow-image:tag .
    ```
2.  **Push to Registry**: Push the built image to a container registry (e.g., AWS ECR, Docker Hub, GitLab Registry).
    ```bash
    docker push your-registry/your-airflow-image:tag
    ```
3.  **Deployment Strategy**:
    -   **EC2 (Current Setup)**:
        -   The CI/CD pipeline can SSH into the EC2 instance.
        -   Pull the new image: `docker pull your-registry/your-airflow-image:tag`.
        -   Update the `AIRFLOW_IMAGE_NAME` in `.env` or directly in `docker-compose.yml` on the EC2 instance to use the new image tag.
        -   Restart services: `docker-compose up -d --remove-orphans`. (Be mindful of scheduler/worker downtime during updates. Consider blue/green or rolling updates if zero downtime is critical).
    -   **AWS ECS/Fargate**: See next section.

## Deploying to AWS ECS/Fargate (Future Extension)

This Docker Compose setup provides a good foundation for migrating to AWS ECS or Fargate for more managed container orchestration.

1.  **Containerize**: You already have Docker images.
2.  **Push Images to ECR**: Store your Airflow image (and Nginx image if used) in Amazon ECR.
3.  **Task Definitions**: Create ECS Task Definitions for each Airflow component (webserver, scheduler, worker, triggerer).
    -   Map environment variables from `.env` to the task definition (use AWS Secrets Manager or SSM Parameter Store for sensitive values).
    -   Configure CPU, memory, port mappings, and volume mounts (e.g., EFS for persistent DAGs/logs/plugins if not baked into the image or synced via other means).
4.  **Services**: Create ECS Services for long-running components (webserver, scheduler, worker, triggerer).
    -   Configure auto-scaling for workers.
    -   Use Application Load Balancer (ALB) for the webserver.
5.  **Database & Broker**:
    -   Use AWS RDS for PostgreSQL.
    -   Use AWS ElastiCache for Redis.
    -   Update Airflow connection strings accordingly.
6.  **DAGs & Plugins Storage**:
    -   **Bake into Image**: Simplest for versioning, but requires image rebuild for every DAG change.
    -   **AWS EFS**: Mount an EFS volume to your ECS tasks for DAGs and plugins.
    -   **S3 Sync**: Sync DAGs from an S3 bucket to the containers at startup or periodically.
7.  **Logging & Monitoring**: Integrate with AWS CloudWatch Logs and CloudWatch Metrics.

## Troubleshooting

-   **Permission Errors (Volumes)**: If you see permission errors related to mounted volumes (`dags/`, `logs/`, `plugins/`), ensure `AIRFLOW_UID` in your `.env` file matches the UID of the user owning these directories on your host machine (especially on Linux/macOS).
    ```bash
    # On your host machine (Linux/macOS)
    id -u
    # Set this value to AIRFLOW_UID in .env
    ```
    Then rebuild or restart: `make down && make up`. The `init_airflow.sh` script attempts to handle this.
-   **Services Not Starting**:
    -   Check logs: `make logs` or `docker-compose logs <service_name>`.
    -   Ensure `.env` variables are correctly set (especially `AIRFLOW_FERNET_KEY`, DB, and Redis details).
    -   Check resource limits on your Docker host / EC2 instance.
-   **Web UI Unresponsive**:
    -   Check `airflow-webserver` logs.
    -   Ensure `postgres` and `redis` services are healthy.
    -   Check Nginx logs if using the reverse proxy: `docker-compose logs nginx`.
-   **DAGs Not Appearing**:
    -   Check `airflow-scheduler` logs for DAG parsing errors.
    -   Ensure DAG files are in the `dags/` directory and have no syntax errors.
    -   Verify `.airflowignore` isn't unintentionally ignoring your DAG files.
-   **Tasks Stuck in Queued**:
    -   Check `airflow-scheduler` and `airflow-worker` logs.
    -   Ensure Celery workers are running and can connect to Redis and PostgreSQL.
    -   Verify `AIRFLOW__CORE__EXECUTOR` is `CeleryExecutor`.

## Makefile Commands

-   `make build`: Build or rebuild Docker images.
-   `make up`: Start all services in detached mode.
-   `make down`: Stop and remove containers, networks, and volumes.
-   `make stop`: Stop running services.
-   `make start`: Start existing stopped services.
-   `make restart`: Restart services.
-   `make logs`: Follow logs from all services.
-   `make logs-webserver`: Follow logs specifically from the webserver.
-   `make ps`: List running containers.
-   `make init`: Manually run the `airflow-init` service (DB migration, user creation).
-   `make clean`: Remove stopped containers and dangling Docker resources.
-   `make shell`: Access a bash shell inside the `airflow-webserver` container.
-   `make fernet-key`: Generate a new Fernet key.
-   `make test`: Run Pytest tests located in the `tests/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details (if you choose to add one).