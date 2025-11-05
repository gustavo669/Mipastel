from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import normales, clientes, reportes, admin

app = FastAPI(title="Mi Pastel — Sistema de pedidos")

app.include_router(normales.router)
app.include_router(clientes.router)
app.include_router(reportes.router)
app.include_router(admin.router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    sabores_normales = [
        "Fresas", "Frutas", "Chocolate", "Selva negra", "Oreo", "Chocofresa",
        "Tres Leches", "Tres leches con Arándanos", "Fiesta", "Ambiente", "Zanahoria"
    ]
    sabores_clientes = sabores_normales + ["Boda", "Quince Años"]
    tamanos = [
        "Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"
    ]
    sucursales = [
        "Jutiapa 1","Jutiapa 2","Jutiapa 3","Progreso","Quesada","Acatempa",
        "Yupiltepeque","Atescatempa","Adelanto","Jeréz","Comapa","Cariña"
    ]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sabores_normales": sabores_normales,
        "sabores_clientes": sabores_clientes,
        "tamanos": tamanos,
        "sucursales": sucursales
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
