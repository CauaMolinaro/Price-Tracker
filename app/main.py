from fastapi import FastAPI
from app.routers import produtos, precos, alertas, auth

app = FastAPI(
    title="Price Tracker API",
    description="API para monitorar histórico de preços de produtos e disparar alertas.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(produtos.router)
app.include_router(precos.router)
app.include_router(alertas.router)


@app.get("/")
def raiz():
    return {"status": "ok", "mensagem": "Price Tracker API no ar. Veja /docs"}