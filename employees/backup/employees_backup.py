import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME","CATALOG_DATABASE","CATALOG_TABLE_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
# set custom logging on
LOG = glueContext.get_logger()
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

database = args["CATALOG_DATABASE"]
table_database= args['CATALOG_TABLE_NAME']

# Script generated for node PostgreSQL
PostgreSQL_node1698597257601 = glueContext.create_dynamic_frame.from_catalog(
    database=database,
    table_name=table_database,
    transformation_ctx="PostgreSQL_node1698597257601",
)

repartitioned_data_frame=PostgreSQL_node1698597257601.toDF().repartition(1).sortWithinPartitions("id",ascending=True)
repartitioned_dynamic_frame = DynamicFrame.fromDF(repartitioned_data_frame, glueContext, "repartitioned_data_frame")

# Script generated for node Amazon S3
AmazonS3_node1698597325950 = glueContext.write_dynamic_frame.from_options(
    frame=repartitioned_dynamic_frame,
    connection_type="s3",
    format="avro",
    connection_options={
        "path": "s3://globant-prueba/BACKUP/jobs/",
        "partitionKeys": [],
    },
    transformation_ctx="AmazonS3_node1698597325950",
)

#The above line of code writes a single part file
import boto3
from datetime import datetime
client = boto3.client('s3')
s3_resource = boto3.resource('s3')
BUCKET_NAME= 'globant-prueba'
PREFIX ='BACKUP/jobs/'

#getting all the content/file inside the bucket. 
response = client.list_objects_v2(Bucket=BUCKET_NAME,Prefix=PREFIX)
names = response["Contents"]

#Find out the file which have part-000* in it's Key
particulars = [name['Key'] for name in names if 'part' in name['Key']]

timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
for particular in particulars:
    copy_source = {
        'Bucket': BUCKET_NAME,
        'Key': particular
    }
    s3_resource.meta.client.copy(copy_source, BUCKET_NAME, PREFIX+f"jobs_backup_{timestamp}.avro")
    client.delete_object(Bucket=BUCKET_NAME, Key=particular)

job.commit()
