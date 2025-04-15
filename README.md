## Problem statement

Loop monitors several restaurants in the US and needs to monitor if the store is online or not. All restaurants are supposed to be online during their business hours. Due to some unknown reasons, a store might go inactive for a few hours. Restaurant owners want to get a report of the how often this happened in the past.

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Celery x Redis

## API ENDPOINTS
#### 1. /trigger_report: 
This endpoint is used to trigger the report generation process on background celery job worker and store on Reddis db.

#### 2. /get_report
This endpoint is used to get the report from the Reddis database. It takes a report_id as a query parameter and returns the report data in JSON format.
```json
{
    "report_id": "string",
}
```


## TO RUN LOCAL

#### 1. Clone the repository
```
git clone https://github.com/Jainex17/jainex_15-04-2025.git
cd jainex_15/04/2025
```

#### 2. Environment setup
```
python -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies
```
pip install -r requirements.txt
```

#### 4. copy .env.example to .env and fill in the values
```
cp .env.example .env
```
#### 5. Run scripts to create the tables and insert data
```
python -m app.scripts.db_init.py
python -m app.scripts.data_insert
```
#### 6. Run the app
```
uvicorn app.main:app
```

#### 7. Run background worker
```
celery -A app.api.celery_worker.celery_app worker --pool=solo
```


![image](https://github.com/user-attachments/assets/a3bc1fc7-2424-45df-bb56-cf01bc2046d7)

![image](https://github.com/user-attachments/assets/f1f83e19-a076-4b1d-adee-4e15de4b8fb7)
