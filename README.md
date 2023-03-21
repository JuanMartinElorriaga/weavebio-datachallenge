# Weavebio Data Engineering Coding Challenge

_tl;dr_: The challenge is to create a data pipeline that will ingest a UniProt XML file (`data/Q9Y261.xml`) and store the data in a Neo4j graph database.

The following data pipeline follows the process of downloading the `data/Q9Y261.xml` data file, parse it to extract the useful information and finally create a graph model and store it in a graph database. An additional query step has been made to show how to query the database. 
All the ETL process has been orchestrated and monitored using Airflow.

The Airflow DAG can be seen in `airflow-data -> dags -> airflow_DAG1.py`

### Tech stack

- Docker and Docker-Compose
- Neo4j (docker container)
- Python (docker container)
- Airflow (docker container)
- Bash scripting

### Features

- Easy deployment in minutes
- _100%_ open-source
- Add any linux packages and/or python libraries to the image easily
- All services run on docker containers to asure fast deployment, portability, consistency and simplified maintainance
- Use _CeleryExecutor_ instead of _LocalExecutor_ for simulating a hypotetical need to distribute jobs across multiple servers (horizontal scaling)
- Add _Flower_ for a web-based tool for monitoring and administrating Celery clusters.
- Use _PostgreSQL_ instead of _SQL Lite_ for hypothetical bigger scale project
- Use _bolt_ protocol instead of HTTP for optimal performance
- Created _index_ to improve the performance of protein searching

### How to deploy

**Prerequisite**: Docker and docker-compose to be installed. 

**Step 1:** Go through the `.env file`, `init_airflow_setup.sh`, `docker-compose.yml` file`s to change settings according to your preference. Or you can just keep them as it is for local development.

**Step 2:** Run `docker-compose build` (only once). This will build the Docker image based on the _Dockerfile_.

**Step 2:** Run `docker-compose up`. You can also add the `-d` flag for detached mode.

**Step 3:** Run `sh init_airflow_setup.sh` (Run this only for initial deployment). This will initialize the airflow instance, create the user with password and upgrade the database. 
Note that in case of using Windows OS, the bash script can be run this way in a Git Bash: `winpty sh init_airflow_setup.sh`.

**Step 4:** Go to http://localhost:8080 and login with user: _airflow_test_user_ and password: _airflow_test_password_ as specified in `init_airflow_setup.sh` script. 
Also, for only the first time, the neo4j connector needs to be configured by going to _Admin -> Connections_, and setting a filling the form with the following values:
1. Go to the Airflow UI and click on the *"Admin"* menu.
2. Click on _"Connections"_ to open the connections page.
3. Click on the _"Create"_ button to create a new connection.
4. In the _"Conn Id"_ field, enter: *neo4j_default*.
5. In the _"Conn Type"_ dropdown, select *Neo4j*.
6. In the _"Host"_ field, enter: *neo4j_host*.
7. In the _"Port"_ field, enter: *7687*.
8. In the _"Login"_ field, enter: *neo4j*.
9. In the _"Password"_ field, enter *user_password*.

**Step 5:** Use the Airflow UI to run the `uniprot_neo4j_pipeline`. You can access http://localhost:7474 as well for the _Neo4j browser_ and run some Cypher queries there, after connecting to the Neo4j graph database located at http://localhost:7687, with same user and password as the previous step.


