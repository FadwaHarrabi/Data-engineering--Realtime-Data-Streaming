import logging
from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

# Configure logging for better debugging and status tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




def create_keyspace(session):
    """
    Creates a keyspace in Cassandra if it doesn't already exist.
    a keyspace is an important entity in Cassandra that dictates how data 
    is distributed and replicated, and it provides a logical 
    grouping for tables within the database.
    """


    """
    In Cassandra, the session.execute() method is used to run CQL (Cassandra Query Language)
    """
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)
    logging.info("Keyspace created successfully!")

def create_table(session):
    """
    Creates a table in Cassandra to store user data if it doesn't already exist.
    """
    session.execute("""
    CREATE TABLE IF NOT EXISTS spark_streams.created_users (
        id UUID PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        address TEXT,
        post_code TEXT,
        email TEXT,
        username TEXT,
        registered_date TEXT,
        phone TEXT,
        picture TEXT);
    """)
    logging.info("Table created successfully!")

def insert_data(session, **kwargs):
    """
    Inserts user data into the Cassandra table.
    """
    logging.info("Inserting data...")

    # Extracting values from the keyword arguments
    user_id = kwargs.get('id')
    first_name = kwargs.get('first_name')
    last_name = kwargs.get('last_name')
    gender = kwargs.get('gender')
    address = kwargs.get('address')
    postcode = kwargs.get('post_code')
    email = kwargs.get('email')
    username = kwargs.get('username')
    dob = kwargs.get('dob')
    registered_date = kwargs.get('registered_date')
    phone = kwargs.get('phone')
    picture = kwargs.get('picture')

    try:
        # Insert data into the table
        session.execute("""
            INSERT INTO spark_streams.created_users(id, first_name, last_name, gender, address, 
                post_code, email, username, dob, registered_date, phone, picture)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, gender, address,
              postcode, email, username, dob, registered_date, phone, picture))
        logging.info(f"Data inserted for {first_name} {last_name}")

    except Exception as e:
        logging.error(f"Could not insert data due to {e}")

def create_spark_connection():
    """
    Creates a Spark session configured with necessary packages for Kafka and Cassandra.
    """
    s_conn = None
    try:
        s_conn = SparkSession.builder \
            .appName('SparkDataStreaming') \
            .config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,"
                                           "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1") \
            .config('spark.cassandra.connection.host', 'localhost') \
            .getOrCreate()
        s_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully!")
    except Exception as e:
        logging.error(f"Couldn't create the Spark session due to exception: {e}")

    return s_conn

def connect_to_kafka(spark_conn):
    """
    Connects to a Kafka topic and reads data as a Spark DataFrame.
    """
    spark_df = None
    try:
        spark_df = spark_conn.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', 'localhost:9092') \
            .option('subscribe', 'users_created') \
            .option('startingOffsets', 'earliest') \
            .load()
        logging.info("Kafka DataFrame created successfully")
    except Exception as e:
        logging.warning(f"Kafka DataFrame could not be created because: {e}")

    return spark_df

def create_cassandra_connection():
    """
    Establishes a connection to the Cassandra cluster.
    """
    try:
        # Connect to Cassandra cluster
        cluster = Cluster(['localhost'])
        cas_session = cluster.connect()
        logging.info("Cassandra connection created successfully!")
        return cas_session
    except Exception as e:
        logging.error(f"Could not create Cassandra connection due to: {e}")
        return None

def create_selection_df_from_kafka(spark_df):
    """
    Extracts and parses Kafka data into a structured Spark DataFrame.
    """
    # Define the schema for the Kafka data
    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StringType(), False),
        StructField("post_code", StringType(), False),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False)
    ])

    # Parse Kafka messages and extract data
    sel = spark_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col('value'), schema).alias('data')).select("data.*")
    logging.info("Data selection DataFrame created successfully!")
    return sel

if __name__ == "__main__":
    # Create Spark connection
    spark_conn = create_spark_connection()

    if spark_conn is not None:
        # Connect to Kafka with Spark connection
        spark_df = connect_to_kafka(spark_conn)
        if spark_df is not None:
            selection_df = create_selection_df_from_kafka(spark_df)
            # Connect to Cassandra
            session = create_cassandra_connection()
            if session is not None:
                # Set up Cassandra keyspace and table
                create_keyspace(session)
                create_table(session)

                logging.info("Streaming is being started...")

                # Start streaming data to Cassandra
                streaming_query = (selection_df.writeStream
                                   .format("org.apache.spark.sql.cassandra")
                                   .option('checkpointLocation', '/tmp/checkpoint')
                                   .option('keyspace', 'spark_streams')
                                   .option('table', 'created_users')
                                   .start())

                # Await termination of the stream
                streaming_query.awaitTermination()
