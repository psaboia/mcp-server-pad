import os
import io
from PIL import Image
from fastapi import FastAPI, HTTPException, Query, Path, Depends, Request
from fastapi.responses import JSONResponse, FileResponse, Response
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, SmallInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL_LD", "mysql+pymysql://user:password@localhost/pad")

# returned image size
MAX_WIDTH = 50  # Adjust as needed
MAX_HEIGHT = 100  # Adjust as needed

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
    deleted = Column(Boolean, nullable=False, default=False)
    issue_id = Column(Integer, nullable=True)

class Project(Base):
    __tablename__ = "projects"  # Adjust this if your table name is different

    id = Column(Integer, primary_key=True, index=True)              # Primary key, auto-incremented; maps to "identifier"
    user_name = Column(String(64), nullable=False, index=True)      # Administrator name; maps to "performedBy" (User)
    project_name = Column(String(64), nullable=False, index=True)   # Project name (category); maps to "hasProjectName"
    annotation = Column(String(8), nullable=True)                   # Card annotation; maps to "hasAnnotation" (optional)
    test_name = Column(String(64), nullable=False)                  # Card layout/test type; maps to "hasTestType"
    sample_names = Column(JSON, nullable=True)                      # Variable list of drugs; stored as JSON; maps to "hasSample"
    neutral_filler = Column(String(64), nullable=True)              # Filler for less than 100% concentration; maps to "hasNeutralFilter"
    qpc20 = Column(SmallInteger, nullable=False, default=0)         # 20% quantity flag; maps to a concentration value (20%); stored as tinyint (0/1)
    qpc50 = Column(SmallInteger, nullable=False, default=0)         # 50% quantity flag; maps to a concentration value (50%); stored as tinyint (0/1)
    qpc80 = Column(SmallInteger, nullable=False, default=0)         # 80% quantity flag; maps to a concentration value (80%); stored as tinyint (0/1)
    qpc100 = Column(SmallInteger, nullable=False, default=1)        # 100% quantity flag; maps to a concentration value (100%); stored as tinyint (0/1)
    notes = Column(Text, nullable=True)                             # Notes on project; maps to "hasNotes" (optional)

def project_to_jsonld(proj: Project) -> dict:
    """
    Convert a Project instance into a JSON‑LD document.
    Database field names are preserved, while the @context maps them to ontology properties.
    """
    # Build the concentrations array based on the qpc columns.
    concentrations = []
    if proj.qpc20:
        concentrations.append(20)
    if proj.qpc50:
        concentrations.append(50)
    if proj.qpc80:
        concentrations.append(80)
    if proj.qpc100:
        concentrations.append(100)
    
    # Process sample_names JSON column: if it's a dict with a "sample_names" key, extract its list.
    sample_names = []
    if proj.sample_names:
        # Check if sample_names is a dictionary with key "sample_names"
        if isinstance(proj.sample_names, dict):
            names_list = proj.sample_names.get("sample_names", [])
        else:
            names_list = proj.sample_names  # Otherwise assume it's a list
        for s in names_list:
            sample_names.append({
                "@type": "Sample",
                "drug": s
            })

    return {
        "@context": {
            "@vocab": "https://pad.crc.nd.edu/ontology#",
            "id": "identifier",
            "project_name": "hasProjectName",       # Maps project_name
            "annotation": "hasAnnotation",          # Maps annotation
            "test_name": "hasLayout",             # Maps test_name
            "sample_names": "hasSample",            # Maps sample_names
            "neutral_filler": "hasNeutralFilter",   # Maps neutral_filler
            "concentrations": "hasConcentrations",  # Derived from qpc20, qpc50, qpc80, qpc100
            "notes": "hasProjectNotes",             # Maps notes
            "user_name": "performedBy",             # Maps user_name
            "description": "rdfs:comment"
        },
        "@type": "Project",
        "id": proj.id,
        "project_name": proj.project_name,
        "annotation": proj.annotation,
        "test_name": { "@type": "Layout", "name": proj.test_name },
        "sample_names": sample_names,
        "neutral_filler": proj.neutral_filler,
        "concentrations": concentrations,
        "notes": proj.notes,
        "user_name": {
            "@type": "User",
            "userName": proj.user_name
        },
        "description": (
            "This project groups PAD cards for drug testing. It details the samples (drugs) to be analyzed, "
            "the test method to be applied, and the expected concentration levels (" + ", ".join(str(c) for c in concentrations) + "). "
            "It also includes project annotations and operator information."
        )
    }

card_context = {
            "@vocab": "https://pad.crc.nd.edu/ontology#",
            "id": "identifier",
            "date_of_creation": "hasCreationDate",             # Maps date_of_creation
            "processed_file_location": "hasProcessedImage",    # Maps processed_file_location
            "raw_file_location": "hasRawImage",                # Maps raw_file_location
            "camera_type_1": "hasCameraUsed",                  # Maps camera_type_1
            "notes": "hasNotes",                               # Maps notes
            "sample_id": "hasSampleId",                        # Maps sample_id
            "quantity": "hasQuantity",                         # Maps quantity
            "sample_name": "hasSample",                        # Maps sample_name
            "test_name": "hasLayout",                          # Maps test_name
            "user_name": "performedBy",                        # Maps user_name
            "project": "belongsToProject",                     # Maps project_id (or lookup)
            "producesColorBarcode": "producesColorBarcode",    # Static/dummy mapping
            "barcodeBoundingBox": "hasBarcodeBoundingBox",     # Static/dummy mapping
            "description": "rdfs:comment"
}

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

# Middleware to log full client connection details
@app.middleware("http")
async def log_client_connection(request: Request, call_next):
    client = request.client  # Contains host and port info
    headers = dict(request.headers)
    logger.info(f"Incoming request from {client.host}:{client.port}")
    logger.info(f"Request headers: {headers}")
    response = await call_next(request)
    return response

# # Middleware to handle proxy headers
# app.add_middleware(ProxyHeadersMiddleware)

# # Allow only requests from trusted hosts
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Change "*" to allowed hosts/IPs

# dereference project id
def get_project_name_by_id(db: Session, project_id: int) -> str:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.project_name

@app.get("/api-ld/v3/cards/by-sample/{sample_id}", tags=["Cards"], responses={
    200: {
        "description": "Successful retrieval of a PAD card.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": [
                        {
                        "@context": {
                            "@vocab": "https://pad.crc.nd.edu/ontology#",
                            "id": "identifier",
                            "date_of_creation": "hasCreationDate",
                            "processed_file_location": "hasProcessedImage",
                            "raw_file_location": "hasRawImage",
                            "camera_type_1": "hasCameraUsed",
                            "notes": "hasNotes",
                            "sample_id": "hasSampleId",
                            "quantity": "hasQuantity",
                            "sample_name": "hasSample",
                            "test_name": "hasLayout",
                            "user_name": "performedBy",
                            "project": "belongsToProject",
                            "producesColorBarcode": "producesColorBarcode",
                            "barcodeBoundingBox": "hasBarcodeBoundingBox",
                            "description": "rdfs:comment"
                        },
                        "@type": "AnalyticalCard",
                        "id": 18429,
                        "sample_name": {
                            "@type": "Sample",
                            "name": "tetracycline"
                        },
                        "test_name": {
                            "@type": "Layout",
                            "name": "12LanePADKenya2015"
                        },
                        "user_name": {
                            "@type": "User",
                            "name": "api-OUDPXFH17PEGKUW3FM4Z"
                        },
                        "project": {
                            "@type": "Project",
                            "name": "FHI2020",
                            "id": 11
                        },
                        "notes": "batch=n/a, quantity=100%, p s",
                        "processed_file_location": "/var/www/html/images/padimages/processed/10000/18429_processed.png",
                        "date_of_creation": "2020-06-03T16:05:05",
                        "raw_file_location": "/var/www/html/images/padimages/raw/10000/18429_raw.png",
                        "camera_type_1": "Google Pixel 3a",
                        "sample_id": 52937,
                        "quantity": 100,
                        "issue_id": 2,
                        "description": "This PAD Analytical Card with sample_id 52937 is a 58mm x 104mm chromatography card with 12 lanes. A swipe line separates the card, and reagents pre-applied below the swipe line react with the drug sample to generate a unique Color Barcode. The layout defines key regions including the barcode bounding box used for image rectification and analysis. The card is associated with a project and operator, and its metadata includes details on sample, test, and processing."
                        }
                    ],
                    "error": "",
                    "summary": "Retrieved 1 PAD cards for sample 52937 in semantic JSON‑LD format."
                }
            }
        }
    }
})
def get_cards_by_sample(
    sample_id: int = Path(..., description="The sample identifier associated with the PAD cards."),
    db: Session = Depends(get_db)
):
    """
    Retrieve PAD cards by sample_id.
    Returns all cards (formatted as JSON‑LD) whose 'sample_id' field matches the provided value.
    """
    cards = db.query(Card).filter(Card.sample_id == sample_id, Card.deleted == False).all()
    #cards = db.query(Card).filter(Card.sample_id == sample_id).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No cards found for the given sample_id")

    json_ld_cards = []
    for card in cards:
        # Dereference project_id to get the project name
        project_name = get_project_name_by_id(db, card.project_id)

        json_ld_cards.append({
            "@context": card_context,
            "@type": "AnalyticalCard",
            "id": card.id,
            "sample_name": { "@type": "Sample", "name": card.sample_name },
            "test_name": { "@type": "Layout", "name": card.test_name },
            "user_name": { "@type": "User", "name": card.user_name },
            "project": { "@type": "Project", "name": project_name, "id": card.project_id },
            "notes": card.notes,
            "processed_file_location": card.processed_file_location,
            "date_of_creation": card.date_of_creation.isoformat() if card.date_of_creation else None,
            "raw_file_location": card.raw_file_location,
            "camera_type_1": card.camera_type_1,
            "sample_id": card.sample_id,
            "quantity": card.quantity,
            "issue_id": card.issue_id,
            "description": (
                f"This PAD Analytical Card with sample_id {card.sample_id} is a 58mm x 104mm chromatography card with 12 lanes. A swipe line separates the card, "
                "and reagents pre-applied below the swipe line react with the drug sample to generate a unique Color Barcode. "
                "The layout defines key regions including the barcode bounding box used for image rectification and analysis. "
                "The card is associated with a project and operator, and its metadata includes details on sample, test, and processing."
            )
        })

    return JSONResponse(content={
        "success": True,
        "data": json_ld_cards,
        "error": "",
        "summary": f"Retrieved {len(json_ld_cards)} PAD cards for sample {sample_id} in semantic JSON‑LD format."
    })

@app.get("/api-ld/v3/projects", tags=["Projects"])
def get_all_projects(db: Session = Depends(get_db)):
    """
    Retrieve all PAD projects.
    Returns projects as JSON-LD documents using the database column names mapped via the context.
    """
    projects = db.query(Project).all()
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    json_ld_projects = [project_to_jsonld(proj) for proj in projects]
    return JSONResponse(content={
        "success": True,
        "data": json_ld_projects,
        "error": "",
        "summary": f"Retrieved {len(json_ld_projects)} PAD projects in semantic JSON‑LD format."
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
    #return FileResponse(card.processed_file_location, media_type="image/png", filename=os.path.basename(card.processed_file_location))

    # Open and resize the image
    with Image.open(card.processed_file_location) as img:
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT))  # Resizes while maintaining aspect ratio

        # Save the resized image to an in-memory file
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")  # Save as PNG (or JPEG for smaller size)
        img_byte_arr.seek(0)

    # Return the resized image as a response
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api-ld:app", host="0.0.0.0", port=8008, reload=True)

