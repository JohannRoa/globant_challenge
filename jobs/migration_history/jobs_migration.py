import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"],["CATALOG_DATABASE"],["CATALOG_TABLE_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Amazon S3
AmazonS3_node1698535119666 = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": False,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://globant-prueba/RAW_DATA/jobs/"],
        "recurse": True,
    },
    transformation_ctx="AmazonS3_node1698535119666",
)

# Script generated for node Change Schema
ChangeSchema_node1698593430546 = ApplyMapping.apply(
    frame=AmazonS3_node1698535119666,
    mappings=[("col0", "string", "id", "bigint"), ("col1", "string", "job", "string")],
    transformation_ctx="ChangeSchema_node1698593430546",
)

database = args['CATALOG_DATABASE']
table_name = args['CATALOG_TABLE_NAME']

# Script generated for node PostgreSQL
PostgreSQL_node1698535126643 = glueContext.write_dynamic_frame.from_catalog(
    frame=ChangeSchema_node1698593430546,
    database=database,
    table_name=table_name,
    transformation_ctx="PostgreSQL_node1698535126643",
)

job.commit()
