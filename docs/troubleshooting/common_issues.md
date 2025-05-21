# Common Issues Troubleshooting Guide

This guide provides solutions for common issues you might encounter with the Airflow deployment.

## DAG Issues

### DAG Not Appearing in the UI

**Symptoms:**
- DAG file exists in the `dags/` directory but doesn't appear in the Airflow UI

**Possible Causes and Solutions:**

1. **Syntax Error in DAG File**
   - Check the scheduler logs for parsing errors:
     ```bash
     make logs-scheduler
     ```
   - Fix any syntax errors in the DAG file

2. **DAG ID Conflict**
   - Ensure the DAG ID is unique across all DAGs
   - Check if the DAG is paused in the Airflow UI

3. **File Permissions Issue**
   - Ensure the DAG file has proper permissions:
     ```bash
     chmod 644 dags/your_dag.py
     ```

4. **Ignored by .airflowignore**
   - Check if the file pattern matches any patterns in `.airflowignore`

### Tasks Stuck in "Queued" State

**Symptoms:**
- Tasks remain in "Queued" state and don't get executed

**Possible Causes and Solutions:**

1. **Worker Not Running or Not Connected**
   - Check worker status:
     ```bash
     make ps
     ```
   - Check worker logs:
     ```bash
     docker-compose logs airflow-worker
     ```
   - Restart the worker:
     ```bash
     docker-compose restart airflow-worker
     ```

2. **Redis Connection Issues**
   - Check Redis logs:
     ```bash
     docker-compose logs redis
     ```
   - Verify Redis connection in Airflow configuration

3. **Worker Out of Resources**
   - Check EC2 resource utilization (CPU, memory)
   - Adjust worker concurrency in `.env`:
     ```
     AIRFLOW__CELERY__WORKER_CONCURRENCY=4
     ```

4. **Task Queue Misconfiguration**
   - Ensure tasks are assigned to queues that workers are listening to

### Tasks Failing with "Import Error"

**Symptoms:**
- Tasks fail with import errors in the logs

**Possible Causes and Solutions:**

1. **Missing Python Package**
   - Add the required package to `requirements.txt`
   - Rebuild the Airflow image:
     ```bash
     make build
     make up
     ```

2. **Custom Module Not in PYTHONPATH**
   - Ensure custom modules are in the `plugins/` directory
   - Or add the directory to PYTHONPATH in `.env`

## System Issues

### Webserver Not Accessible

**Symptoms:**
- Unable to access the Airflow UI in the browser

**Possible Causes and Solutions:**

1. **Webserver Container Not Running**
   - Check container status:
     ```bash
     make ps
     ```
   - Check webserver logs:
     ```bash
     make logs-webserver
     ```
   - Restart the webserver:
     ```bash
     docker-compose restart airflow-webserver
     ```

2. **Nginx Configuration Issue**
   - Check Nginx logs:
     ```bash
     docker-compose logs nginx
     ```
   - Verify Nginx configuration

3. **EC2 Security Group Issue**
   - Ensure ports 80/443 are open in the EC2 security group
   - Check if the EC2 instance is reachable

4. **SSL Certificate Issue**
   - Check if SSL certificates are valid and properly configured
   - Renew certificates if needed:
     ```bash
     docker-compose run --rm certbot renew
     ```

### Database Connection Issues

**Symptoms:**
- Services fail to start with database connection errors
- "OperationalError" in logs

**Possible Causes and Solutions:**

1. **PostgreSQL Container Not Running**
   - Check container status:
     ```bash
     make ps
     ```
   - Check PostgreSQL logs:
     ```bash
     docker-compose logs postgres
     ```
   - Restart PostgreSQL:
     ```bash
     docker-compose restart postgres
     ```

2. **Incorrect Database Credentials**
   - Verify database credentials in `.env`
   - Ensure they match what PostgreSQL is configured with

3. **Database Initialization Failed**
   - Run the initialization process:
     ```bash
     make init
     ```

4. **Database Corruption**
   - Restore from backup or reinitialize (data loss warning):
     ```bash
     make down
     docker volume rm airflow-ec2-setup_postgres-db-volume
     make init
     make up
     ```

### Out of Disk Space

**Symptoms:**
- Services failing to start or run
- "No space left on device" errors in logs

**Possible Causes and Solutions:**

1. **Log Files Accumulation**
   - Check disk usage:
     ```bash
     df -h
     ```
   - Clean up old logs:
     ```bash
     find logs -type f -name "*.log" -mtime +30 -delete
     ```

2. **Docker Images and Volumes**
   - Clean up unused Docker resources:
     ```bash
     make clean
     ```
   - Remove unused images:
     ```bash
     docker image prune -a
     ```

3. **EC2 Volume Size**
   - Increase EBS volume size in AWS console
   - Extend the filesystem after resizing

## Performance Issues

### Slow Task Execution

**Symptoms:**
- Tasks take longer than expected to complete

**Possible Causes and Solutions:**

1. **Insufficient Resources**
   - Check EC2 resource utilization
   - Upgrade to a larger EC2 instance type
   - Optimize task resource usage

2. **Database Performance**
   - Monitor database performance
   - Consider moving to RDS
   - Optimize queries in custom operators

3. **Network Latency**
   - Check if tasks are making external API calls
   - Consider moving EC2 instance closer to external resources

### High CPU/Memory Usage

**Symptoms:**
- EC2 instance shows high CPU or memory utilization
- Tasks failing due to memory errors

**Possible Causes and Solutions:**

1. **Too Many Concurrent Tasks**
   - Adjust parallelism settings in `.env`:
     ```
     AIRFLOW__CORE__PARALLELISM=16
     AIRFLOW__CORE__DAG_CONCURRENCY=8
     ```

2. **Memory Leaks in Custom Code**
   - Review custom operators and functions for memory leaks
   - Add proper resource cleanup

3. **Database Connections Not Being Closed**
   - Ensure database connections are properly closed in custom code
   - Adjust connection pool settings

## Recovery Procedures

### Recovering from a Crashed System

1. **Assess the Situation**
   - Check logs to determine the cause of the crash
   - Verify EC2 instance status

2. **Restart Services**
   ```bash
   make down
   make up

- Verify Database Integrity

- Check if the database is accessible
- Run a test query to verify data integrity
- Check DAG Status

- Verify DAGs are being parsed correctly
- Check for any failed task instances that need attention


### Recovering from a Failed Upgrade
1. Roll Back to Previous Version
   
   ```bash
   git checkout <previous-commit-hash>
   make down
   make build
   make up
    ```
   ```
2. Restore Database if Needed
   
   - Restore from the backup taken before the upgrade
3. Verify System Functionality
   
   - Check all components are running
   - Test a simple DAG run
```plaintext

Finally, let's create a monitoring strategy document:

```markdown:d%3A%5Cinsignia%5Cluthfi%5Coffice_work%5Cadhi_karya%5Cairflow-ec2-setup%5Cdocs%5Cmonitoring%5Cmonitoring_strategy.md
# Airflow Monitoring Strategy

This document outlines our approach to monitoring the Airflow environment, including what metrics to track, alerting thresholds, and response procedures.

## Monitoring Objectives

1. **System Health**: Ensure all Airflow components are operational
2. **Performance**: Track resource utilization and task execution times
3. **DAG Success**: Monitor DAG and task success/failure rates
4. **Resource Utilization**: Track EC2 and container resource usage
5. **Security**: Monitor for unauthorized access attempts

## Monitoring Tools

### Core Monitoring Stack

1. **CloudWatch** (AWS native monitoring)
   - EC2 instance metrics (CPU, memory, disk, network)
   - Custom metrics for Airflow components
   - Logs aggregation

2. **Prometheus & Grafana** (Optional enhanced monitoring)
   - More detailed metrics collection
   - Custom dashboards
   - Longer retention of metrics history

3. **Airflow's Built-in Monitoring**
   - Web UI for task status
   - Logs for detailed debugging
   - Metrics view in the UI

## Key Metrics to Monitor

### System-level Metrics

1. **EC2 Instance**
   - CPU Utilization (%) - Alert threshold: >80% for 15 minutes
   - Memory Utilization (%) - Alert threshold: >85% for 15 minutes
   - Disk Usage (%) - Alert threshold: >85%
   - Network I/O - For baseline and anomaly detection

2. **Docker Containers**
   - Container CPU usage
   - Container memory usage
   - Container restarts - Alert threshold: >3 restarts in 1 hour

### Airflow-specific Metrics

1. **Scheduler**
   - Heartbeat - Alert if missing for >5 minutes
   - DAG processing time - Alert if consistently increasing
   - DAG file parsing errors - Alert on any errors

2. **Workers**
   - Task processing time
   - Queue length - Alert if >100 tasks queued for >15 minutes
   - Worker heartbeat - Alert if missing for >5 minutes

3. **Webserver**
   - Response time - Alert if >2 seconds for 5 minutes
   - Error rate - Alert if >1% errors for 5 minutes
   - Active sessions

4. **DAGs and Tasks**
   - Success rate (%) - Alert if <95% for critical DAGs
   - Duration - Alert if >150% of average duration
   - SLA misses - Alert on any SLA miss

5. **Database**
   - Connection pool usage
   - Query performance
   - Database size growth

## Alerting Strategy

### Alert Severity Levels

1. **Critical (P1)**
   - System-wide outage
   - Scheduler not running
   - Database unavailable
   - Multiple critical DAGs failing
   - Response: Immediate action required (24/7)

2. **High (P2)**
   - Single critical DAG failing
   - Worker not processing tasks
   - High resource utilization affecting performance
   - Response: Action required within 1 hour (business hours)

3. **Medium (P3)**
   - Non-critical DAG failures
   - Slow performance
   - Warning-level resource utilization
   - Response: Action required within 1 business day

4. **Low (P4)**
   - Minor issues
   - Non-urgent improvements
   - Response: Scheduled maintenance

### Alert Notification Channels

1. **Email**
   - All alert levels
   - Configured in Airflow for task/DAG failures

2. **Slack/Teams**
   - P1, P2, and P3 alerts
   - Dedicated channel for Airflow alerts

3. **PagerDuty/OpsGenie**
   - P1 and P2 alerts only
   - On-call rotation for urgent issues

## Monitoring Implementation

### CloudWatch Setup

1. **EC2 Metrics**
   - Enable detailed monitoring for the EC2 instance
   - Create CloudWatch alarms for CPU, memory, and disk usage

2. **Custom Metrics**
   - Install CloudWatch agent on the EC2 instance
   - Configure custom metrics collection for Airflow components

3. **Log Groups**
   - Create log groups for Airflow components
   - Set up log retention policies

### Prometheus & Grafana Setup (Optional)

1. **Prometheus Installation**
   ```bash
   # Add to docker-compose.yml
   prometheus:
     image: prom/prometheus
     volumes:
       - ./config/prometheus:/etc/prometheus
       - prometheus-data:/prometheus
     ports:
       - "9090:9090"
     restart: unless-stopped
 ```
```

2. Grafana Installation
   
   ```bash
   # Add to docker-compose.yml
   grafana:
     image: grafana/grafana
     volumes:
       - grafana-data:/var/lib/grafana
     ports:
       - "3000:3000"
     restart: unless-stopped
    ```
   ```
3. Airflow Metrics Export
   
   - Enable StatsD or Prometheus metrics in Airflow configuration
   - Configure exporters for system metrics
### Airflow Health Checks
1. Scheduler Health Check
   
   ```bash
   # Add to crontab
   */5 * * * * docker-compose ps | grep airflow-scheduler | grep -q Up || (docker-compose restart airflow-scheduler && mail -s "Airflow Scheduler Restarted" admin@example.com)
    ```
   ```
2. Worker Health Check
   
   ```bash
   # Add to crontab
   */5 * * * * docker-compose ps | grep airflow-worker | grep -q Up || (docker-compose restart airflow-worker && mail -s "Airflow Worker Restarted" admin@example.com)
    ```
   ```
## Response Procedures
### Critical Alert Response
1. Initial Assessment
   
   - Check Airflow UI and logs
   - Verify all containers are running
   - Check resource utilization
2. Common Actions
   
   - Restart failed components:
     ```bash
     docker-compose restart <service_name>
      ```
     ```
   - Check for disk space issues:
     ```bash
     df -h
      ```
   - Check for memory pressure:
     ```bash
     free -m
      ```
3. Escalation Path
   
   - If unable to resolve within 30 minutes, escalate to senior engineer
   - If system-wide impact, notify stakeholders
### Performance Degradation Response
1. Identify Bottleneck
   
   - Check CPU, memory, disk I/O, and network metrics
   - Review slow-running tasks in Airflow UI
2. Mitigation Actions
   
   - Pause non-critical DAGs temporarily
   - Adjust concurrency settings
   - Clear out old task instances:
     ```bash
     docker-compose exec airflow-webserver airflow db clean
      ```
     ```
3. Long-term Solutions
   
   - Upgrade EC2 instance type
   - Optimize DAG code
   - Consider architectural changes
## Dashboard Guide
See Dashboard Guide for details on setting up and using monitoring dashboards.

## Regular Maintenance
1. Daily Checks
   
   - Review failed tasks from the previous day
   - Check resource utilization trends
2. Weekly Maintenance
   
   - Review slow-running DAGs
   - Check disk space usage
   - Verify backup processes
3. Monthly Review
   
   - Analyze performance trends
   - Review and adjust alert thresholds
   - Test recovery procedures
```plaintext

Let's create a dashboard guide to complete the documentation:

```markdown:d%3A%5Cinsignia%5Cluthfi%5Coffice_work%5Cadhi_karya%5Cairflow-ec2-setup%5Cdocs%5Cmonitoring%5Cdashboard_guide.md
# Monitoring Dashboard Guide

This guide describes the monitoring dashboards available for our Airflow environment and how to use them effectively.

## Available Dashboards

### 1. Airflow UI Dashboard

The built-in Airflow UI provides several monitoring views:

- **DAGs View**: Overview of all DAGs and their status
- **Tree View**: Historical view of DAG runs
- **Graph View**: Task dependencies and status
- **Task Duration**: Historical task duration
- **Gantt Chart**: Task timing and overlap
- **Landing Times**: When tasks completed relative to schedule
- **Metrics**: System metrics if StatsD/Prometheus is enabled

**Access**: https://your-airflow-domain.com

### 2. CloudWatch Dashboards

We have created custom CloudWatch dashboards for monitoring the EC2 instance and Airflow components.

#### EC2 System Dashboard

Monitors the overall health of the EC2 instance:

- CPU Utilization
- Memory Usage
- Disk Space
- Network I/O
- System Load

**Access**: AWS Console > CloudWatch > Dashboards > Airflow-EC2-System

#### Airflow Components Dashboard

Monitors specific Airflow components:

- Scheduler Health
- Worker Task Processing
- Webserver Response Time
- DAG Processing Time
- Task Success/Failure Rate

**Access**: AWS Console > CloudWatch > Dashboards > Airflow-Components

### 3. Grafana Dashboards (Optional)

If using Prometheus and Grafana, we have the following dashboards:

#### Airflow Overview

- DAG success rates
- Task duration percentiles
- Queue depth
- Scheduler performance

**Access**: http://your-ec2-ip:3000/dashboards/airflow-overview

#### System Resources

- Detailed CPU, memory, disk, and network metrics
- Container-specific resource usage
- Resource usage by task type

**Access**: http
 ```
```