from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from config import Settings

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def check_camera_availability():
    import os
    import cv2
    from pymongo import MongoClient
    from typing import Dict, Any
    
    # MongoDB connection
    client = MongoClient(Settings().mongodb.host, Settings().mongodb.port)
    db = client[Settings().mongodb.db_name]
    collection = db['cameras']
    
    print(f"Connected to MongoDB at {Settings().mongodb.host}:{Settings().mongodb.port}")
    
    # Fetch all enabled cameras
    enabled_cameras = list(collection.find({'enabled': True}))
    print(f"Found {len(enabled_cameras)} enabled cameras to check")
    
    for camera in enabled_cameras:
        camera_id = camera['_id']
        rtsp_url = camera.get('url', '')
        camera_name = camera.get('name', 'Unknown')
        
        print(f"Checking camera: {camera_name} (ID: {camera_id})")
        print(f"  RTSP URL: {rtsp_url}")
        
        # Check RTSP availability
        is_available = check_rtsp_url(rtsp_url)
        
        print(f"  Available: {is_available}")
        
        # Update the database
        collection.update_one(
            {'_id': camera_id},
            {'$set': {'available': is_available}}
        )
        print(f"  Updated database for camera: {camera_name}")
    
    client.close()
    print("Camera availability check completed")


def check_rtsp_url(url: str, timeout: int = 10) -> bool:
    import cv2
    
    if not url:
        return False
    
    try:
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout * 1000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, timeout * 1000)
        
        if not cap.isOpened():
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        return ret and frame is not None
        
    except Exception as e:
        print(f"Error checking RTSP URL {url}: {e}")
        return False


# Define the DAG
with DAG(
    'camera_availability_checker',
    default_args=default_args,
    description='Periodically checks RTSP URL availability for enabled cameras',
    schedule_interval=timedelta(minutes=5),  # Run every 5 minutes
    start_date=datetime.now(),
    catchup=False,
    tags=['cameras', 'rtsp', 'availability'],
) as dag:
    
    check_availability_task = PythonOperator(
        task_id='check_camera_availability',
        python_callable=check_camera_availability,
    )
