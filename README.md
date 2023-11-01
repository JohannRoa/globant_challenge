# Globant Challenge
For this challenge, all the scripts and files used will be stored in folders named by the entities of the database. So every solution code for each table can be found in the folders. The folders with names of example have the standard structure from some codes.
## Challenge #1
**Part 1**

Due to big data problem, the first task of migrating the data from csv will be solved by using AWS Glue. It is supposed that our data is stored in an S3. Probably the source could be an SFTP server, another database, an API, another cloud storage like GCP or even a webpage. However by doing all the extraction we can stored it in an s3 Bucket.

Due to the above, we are going to create Glue ETL jobs which load the CSV data from S3 to a new database,which will be created using RDS.

The RDS is created using Postgres 11 within a VPC open (public) for test purpose:

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

**Part 2**

