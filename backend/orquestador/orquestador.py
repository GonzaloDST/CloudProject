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
    title="Orquestrador de Microservicios",
    version="1.0.0",
    description="Orquestrador que redirige peticiones a microservicios",
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
    """Health check del orquestrador"""
    return {
        "status": "healthy", 
        "service": "orquestrador",
        "microservices": list(MICROSERVICES.keys())
    }

# Rutas específicas para archivos estáticos de Swagger
@app.get("/api/{service}/static/{file_path:path}")
async def static_files_fastapi(service: str, file_path: str, request: Request):
    """Maneja archivos estáticos de FastAPI Swagger UI"""
    if service not in MICROSERVICES:
        raise HTTPException(404, f"Microservicio '{service}' no encontrado")
    
    target_url = f"{MICROSERVICES[service]}/static/{file_path}"
    logger.info(f"Archivo estático FastAPI: {request.url} → {target_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(target_url)
            
            clean_headers = {k: v for k, v in response.headers.items() 
                            if k.lower() not in ['content-length', 'transfer-encoding', 'connection', 'server']}
            
            # Determinar Content-Type correcto basado en la extensión
            content_type = 'application/octet-stream'
            if file_path.lower().endswith('.css'):
                content_type = 'text/css'
            elif file_path.lower().endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.lower().endswith('.png'):
                content_type = 'image/png'
            elif file_path.lower().endswith('.ico'):
                content_type = 'image/x-icon'
            elif file_path.lower().endswith('.svg'):
                content_type = 'image/svg+xml'
            elif file_path.lower().endswith(('.woff', '.woff2')):
                content_type = 'font/woff2' if file_path.lower().endswith('.woff2') else 'font/woff'
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=clean_headers,
                media_type=content_type
            )
    except Exception as e:
        logger.error(f"Error cargando archivo estático FastAPI: {str(e)}")
        raise HTTPException(404, f"Archivo estático no encontrado")

@app.get("/api/{service}/webjars/{file_path:path}")
async def static_files_springboot(service: str, file_path: str, request: Request):
    """Maneja archivos estáticos de Spring Boot Swagger UI"""
    if service not in MICROSERVICES:
        raise HTTPException(404, f"Microservicio '{service}' no encontrado")
    
    target_url = f"{MICROSERVICES[service]}/webjars/{file_path}"
    logger.info(f"Archivo estático Spring Boot: {request.url} → {target_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(target_url)
            
            clean_headers = {k: v for k, v in response.headers.items() 
                            if k.lower() not in ['content-length', 'transfer-encoding', 'connection', 'server']}
            
            # Determinar Content-Type correcto basado en la extensión
            content_type = 'application/octet-stream'
            if file_path.lower().endswith('.css'):
                content_type = 'text/css'
            elif file_path.lower().endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.lower().endswith('.png'):
                content_type = 'image/png'
            elif file_path.lower().endswith('.ico'):
                content_type = 'image/x-icon'
            elif file_path.lower().endswith('.svg'):
                content_type = 'image/svg+xml'
            elif file_path.lower().endswith(('.woff', '.woff2')):
                content_type = 'font/woff2' if file_path.lower().endswith('.woff2') else 'font/woff'
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=clean_headers,
                media_type=content_type
            )
    except Exception as e:
        logger.error(f"Error cargando archivo estático Spring Boot: {str(e)}")
        raise HTTPException(404, f"Archivo estático no encontrado")

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def redirect_request(service: str, path: str, request: Request):
    """Redirige peticiones a microservicios específicos"""
    
    if service not in MICROSERVICES:
        logger.warning(f"Microservicio '{service}' no encontrado")
        raise HTTPException(404, f"Microservicio '{service}' no encontrado")
    
    target_url = f"{MICROSERVICES[service]}/{path}"
    logger.info(f"Redirigiendo {request.method} {request.url} → {target_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=await request.body()
            )
            
            logger.info(f"Respuesta de {service}: {response.status_code}")
            
            # Limpiar headers problemáticos para todas las respuestas
            clean_headers = {k: v for k, v in response.headers.items() 
                            if k.lower() not in ['content-length', 'transfer-encoding', 'connection', 'server']}
            
            # Para archivos estáticos (CSS, JS, imágenes, fuentes) - SOLUCIÓN CRÍTICA
            if any(ext in path.lower() for ext in ['.css', '.js', '.png', '.ico', '.svg', '.woff', '.woff2', '.ttf']):
                # Determinar Content-Type correcto basado en la extensión
                content_type = 'application/octet-stream'
                if path.lower().endswith('.css'):
                    content_type = 'text/css'
                elif path.lower().endswith('.js'):
                    content_type = 'application/javascript'
                elif path.lower().endswith('.png'):
                    content_type = 'image/png'
                elif path.lower().endswith('.ico'):
                    content_type = 'image/x-icon'
                elif path.lower().endswith('.svg'):
                    content_type = 'image/svg+xml'
                elif path.lower().endswith(('.woff', '.woff2')):
                    content_type = 'font/woff2' if path.lower().endswith('.woff2') else 'font/woff'
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=clean_headers,
                    media_type=content_type
                )
            
            # Para archivos OpenAPI JSON
            if "openapi.json" in path or "api-docs" in path:
                return response.json()
            
            # Para endpoints de documentación (Swagger), devolver HTML
            if "docs" in path or "swagger" in path:
                # Modificar el HTML para que los archivos estáticos apunten al orquestrador
                html_content = response.text
                
                # Reemplazar rutas de archivos estáticos para que apunten al orquestrador
                if service == "orders":  # FastAPI
                    html_content = html_content.replace('/static/', f'/api/{service}/static/')
                elif service == "inventory":  # NestJS
                    html_content = html_content.replace('/docs/', f'/api/{service}/docs/')
                elif service == "menu":  # Spring Boot
                    html_content = html_content.replace('/webjars/', f'/api/{service}/webjars/')
                
                return HTMLResponse(
                    content=html_content,
                    status_code=response.status_code,
                    headers=clean_headers
                )
            
            # Para otros endpoints, intentar JSON primero
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