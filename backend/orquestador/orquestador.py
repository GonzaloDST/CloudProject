from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import logging
import json

#Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Orquestador de Microservicios",
    version="1.0.0",
    description="Orquestador que redirige peticiones a microservicios",
    redirect_slashes=False
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios exactos
    allow_credentials=False,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Todos los headers
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
            
            # Manejar redirects (302, 301)
            if response.status_code in [301, 302]:
                location = response.headers.get('location', '')
                if location:
                    # Reemplazar URL interna con URL del orquestrador
                    if service in location:
                        new_location = location.replace(f"http://{service}_service", f"https://jiql4i2xy4.execute-api.us-east-1.amazonaws.com/prod/api/{service}")
                        return RedirectResponse(url=new_location, status_code=response.status_code)
                return RedirectResponse(url=location, status_code=response.status_code)
            
            # Para endpoints de documentación (Swagger), devolver HTML con Content-Type correcto
            if "docs" in path or "swagger" in path:
                # Limpiar headers problemáticos
                clean_headers = {k: v for k, v in response.headers.items() 
                                if k.lower() not in ['content-length', 'transfer-encoding', 'connection']}
                return HTMLResponse(
                    content=response.text,
                    status_code=response.status_code,
                    headers=clean_headers
                )
            
            # Para archivos estáticos de Swagger (CSS, JS, imágenes)
            if any(ext in path for ext in ['.css', '.js', '.png', '.ico', '.svg']):
                # Limpiar headers problemáticos para archivos estáticos
                clean_headers = {k: v for k, v in response.headers.items() 
                                if k.lower() not in ['content-length', 'transfer-encoding', 'connection']}
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=clean_headers,
                    media_type=response.headers.get('content-type', 'application/octet-stream')
                )
            
            # Para archivos OpenAPI, devolver JSON
            if "openapi.json" in path or "api-docs" in path:
                return response.json()
            
            # Para otros endpoints, intentar JSON
            try:
                return response.json()
            except:
                # Si no es JSON válido, devolver texto
                return response.text
            
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
