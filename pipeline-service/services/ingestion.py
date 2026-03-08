import requests
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from database import SessionLocal
from models.customer import Customer

MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000/api/customers")

def fetch_all_customers():
    page = 1
    limit = 10
    all_customers = []
    
    while True:
        try:
            response = requests.get(f"{MOCK_SERVER_URL}?page={page}&limit={limit}")
            response.raise_for_status()
            data = response.json()
            
            customers = data.get("data", [])
            if not customers:
                break
                
            all_customers.extend(customers)
            
            total = data.get("total", 0)
            if page * limit >= total:
                break
                
            page += 1
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
            
    return all_customers

def run_pipeline():
    customers_data = fetch_all_customers()
    processed = 0
    
    db = SessionLocal()
    try:
        for c_data in customers_data:
            # Parse dates
            dob = None
            if c_data.get("date_of_birth"):
                dob = datetime.strptime(c_data["date_of_birth"], "%Y-%m-%d").date()
                
            created_at = None
            if c_data.get("created_at"):
                created_at = datetime.strptime(c_data["created_at"].replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")

            values = {
                "customer_id": c_data["customer_id"],
                "first_name": c_data["first_name"],
                "last_name": c_data["last_name"],
                "email": c_data["email"],
                "phone": c_data.get("phone"),
                "address": c_data.get("address"),
                "date_of_birth": dob,
                "account_balance": c_data.get("account_balance"),
                "created_at": created_at
            }
            
            stmt = insert(Customer).values(**values)
            
            # Upsert logic
            update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}
            
            if update_dict:
                stmt = stmt.on_conflict_do_update(
                    index_elements=['customer_id'],
                    set_=update_dict
                )
            else:
                stmt = stmt.on_conflict_do_nothing()
                
            db.execute(stmt)
            processed += 1
            
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
    class LoadInfoMock:
        def __str__(self):
            return f"Inserted/Updated {processed} records"
            
    return LoadInfoMock()
