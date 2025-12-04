from app.main import app

if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)