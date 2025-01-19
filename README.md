# Data-engineering--Realtime-Data-Streaming
# Spark Data Streaming with Kafka and Cassandra

## Overview

This project demonstrates how to use Apache Spark to stream data from a Kafka topic and write it to a Cassandra database. The code reads user data from a Kafka topic called `users_created`, processes the data in real-time using Apache Spark, and inserts it into a Cassandra table `created_users`. The project is designed to showcase real-time data streaming and persistence in a distributed environment, while also providing logging to track progress and debug issues.

## Features

- **Kafka Integration**: Streams data in real-time from a Kafka topic (`users_created`).
- **Apache Spark**: Processes and transforms data in real-time.
- **Cassandra Persistence**: Inserts processed data into a Cassandra database.
- **Logging**: Provides detailed logging to help with debugging and progress tracking.
- **Automatic Keyspace and Table Creation**: The script creates a keyspace and table in Cassandra if they do not exist.

# User Automation DAG

This project implements an Apache Airflow Directed Acyclic Graph (DAG) to automate the process of fetching random user data from an API, formatting the data, and streaming it to a Kafka topic. The DAG is scheduled to run daily.

## Features

- Fetch random user data from the [Random User API](https://randomuser.me/).
- Format the data into a structured dictionary with detailed user information.
- Stream the data to a Kafka topic (`users_created`) for further processing.
- Highly modular design for better readability and scalability.

---

## Project Structure

### 1. **Python Functions**
- **`get_data()`**: Fetches random user data from the API.
- **`format_data(res)`**: Formats the fetched data into a structured dictionary.
- **`stream_data()`**: Streams formatted user data to the Kafka topic `users_created`.

### 2. **Airflow DAG**
- **`user_automation`**: The DAG orchestrates the workflow and executes the tasks.

---

## Prerequisites

1. **Apache Airflow**: Ensure you have Airflow installed and configured.
   ```bash
   pip install apache-airflow

# Docker Compose Setup for Streaming Data with Kafka, Zookeeper, and Airflow

This repository provides a Docker Compose setup for an ETL pipeline involving **Kafka**, **Zookeeper**, **Airflow**, **Spark**, and other components. The setup facilitates streaming data and data orchestration. Below is an overview of the services and their configurations.

---

## 🛠️ **Services Overview**

### 1. **Zookeeper**
   - Manages coordination for Kafka.
   - Port: `2181`.
   - Healthcheck ensures Zookeeper is ready before Kafka starts.

### 2. **Kafka Broker**
   - Handles message queuing and streaming.
   - Port: `9092` (host) and `29092` (internal).
   - Depends on Zookeeper.

### 3. **Schema Registry**
   - Provides schema management for Kafka topics.
   - Port: `8081`.
   - Depends on the Kafka broker.

### 4. **Control Center**
   - Confluent Control Center for monitoring and managing Kafka.
   - Port: `9021`.
   - Depends on the Kafka broker and Schema Registry.

### 5. **Apache Airflow**
   - Workflow orchestration for ETL pipelines.
   - Webserver: Port `8082`.
   - Scheduler and PostgreSQL database for backend management.
   - Includes DAGs and requirements mounting for customization.

### 6. **PostgreSQL**
   - Backend database for Airflow.
   - Preconfigured credentials:
     - Username: `airflow`
     - Password: `airflow`
     - Database: `airflow`.

### 7. **Spark Cluster**
   - For distributed data processing.
   - Spark Master: Ports `9090` (UI) and `7077` (communication).
   - Spark Worker: Connects to the master.

### 8. **Cassandra Database**
   - NoSQL database for storing data from the pipeline.
   - Port: `9042`.
   - Default credentials:
     - Username: `cassandra`
     - Password: `cassandra`.

---

## 🔧 **Getting Started**

### Prerequisites
- Install Docker and Docker Compose.
- Allocate sufficient resources to Docker (CPU, memory, etc.) for running multiple containers.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/docker-etl-setup.git
   cd docker-etl-setup
