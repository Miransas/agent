from app.config.settings import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.server.api:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
