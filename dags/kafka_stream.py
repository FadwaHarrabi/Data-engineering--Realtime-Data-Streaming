from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import json
default_args={
    'owner':'fadwa harrabi',
    'start_date':datetime.now(),

}

def get_data():
    
    res=requests.get("https://randomuser.me/api/")
    res=res.json()
    res=res['results'][0] 
    return res 

def format_data(res):
    data={}
    data['first_name']=res['name']['first']
    data['last_name']=res['name']['last']
    data['address'] = f"{res['location']['street']['number']} {res['location']['street']['name']}, " \
                  f"{res['location']['city']}, {res['location']['state']}, {res['location']['country']}"
    
    data['location']=res['location']['postcode']
    data['email']=res['email']
    data['username']=res['login']['username']
    data['dob']=res['dob']['date']
    data['registered_date']=res['registered']['date']
    data['phone']=res['phone']
    data['picture']=res['picture']['medium']

def stream_data():
    res=get_data()
    res=format_data(res)
    print(json.dumps(res,indent=3))


    
    

    
with DAG('user_automation',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:
        
    streaming_task=PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
            
    )



stream_data()