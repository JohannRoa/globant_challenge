import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node PostgreSQL
PostgreSQL_node1698616615489 = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.jobs",
        "connectionName": "teste1",
    },
    transformation_ctx="PostgreSQL_node1698616615489",
)

# Script generated for node Amazon S3
AmazonS3_node1698617028424 = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="avro",
    connection_options={
        "paths": [
            "s3://globant-prueba/BACKUP/jobs/jobs_backup_2023-10-29T21-46-02.avro"
        ]
    },
    transformation_ctx="AmazonS3_node1698617028424",
)


# Convert data to a Spark DataFrame
spark_df = AmazonS3_node1698617028424.toDF().repartition(1).sortWithinPartitions("id",ascending=True)#.sort("id",ascending=True)


conn = glueContext.extract_jdbc_conf("teste1")
HOST_NAME = conn['host']
USERNAME = conn['user']
PASSWORD = conn['password']
PORT = conn['port']
DATABASE = "postgres"
URL = conn['url']+"/"+DATABASE
DRIVER = "org.postgresql.Driver"
table_name='jobs'

spark_df.write \
    .format("jdbc") \
    .option("url", URL) \
    .option("dbtable", table_name) \
    .option("user", USERNAME) \
    .option("password", PASSWORD) \
    .mode("overwrite") \
    .save()

# You might need to apply additional transformations here if the backup format differs from your database schema
"""
# Write data to the RDS database
table_name='jobs'
user_name = "postgres"#secret_json["username"]
password = "12345678"#secret_json["password"]
spark_df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://databasepsql.czrmhtxwh3mw.us-east-2.rds.amazonaws.com:5432/postgres") \
    .option("dbtable", table_name) \
    .option("user", user_name) \
    .option("password", password) \
    .mode("overwrite") \
    .save()
"""


job.commit()
