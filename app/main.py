from contextlib import asynccontextmanager
from pathlib import Path
import sys
DB_DIR = Path(__file__).resolve().parent.parent / "db"
if str(DB_DIR) not in sys.path:
    sys.path.insert(0, str(DB_DIR))

import models
import database
import crud

sys.modules["db.models"] = models
sys.modules["db.database"] = database
sys.modules["db.crud"] = crud

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import create_db_and_tables
from app.routers import products, category


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialise poleatheck.sqlite et crée les tables au démarrage du serveur
    create_db_and_tables()
    yield #avant yield s'execute au démarrage et après yield à l'extinction
    
app = FastAPI(title="Pol-eat-heck API",description="API REST de gestion des menus hebdomadaires et de réservation de produits",lifespan=lifespan)

# Autorise les requêtes fetch() du front-end en développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(products.router)
app.include_router(category.router)

@app.get("/ping", tags=["Test"])
async def ping():
    return {
        "status": "ok",
        "message": "Serveur FastAPI opérationnel"
    }