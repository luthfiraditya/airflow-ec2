# Airflow Deployment Runbook

This runbook provides step-by-step instructions for deploying and updating the Airflow environment on EC2.

## Initial Deployment

### Prerequisites
- AWS EC2 instance (t3.medium or larger recommended)
- Docker and Docker Compose installed
- Git installed
- Domain name (if using HTTPS with Nginx)

### Deployment Steps

1. **Clone the Repository**
   ```bash
   git clone https://your-repository-url/airflow-ec2-setup.git
   cd airflow-ec2-setup

- Configure Environment Variables

```bash
# Generate a Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Copy the example .env file and update it
cp .env.example .env
# Edit .env with appropriate values, including the generated Fernet key
 ```
```
- Initialize the Environment

```bash
make init
 ```
- Start Airflow Services

```bash
make up
 ```
- Configure HTTPS (if using Nginx)

```bash
# Create directories for Let's Encrypt
mkdir -p letsencrypt/etc
mkdir -p letsencrypt/var/www/certbot

# Obtain SSL certificate
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot --email your-email@example.com -d your.airflow.domain.com --agree-tos --no-eff-email --force-renewal

# Restart Nginx to apply SSL
docker-compose up -d --force-recreate nginx certbot
 ```
```


## Deployment Process
1. Commit DAG to Git Repository
   
   ```bash
   git add dags/your_new_dag.py
   git commit -m "Add new DAG for domain process"
   git push
    ```
   ```
2. CI/CD Pipeline
   
   - Automated tests will run
   - DAG validation will occur
   - If tests pass, DAG will be deployed to production
3. Monitoring
   
   - Monitor the first few runs of your DAG
   - Check for any errors or performance issues
   - Adjust as needed