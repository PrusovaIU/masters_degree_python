from auth_service.app.app import App
from auth_service.app.core.config import settings

app = App(settings).app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
