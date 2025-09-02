import uvicorn
from server import app_api

if __name__ == "__main__":
    print("Starting WaterWise Bot Backend...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "server:app_api",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
