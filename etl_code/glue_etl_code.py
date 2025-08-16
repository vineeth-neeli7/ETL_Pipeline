import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql.functions import col, coalesce, to_date, year,trim, round as spark_round
from pyspark.sql.types import IntegerType, LongType, FloatType, StringType, DateType, DecimalType

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext); job.init(args['JOB_NAME'], args)

# 1) Read from Catalog (update table_name to the actual table from your crawler)
dyf = glueContext.create_dynamic_frame.from_catalog(
    database="sales_data_raw_team2",
    table_name="team2_raw",  
    transformation_ctx="dyf"
)
df = dyf.toDF()

df = (df
    .withColumn("order_id", col("order_id").cast(LongType()))
    .withColumn("quantity",   col("quantity").cast(LongType()))
)
#df = df.dropna(how='all').filter(col("quantity") > 0)
df = df.filter(col("quantity").isNotNull() & (col("quantity") > 0))
df = df.filter(col("order_id").isNotNull())
df = df.filter(col("customer_id").isNotNull())

# 3) Filling text fields with default values
df = df.fillna({
    "region": "unknown",
    "product_name": "unknown",
    "unit_price": 0.0
})

raw = trim(col("order_date").cast("string"))
df = df.withColumn(
    "order_date",
    coalesce(
        to_date(raw, "dd-MM-yyyy"),         # 31-07-2024
        to_date(raw, "dd/MM/yyyy"),         # 31/07/2024 
        to_date(raw, "dd-MM-yy"),            # 31-07-24
        to_date(raw, "yyyy-MM-dd")
    )
)
df = df.filter(col("order_date").isNotNull())
df = df.withColumn("order_year", year(col("order_date")))
df = df.withColumn("unit_price", spark_round(col("unit_price").cast("double"), 2).cast(DecimalType(12,2)))
df = df.withColumn("total_price",
                   spark_round(col("quantity") * col("unit_price"), 2).cast(DecimalType(14,2)))
#df = df.dropDuplicates()
#required = ["order_id", "order_date", "quantity", "unit_price"]
#df = df.dropna(subset=required)
# Final types
df = (df
    .withColumn("customer_id",  col("customer_id").cast(StringType()))
    .withColumn("product_name", col("product_name").cast(StringType()))
    .withColumn("region",       col("region").cast(StringType()))
    .withColumn("order_date",   col("order_date").cast(DateType()))
    .withColumn("order_year",   col("order_year").cast(IntegerType()))
)

df_out = df.select(
    "order_id", "customer_id", "product_name", "region",
    "quantity", "unit_price", "total_price", "order_date", "order_year"
).coalesce(16)
cleaned_dyf = DynamicFrame.fromDF(df_out, glueContext, "cleaned_dyf")

# 5) Write to Redshift (no TRUNCATE; just ensure table exists)
glueContext.write_dynamic_frame.from_jdbc_conf(
    frame=cleaned_dyf,
    catalog_connection="redshift_connection_team2",
    connection_options={
        "dbtable": "public.sales_data_team2",
        "database": "sales_data_redshift_team2",
        "extracopyoptions": "TRUNCATECOLUMNS BLANKSASNULL EMPTYASNULL COMPUPDATE OFF STATUPDATE OFF"
    },
    redshift_tmp_dir="s3://batch-etl-pipeline-team2/temp/"
)

#print(f"Initial row count: {row_count}")
#print(f"Final row count: {df.count()}")

#print(">>> columns from catalog:")
#print(df.columns)
#df.show(5, truncate=False)
#print(">>> row count right after read:", df.count())

job.commit()
