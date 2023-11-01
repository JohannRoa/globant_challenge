import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame


args = getResolvedOptions(sys.argv, ["JOB_NAME","TABLE_DATABASE","DATABASE","FILE_RESTORE"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

table_name=args['TABLE_DATABASE']

# Script generated for node Amazon S3
file_s3url_restoration = args['FILE_RESTORE']
AmazonS3_node1698617028424 = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="avro",
    connection_options={
        "paths": [
            file_s3url_restoration
        ]
    },
    transformation_ctx="AmazonS3_node1698617028424",
)

ChangeSchema_node1698593430546 = ApplyMapping.apply(
    frame=AmazonS3_node1698617028424,
     mappings=[("id", "int", "id", "bigint"), ("name", "string", "name", "string"),("datetime", "string", "datetime", "timestamp"),("department_id", "int", "department_id", "bigint"),("job_id", "int", "job_id", "bigint")],
    transformation_ctx="ChangeSchema_node1698593430546",
)
# Convert data to a Spark DataFrame
#  we use repartition 1 just because the data is small, this value must be different from 1 to take the benefits from spark is the data is big
spark_df = ChangeSchema_node1698593430546.toDF().repartition(1).sortWithinPartitions("id",ascending=True)


conn = glueContext.extract_jdbc_conf("teste1")
HOST_NAME = conn['host']
USERNAME = conn['user']
PASSWORD = conn['password']
PORT = conn['port']
DATABASE = args['DATABASE']#"postgres"
URL = conn['url']+"/"+DATABASE
DRIVER = "org.postgresql.Driver"


spark_df.write \
    .format("jdbc") \
    .option("truncate","true") \
    .option("url", URL) \
    .option("dbtable", table_name) \
    .option("user", USERNAME) \
    .option("password", PASSWORD) \
    .mode("overwrite") \
    .save()


job.commit()
