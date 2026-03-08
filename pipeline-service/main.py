from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models.customer import Customer
from services.ingestion import run_pipeline

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Data Pipeline API")

@app.post("/api/ingest")
def ingest_data():
    try:
        load_info = run_pipeline()
        
        return {
            "status": "success",
            "message": "Data ingested successfully",
            "info": str(load_info)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    customers = db.query(Customer).offset(skip).limit(limit).all()
    total = db.query(Customer).count()
    
    return {
        "data": customers,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
