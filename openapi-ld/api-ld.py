import os
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL_LD", "mysql+pymysql://user:password@localhost/pad")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Card model based on your MariaDB schema.
class Card(Base):
    __tablename__ = "card"
    id = Column(Integer, primary_key=True, index=True)
    sample_name = Column(String(64), nullable=False, index=True)
    test_name = Column(String(64), nullable=False, index=True)
    user_name = Column(String(64), nullable=False, index=True)
    date_of_creation = Column(DateTime, nullable=False, index=True)
    raw_file_location = Column(Text, nullable=False)
    processed_file_location = Column(Text, nullable=True)
    processing_date = Column(DateTime, nullable=True, index=True)
    camera_type_1 = Column(String(64), nullable=False, index=True)
    notes = Column(Text, nullable=False)
    sample_id = Column(Integer, nullable=False, default=0)
    quantity = Column(SmallInteger, nullable=False, default=100)
    project_id = Column(Integer, nullable=False, default=0)
    #deleted = Column(Boolean, nullable=False, default=False)
    #issue_id = Column(Integer, nullable=True)

# Dependency to get a database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create FastAPI instance.
app = FastAPI(
    title="PAD LLM-Friendly API",
    version="2.0.0",
    openapi_url="/api-ld/v3/openapi.json",
    description=(
        "This API provides access to Paper Analytical Devices (PAD) data in a semantically rich JSON‑LD format. "
        "Interactive API documentation is available at /docs (Swagger UI) and /redoc (ReDoc)."
    )
)

# Middleware to handle proxy headers
app.add_middleware(ProxyHeadersMiddleware)

# Allow only requests from trusted hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Change "*" to allowed hosts/IPs

@app.get("/api-ld/v3/cards/by-sample/{sample_id}", tags=["Cards"])
def get_cards_by_sample(
    sample_id: int = Path(..., description="The sample identifier associated with the PAD cards."),
    db: Session = Depends(get_db)
):
    """
    Retrieve PAD cards by sample_id.
    Returns all cards (formatted as JSON‑LD) whose 'sample_id' field matches the provided value.
    """
    #cards = db.query(Card).filter(Card.sample_id == sample_id, Card.deleted == False).all()
    cards = db.query(Card).filter(Card.sample_id == sample_id).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No cards found for the given sample_id")

    json_ld_cards = []
    for card in cards:
        json_ld_cards.append({
            "@context": "https://pad.crc.nd.edu/ontology#",
            "@type": "AnalyticalCard",
            "id": card.id,
            "sample": { "@type": "Sample", "name": card.sample_name },
            "test": { "@type": "TestType", "name": card.test_name },
            "notes": card.notes,
            "image_path": card.processed_file_location,
            "description": f"PAD card with sample_id {card.sample_id}."
        })

    return JSONResponse(content={
        "success": True,
        "data": json_ld_cards,
        "error": "",
        "summary": f"Retrieved {len(json_ld_cards)} PAD cards for sample {sample_id} in semantic JSON‑LD format."
    })

@app.get("/api-ld/v3/cards/{id}/download-image", tags=["Cards"])
def download_processed_card_image(
    id: int = Path(..., description="The unique identifier of the PAD card."),
    db: Session = Depends(get_db)
):
    """
    Download the processed card image for a given card ID.
    Returns the image file in PNG format.
    """
    #card = db.query(Card).filter(Card.id == id, Card.deleted == False).first()
    card = db.query(Card).filter(Card.id == id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    if not card.processed_file_location or not os.path.exists(card.processed_file_location):
        raise HTTPException(status_code=404, detail="Processed image not found")
    
    logger.info(f"Serving image from: {card.processed_file_location}")
    return FileResponse(card.processed_file_location, media_type="image/png", filename=os.path.basename(card.processed_file_location))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)

