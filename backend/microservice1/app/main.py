from fastapi import FastAPI
from app.routes import users, products, orders
from app.database import Database

app = FastAPI(
    title="Maki Orders API",
    description="Microservicio para gestión de pedidos de Maki",
    version="1.0.0"
)

# Incluir routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a Maki Orders API"}

@app.get("/health")
def health_check():
    try:
        db = Database()
        conn = db.get_connection()
        if conn.is_connected():
            return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}
    finally:
        if 'db' in locals():
            db.close_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)