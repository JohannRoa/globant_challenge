# Globant Challenge
For this challenge, all the scripts and files used will be stored in folders named by the entities of the database. So every solution code for each table can be found in the folders.
## Challenge #1
**Part 1: Move historic data from files in CSV format to the new database**

Due to big data problem, the first task of migrating the data from csv will be solved by using AWS Glue. It is supposed that our data is stored in an S3. Probably the source could be an SFTP server, another database, an API, another cloud storage like GCP or even a webpage. However by doing all the extraction we can stored it in an s3 Bucket.

Due to the above, we are going to create Glue ETL jobs which load the CSV data from S3 to a new database,which will be created using RDS.

The RDS is created using Postgres 11 within a VPC (public, but only mi ip is whitelisted to prevent SQL injections):

hostname: *databasepsql.czrmhtxwh3mw.us-east-2.rds.amazonaws.com*
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/86b897e5-5e5c-4f76-b2c7-6d524efa9601)
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/dafd7795-8c0d-4ca1-8d24-ab7ba3c48ce6)

Now that our RDS is online, we can connect to it and create the tables within. The queries for the tables creation are stored in the SQL file at root. The database diagram will look like the image below:
![database_squeme](https://github.com/JohannRoa/globant_challenge/assets/32910991/ebf99bac-60d4-4134-b444-1d7d6ab9661d)


For the migration of the data, we must follow the next steps:

1. Create an endpoint on the VPC (which RDS uses) service that allows the service "com.amazonaws.us-east-2.s3" in gateway
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/7e005ae6-0e32-4fc1-8faa-c33f398ed43c)
2. Create a Glue connection by taking into account the credentials generated in RDS and selecting one subnet from the VPC
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/76e053e2-fdee-4844-91cb-17ab5d6fbcba)
3. Make a Glue crawler which uses the connection from above to generate (run the crawler after its creation) a Glue Catalog over the 3 tables of the RDS
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/45481041-9e62-408b-b48b-5d6e4260b346)
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/4d0f919b-3b63-4cab-b979-95b68eedfc70)
4. Create ETL jobs for each table, the source will be an S3, the target will be these tables from the Glue Catalog. The data must be transformed due to the non header behaviour of the CSV data and also the different type of variables over the data. The visual mode of this ETL give us something like this:
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/198b4202-e833-47b6-924c-b1caf0aaf0c9)

      In addition, by using the repository connection of Glue, we can deploy the  ETLs faster. There are 2 files for each ETL, one is the json configuration and the other the python script which uses the spark big data logic to do the process. The migration files are in the migration_history subfolders.

5. Run each ETL, if the configure files are ok, the processes will be successfull and our CSV data is now migrated!

**Part 2: Create a Rest API service to receive new data.** This service must have:
- Each new transaction must fit the data dictionary rules.
- Be able to insert batch transactions (1 up to 1000 rows) with one request.
- Receive the data for each table in the same service.
- Keep in mind the data rules for each table: Transactions that don't accomplish the rules must not be inserted but they must be
logged and all the fields are required.

To solve the problem of delivering data in real time, It is build a pipeline in AWS consisting in 3 services: API Gateway, Lambda and the RDS we have created.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/916cbeff-f359-4af2-8cb9-709402a8e456)

First we create an API REST service with 3 resources and a POST method within. Each resource-method will represent the data insertion over each table. 

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/d50c9908-6691-4071-9592-0e63cbd02915)

In the POST method configuration we must specify the following parameters in the integration request:
![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/d2fe7c3d-e582-4f90-8043-57ca828cb43c)

The above will connect the POST requests of the path to to invoke a lambda function, also is is imporant to enable the checkmark *Use Lambda Proxy integration* for controling responses in the lambda function.
Furthermore, we have used x-api-key as authentication for the API, so we set the value API Key Required for True in the Method requests configuration for all tables.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/4b12b7e0-e74d-4025-b0f1-913b73d537cd)

The Api Key is generated using the tool of API Key and we associate to this API by the Usage Plans

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/9f9e77aa-25b1-4e97-838e-1c3dad7a5ff2)

Finally this API Rest was built with the following base_url: *https://5qw4kk70ke.execute-api.us-east-2.amazonaws.com/v1*, each path has a throttling rate of 10000 requests per second with a burst of 5000 requests.

For the insert part, we have developed a lambda function named *InsertTables*. The function is built with python3.8 and a layer with the psycopg2 module (the .zip of the module is in root folder), which allow us to connect and performs inserts on the RDS. Addtionaly, the lambda is configured with 15 minute of timeout, 2GB of memory and 500MB of ephemeral memory. Without a doubt, this lambda will process batch transactions up to 1000 for earch request. On other hand, the lambda must be configured to work in the same VPC from the RDS.

The lambda was deployed 3 times, one per table code configuration (the scripts of the lambdas are stored in the folders). The three versions are associated with one alias which distinguished them.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/949529e3-03f5-4eff-a45f-e84431b0c30a)

Therefore, the body of the request must respect the data rules of the dictionary ("json"), the lambda code will control bad inputs from users and return 400 responses if needed. However, if the transactions meet the minimum requeriments the transactions can proceed, bad transactions will be logged in the success status response. For example:

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/9cbcae72-43c1-461f-8414-50d2759f5fd3)

A cURL example for the department resource is below:

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
 This request will fail if there is an id of 1 in the job table, However, if not, it will process the transactions and insert the first one. The remaining will be printed with the error as another field.

**Part 3: Create a feature to backup for each table and save it in the file system in AVRO format**

For this task, we will use again Glue, it is a powerfull tool for processing big data, also it facilitates the export of AVRO format. Thus, we are creating 3 ETLS to export each table. Also we can schedule each ETL to make a backup each month, so we stored it in S3. In this way, the ETL should be built with the database catalog of our RDS as origin source. Also this origin can be built with our glue connection of JDBC too. Thus, the target or destiny will be  S3, and we can configure format output options as AVRO. 

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/be0bf656-b3c0-40b4-97ac-2bae0d095af3)

The pair of scripts for each ETL are stored in the subfolder *backup*. Furthermore, these scripts reduce the number of repartitions to one due to the writing of just one file. When working with big data is not a good practice to work with 1 repartition, however, for this test little case we make the exception. 

The resulting AVRO files are stored in each folder due to the small size of them.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/b50d6d7b-90e1-476e-83ac-956e50fca8b8)

**Part4: Create a feature to restore a certain table with its backup**

Finally, for the restoration process we use Glue too. On the other hand, now the  source will be the S3 file and the destination will be the tables from the glue catalog associated with the RDS. Fortuntely Glue reads for us the AVRO file and make all the transformations for uploading them in the RDS. The scripts which helps these processes are stored in the subfolder *backup_restore_Glue*.

![image](https://github.com/JohannRoa/globant_challenge/assets/32910991/245ba331-7911-485a-bb2b-4d3f3a1f82c9)

For demonstrating the restoration ETL, all tables were truncated before running the jobs. All tables were repopulated, the procedure was sucessfull!






