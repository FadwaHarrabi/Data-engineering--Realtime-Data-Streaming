# Import necessary modules
from datetime import datetime  # To handle date and time
from airflow import DAG  # To define workflows as Directed Acyclic Graphs (DAGs)
from airflow.operators.python import PythonOperator  # To execute Python functions as tasks in the DAG
import requests  # To make HTTP requests to APIs
import json  # To work with JSON data
import time  # To handle delays and timestamps
import uuid  # To generate unique identifiers

# Default arguments for the DAG
default_args = {
    'owner': 'fadwa harrabi',  # Specifies the owner of the DAG
    'start_date': datetime(2025, 1, 1),  # The date from which the DAG will start running
}

# Function to fetch data from the random user API
def get_data():
    # Make a GET request to the API
    res = requests.get("https://randomuser.me/api/")
    # Parse the JSON response
    res = res.json()
    # Extract the first user's details
    res = res['results'][0]
    return res

# Function to format the data into a structured dictionary
def format_data(res):
    data = {}  # Initialize an empty dictionary

    # Extract location details
    location = res['location']
    # Populate the dictionary with relevant fields
    data['id'] = uuid.uuid4()  # Generate a unique ID
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, " \
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']  # Date of birth
    data['registered_date'] = res['registered']['date']  # Registration date
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']  # Profile picture URL

    return data  # Return the structured data

# Function to stream data to a Kafka topic
def stream_data():
    import json  # Import JSON for data serialization
    from kafka import KafkaProducer  # To send data to Kafka
    import time  # To manage timing
    import logging  # For error logging

    # Create a Kafka producer instance
    # Adjust the bootstrap server depending on your Kafka setup
    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    curr_time = time.time()  # Record the current time

    # Stream data for one minute
    while True:
        if time.time() > curr_time + 60:  # Stop after 1 minute
            break
        try:
            res = get_data()  # Fetch data from the API
            res = format_data(res)  # Format the data

            # Send the data to the 'users_created' Kafka topic
            producer.send('users_created', json.dumps(res).encode('utf-8'))
        except Exception as e:
            # Log any errors encountered
            logging.error(f'An error occurred: {e}')
            continue

# Define the DAG
with DAG(
    'user_automation',  # Unique name for the DAG
    default_args=default_args,  # Use the default arguments defined earlier
    schedule_interval='@daily',  # Run the DAG once a day
    catchup=False  # Prevent running for past dates
) as dag:
    # Define a task to stream data
    streaming_task = PythonOperator(
        task_id='stream_data_from_api',  # Unique task ID
        python_callable=stream_data  # Function to execute
    )
