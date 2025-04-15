from celery import Celery
from dotenv import load_dotenv
import os
import pandas as pd
import pytz

from datetime import timedelta
from app.db import db
from app.models import StoreStatus, BusinessHours, StoreTimeZone

load_dotenv()
celery_app = Celery('tasks')

celery_app.conf.update(
    broker_url=os.getenv("BROKER_URL"),
    result_backend=os.getenv("RESULT_BACKEND"),
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

@celery_app.task
def generate_report():
    try:
        report_data = calculate_report()
        if not report_data:
            raise Exception("No data available for report generation")
        
        print("done")
        return report_data

    except Exception as e:
        print(f"Error generating report: {e}")
        return {
            "report": {
                "status": "failed",
                "error": str(e)
            }
        }    

def calculate_report():

    store_status_df, business_hours_df, store_timezone_df = get_data_from_db()

    store_status_df['timestamp_utc'] = pd.to_datetime(store_status_df['timestamp_utc'], utc=True)
    current_time = store_status_df['timestamp_utc'].max()
    
    print(f"Current Time: {current_time}")

    one_hour_ago = current_time - timedelta(hours=1)
    one_day_ago = current_time - timedelta(days=1)
    one_week_ago = current_time - timedelta(weeks=1)

    unique_store_ids = store_status_df['store_id'].unique()
    report_data = []

    for store_id in unique_store_ids:
        timezone_info = store_timezone_df[store_timezone_df['store_id'] == store_id]['timezone_str']
        timezone_str = 'America/Chicago'

        if not timezone_info.empty:
            timezone_str = timezone_info.iloc[0]

            try:
                pytz.timezone(timezone_str)
            except pytz.exceptions.UnknownTimeZoneError:
                print(f"Invalid timezone for store {store_id}: {timezone_str}, using default")
                timezone_str = 'America/Chicago'

        store_hours = business_hours_df[business_hours_df['store_id'] == store_id]
        is_24_7 = store_hours.empty

        status_data = store_status_df[store_status_df['store_id'] == store_id].copy()

        hour_uptime, hour_downtime = calculate_metrics(status_data, store_hours, is_24_7, one_hour_ago, current_time, timezone_str, 60)
        day_uptime, day_downtime = calculate_metrics(status_data, store_hours, is_24_7, one_day_ago, current_time, timezone_str, 24)
        week_uptime, week_downtime = calculate_metrics(status_data, store_hours, is_24_7, one_week_ago, current_time, timezone_str, 168)

        report_data.append({
            "store_id": store_id,
            "hour_uptime": hour_uptime,
            "hour_downtime": hour_downtime,
            "day_uptime": day_uptime,
            "day_downtime": day_downtime,
            "week_uptime": week_uptime,
            "week_downtime": week_downtime
        })
    
    return report_data

def get_data_from_db():
    StoreStatusData = db.query(StoreStatus).all()
    BusinessHoursData = db.query(BusinessHours).all()
    StoreTimeZoneData = db.query(StoreTimeZone).all()

    store_status_df = pd.DataFrame([{
        'store_id': status.store_id,
        'status': status.status,
        'timestamp_utc': status.timestamp_utc
    } for status in StoreStatusData])
    
    business_hours_df = pd.DataFrame([{
        'store_id': hours.store_id,
        'day_of_week': hours.day_of_week,
        'start_time_local': hours.start_time_local,
        'end_time_local': hours.end_time_local
    } for hours in BusinessHoursData])

    store_timezone_df = pd.DataFrame([{
        'store_id': timezone.store_id,
        'timezone_str': timezone.timezone_str
    } for timezone in StoreTimeZoneData])

    return store_status_df, business_hours_df, store_timezone_df

def calculate_metrics(status_data, store_hours, is_24_7, how_long, current_time, timezone_str, units):

    one_hour_status_data = status_data[(status_data['timestamp_utc'] >= how_long) & 
                              (status_data['timestamp_utc'] <= current_time)].copy()

    if one_hour_status_data.empty:
        return 0, 0
    
    local_tz = pytz.timezone(timezone_str)

    one_hour_status_data['local_time'] = one_hour_status_data['timestamp_utc'].dt.tz_convert(local_tz)
    one_hour_status_data['day_of_week'] = one_hour_status_data['local_time'].dt.dayofweek
    
    one_hour_status_data = one_hour_status_data.sort_values(by='local_time')  

    if is_24_7:
        business_data = one_hour_status_data
    else:
        business_data = []
        for idx, row in one_hour_status_data.iterrows():
            day_of_week = row['day_of_week']
            time_of_day = row['local_time'].time()
            if is_in_business_hour(day_of_week, time_of_day, store_hours):
                business_data.append(row)
    
    business_data = pd.DataFrame(business_data)
    if business_data.empty:
        return 0, 0
    
    total_observations = len(business_data)
    active_observations = len(business_data[business_data['status'] == 'active'])

    uptime_ratio = active_observations / total_observations if total_observations > 0 else 0
    downtime_ratio = 1 - uptime_ratio
    
    uptime = round(uptime_ratio * units, 1)
    downtime = round(downtime_ratio * units, 1)

    hour_uptime = uptime
    hour_downtime = downtime
    return hour_uptime, hour_downtime


def is_in_business_hour(day_of_week, time_of_day, store_hours):
    day_hours = store_hours[store_hours['day_of_week'].isin([day_of_week])]

    if day_hours.empty:
        return False

    for idx, row in day_hours.iterrows():

        start_time = row['start_time_local']
        end_time = row['end_time_local']
        

        if start_time <= time_of_day <= end_time:
            return True

    return False