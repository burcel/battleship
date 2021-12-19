import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from api import user, game, websocket
import api
from core.db import Base, engine
from core.settings import settings

# Create sqlalchemy tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.name)

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(game.router, prefix="/game", tags=["game"])
api_router.include_router(websocket.router)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Battleship</title>
    </head>
    <body>
        <h1>Examples</h1>
        <div style="padding-bottom: 10px;">
            {"type": "TOKEN", "token": ""}|
            token: <input type="text" id="token">
            <button onclick="populateMessage('token')">Populate</button>
        </div>
        <div style="padding-bottom: 10px;">
            {"type": "MESSAGE", "message": x}|
            message: <input type="text" id="message">
            <button onclick="populateMessage('message')">Populate</button>
        </div>
        <hr>
        <h1>WebSocket</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" style="width: 500px;"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
            function populateMessage(type) {
                if (type === 'token') {
                    document.getElementById("messageText").value = JSON.stringify({
                        "type": "TOKEN",
                        "token": document.getElementById('token').value
                    })
                } else if (type === 'message') {
                    document.getElementById("messageText").value = JSON.stringify({
                        "type": "MESSAGE",
                        "message": document.getElementById('message').value
                    })
                }
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.server_ip, port=settings.server_port)
