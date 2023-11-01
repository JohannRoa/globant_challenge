# Globant Challenge

This README.md follows the steps to develop the required project described in the file "coding_challengeGlobant.pdf"
In this challenge, all scripts and files are organized into folders named after the entities in the database. This structure makes it easy to locate the solution code for each table.

## Challenge #1

### Part 1: Move historic data from files in CSV format to the new database

To address the challenge of migrating data from CSV files to the new database, we employ AWS Glue. The source data is assumed to be stored in an S3 bucket, although it could come from various sources such as an SFTP server, another database, an API, another cloud storage service like GCP, or even a webpage. Regardless of the source, we extract the data and store it in an S3 bucket.

The migration process involves creating Glue ETL jobs that load CSV data from S3 into a new database created using RDS (Relational Database Service). This RDS instance uses Postgres 11 and resides within a VPC (Virtual Private Cloud), which is public but only allows whitelisted IP addresses to prevent SQL injections. The RDS instance is accessible at the following hostname: `databasepsql.czrmhtxwh3mw.us-east-2.rds.amazonaws.com`.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/86b897e5-5e5c-4f76-b2c7-6d524efa9601)
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/dafd7795-8c0d-4ca1-8d24-ab7ba3c48ce6)

Now that the RDS is online, we can connect to it and create the necessary tables. The SQL queries for table creation are stored in an SQL file located at the root of this project. The database schema is visualized in the image below:
![database_squeme](https://github.com/JohannRoa/globant_challenge/assets/32910991/ebf99bac-60d4-4134-b444-1d7d6ab9661d)


To migrate the data, follow these steps:

1. Create a VPC endpoint to allow the "com.amazonaws.us-east-2.s3" service to communicate with the RDS instance, which it uses as a gateway.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/7e005ae6-0e32-4fc1-8faa-c33f398ed43c)

2. Establish a Glue connection, taking into account the credentials generated in RDS, and select a subnet from the VPC.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/76e053e2-fdee-4844-91cb-17ab5d6fbcba)

3.Create a Glue Crawler, which uses the previously established connection to generate a Glue Catalog for the three tables in the RDS. Be sure to run the crawler after its creation.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/45481041-9e62-408b-b48b-5d6e4260b346)
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/4d0f919b-3b63-4cab-b979-95b68eedfc70)

4. Develop ETL jobs for each table. The source will be an S3 bucket, and the target will be the tables from the Glue Catalog. The data must undergo transformations due to the non-header behavior of the CSV data and the variation in data types. The visual representation of this ETL might resemble the following:

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/198b4202-e833-47b6-924c-b1caf0aaf0c9)

An important feature to enable is the bookmark in the Glue interface, which provides memory to the jobs to avoid duplicating information. This is particularly useful when running asynchronous jobs that process new S3 files. Additionally, Glue's repository connection allows for faster deployment of ETLs. Each ETL consists of two files: a JSON configuration file and a Python script using Spark for processing the data. The migration files are stored in the "migration_history" subfolders.

5. Execute each ETL job. If the configuration files are correct, the processes will be successful, and your CSV data will be successfully migrated!

### Part 2: Create a REST API Service to Receive New Data

The REST API service created for this challenge must meet the following criteria:
- Each new transaction must adhere to the data dictionary rules.
- It should support batch transactions, allowing the insertion of 1 to 1000 rows with a single request.
- The service should accept data for each table within the same service.
- Data validation rules for each table must be enforced, and transactions that do not meet these rules should not be inserted, but they should be logged. All fields are required.

To achieve real-time data delivery, an AWS pipeline is constructed, consisting of three services: API Gateway, Lambda, and the previously created RDS.

![Architecture (1)](https://github.com/JohannRoa/globant_challenge/assets/32910991/843b1bf3-a78f-4935-ac34-f41fe6e739dd)

The initial step involves creating a REST API service with three resources and a POST method for each. Each resource-method represents data insertion for a specific table.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/d50c9908-6691-4071-9592-0e63cbd02915)

In the POST method configuration, specific parameters must be set in the integration request:

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/d2fe7c3d-e582-4f90-8043-57ca828cb43c)

This setup links POST requests to invoke a Lambda function. It's important to enable the "Use Lambda Proxy Integration" option to control responses in the Lambda function. Authentication for the API is implemented using x-api-key, and "API Key Required" is set to true in the Method requests configuration for all tables.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/4b12b7e0-e74d-4025-b0f1-913b73d537cd)

API keys are generated using the API Key tool and associated with this API through Usage Plans.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/9f9e77aa-25b1-4e97-838e-1c3dad7a5ff2)

Finally, the REST API is accessible at the following base URL: `https://5qw4kk70ke.execute-api.us-east-2.amazonaws.com/v1`. Each path has a throttling rate of 10,000 requests per second with a burst of 5,000 requests.

For data insertion, a Lambda function named "InsertTables" is developed. This function is built with Python 3.8 and utilizes a layer with the psycopg2 module (the .zip of the module is located in the root folder). This module allows the Lambda to connect to the RDS and perform inserts. The Lambda is configured with a timeout of 15 minutes, 2GB of memory, and 500MB of ephemeral memory. It can process batch transactions of up to 1,000 rows in a single request. Additionally, the Lambda must be configured to work within the same VPC as the RDS.

The Lambda function is deployed three times, one for each table's code configuration, and the scripts for these Lambdas are stored in the respective folders. These three versions are associated with a distinct alias for differentiation.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/949529e3-03f5-4eff-a45f-e84431b0c30a)

The request body must adhere to the data rules defined in the data dictionary (JSON). The Lambda code will validate input data from users and return a 400 response for invalid body type or duplicated id. If the transactions meet the minimum requirements, they will be processed, valid transactions will be inserted and invalid transactions will be logged in the success status response.

For example:

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/9cbcae72-43c1-461f-8414-50d2759f5fd3)

A cURL example for the "department" resource is provided below. This request will fail if an "id" of 1 already exists in the "job" table. However, if not, the Lambda will process the transactions, inserting the first one, while the remaining invalid transactions will be included in the error response.

```
curl --location 'https://5qw4kk70ke.execute-api.us-east-2.amazonaws.com/v1/jobs' \
--header 'x-api-key: **************' \
--header 'Content-Type: application/json' \
--data ' [
        {
            "id": 1,
            "job": "hey"
        },
        {
            "id": 2,
            "name": "name2 surname2",
            "datetime": "2021-11-07T02:41:42Z",
            "department_id": 1,
            "job_id": 1
        },
        {
            "id": 3,
            "name": "name3 surname3",
            "datetime": "2021-11-07T02:49:42Z",
            "department_id": 1,
            "job_id": 1
        },
        {
            "id": 4,
            "name": "name3 surname3",
            "datetime": "2021-11-07T02:49:42Z",
            "department_id": 1,
            "job_id": 1
        }
    ]
'
```

### Part 3: Create a Feature for Backup of Each Table in AVRO Format

To address the backup feature, we again turn to AWS Glue, a powerful tool for processing big data and facilitating data export in AVRO format. We create three ETLs to export each table. These ETLs can be scheduled to run periodically to create backups, which are stored in S3. The ETLs are designed to use the database catalog from our RDS as the source. Additionally, the source can be built using the Glue JDBC connection.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/be0bf656-b3c0-40b4-97ac-2bae0d095af3)

The destination or target for these ETLs is S3, and we configure the output format as AVRO.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/b50d6d7b-90e1-476e-83ac-956e50fca8b8)

For simplicity, the scripts for each ETL are stored in the "backup" subfolders. These scripts limit the number of repartitions to one, although working with a single repartition is generally discouraged for big data. However, for this small-scale project, this approach is acceptable.

The resulting AVRO files are stored in this repository in their respective folders due to their small file size.

### Part 4: Create a Feature to Restore a Specific Table from Its Backup

For the restoration process, we again rely on AWS Glue. The source is now the AVRO file stored in S3, and the destination is the tables within the Glue catalog associated with the RDS. Glue automatically reads the AVRO file and handles all necessary transformations, including mapping columns, for uploading the data to the RDS. The scripts that facilitate these processes are stored in the "backup_restore_Glue" subfolder.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/cbecfebf-4045-4d2e-85b7-68e2684d48ef)

To demonstrate the restore ETL procedure, all tables were truncated before running the jobs. After the jobs were executed, the tables were successfully repopulated, indicating a successful restoration process.

## Challenge #2

For the data analysis task, we will run various queries on the database created in the first challenge. The queries are located in the "Challenge2" folder.

Analyzing the distribution of total employees grouped by "department_id" and year, we observe that some "department_ids" do not match the values in the "department_id" table. These anomalies appear to be outliers. However, when performing inner joins on shared keys, these outliers are removed from the results. A similar pattern is observed with "job_id."

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/9a7852ab-b406-4309-bae1-e6a6e294e5f9)
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/5044f2bd-69bb-41d4-b4e6-e6e7b92a820e)


The first query calculates the number of employees hired for each job and department in 2021, divided by quarter. A sample result for the first department and job arranged alphabetically is shown below:

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/62d63738-cd1f-4550-ad7b-7daccf6ec68a)

The second query provides a list of department IDs, names, and the number of employees hired by each department, comparing it to the mean number of employees hired in 2021 for all departments. The results are presented as follows:

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/1d2955ce-ebea-4f94-9598-638ee42befed)

Data from these queries are exported to CSV files located in the designated folder.

For a more in-depth understanding of these results, a Jupyter notebook is available for generating plots and conducting further data analysis and exploration. Refer to the "plots.ipynb" for an extended analysis of the data.






