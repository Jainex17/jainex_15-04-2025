import csv
from app.models import StoreTimeZone, StoreStatus, BusinessHours
from app.db import db

def add_timezone_data():
    try:
        with open('data/timezone.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                existing = db.query(StoreTimeZone).filter(StoreTimeZone.store_id == row['store_id']).first()
                if existing:
                    continue
                    
                timezone_value = StoreTimeZone(
                    store_id= row['store_id'],
                    timezone_str= row['timezone_str']
                )        
                db.add(timezone_value)    
                db.commit()
    
        print("Timezone data added successfully.")
    except Exception as e:
        print(f"❌ Error adding timezone data: {e}")
        db.rollback()

def add_status_data():
    try:
        with open('data/store_status.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                existing = db.query(StoreStatus).filter(
                    StoreStatus.store_id == row["store_id"],
                    StoreStatus.timestamp_utc == row["timestamp_utc"]
                ).first()
                if existing:
                    continue

                store_status_value = StoreStatus(
                    store_id = row["store_id"],
                    status = row["status"],
                    timestamp_utc = row["timestamp_utc"]
                )        
                db.add(store_status_value)
                db.commit()
        
        print("Status data added successfully.")
    except Exception as e:
        print(f"Error adding status data: {e}")
        db.rollback()

def add_business_hour_data():
    try:
        with open('data/menu_hour.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                existing = db.query(BusinessHours).filter(
                    BusinessHours.store_id == row['store_id'],
                    BusinessHours.day_of_week == int(row['dayOfWeek'])
                ).first()
                if existing:
                    continue

                business_hour_value = BusinessHours(
                    store_id = row['store_id'],
                    day_of_week = int(row['dayOfWeek']),
                    start_time_local = row['start_time_local'],
                    end_time_local = row['end_time_local']
                )
                db.add(business_hour_value)
                db.commit()
        
        print("Business hour data added successfully.")
    except Exception as e:
        print(f"Error adding business hour data: {e}")
        db.rollback()
        return


add_timezone_data()
add_status_data()
add_business_hour_data()

print("done 👍")