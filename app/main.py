from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pol-eat-heck API",description="API REST de gestion des menus hebdomadaires et de réservation de produits")


# Autorise les requêtes fetch() du front-end en développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", tags=["Test"])
async def ping():
    return {
        "status": "ok",
        "message": "Serveur FastAPI opérationnel"
    }