from fastapi import FastAPI, HTTPException, Request
import httpx
import logging

#Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Orquestador de Microservicios",
    version="1.0.0",
    description="Orquestador que redirige peticiones a microservicios",
    redirect_slashes=False
)

#Microservicios config
MICROSERVICES = {
    "orders":    "http://maki_api:8000",
    "inventory": "http://inventory-service:4000",
    "menu":      "http://menu_service:8080"
}

@app.get("/")
async def health_check():
    """Health check del orquestador"""
    return {
        "status": "healthy", 
        "service": "orquestador",
        "microservices": list(MICROSERVICES.keys())
    }

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def redirect_request(service: str, path: str, request: Request):
    """Redirige peticiones a microservicios específicos"""
    
    if service not in MICROSERVICES:
        logger.warning(f"Microservicio '{service}' no encontrado")
        raise HTTPException(404, f"Microservicio '{service}' no encontrado")
    
    target_url = f"{MICROSERVICES[service]}/{path}"
    logger.info(f"Redirigiendo {request.method} {request.url} → {target_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=await request.body()
            )
            
            logger.info(f"Respuesta de {service}: {response.status_code}")
            return response.json()
            
    except httpx.TimeoutException:
        logger.error(f"Timeout al conectar con {service}")
        raise HTTPException(504, f"Timeout al conectar con {service}")
    except httpx.ConnectError:
        logger.error(f"Microservicio {service} no disponible")
        raise HTTPException(503, f"Microservicio {service} no disponible")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(500, f"Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
