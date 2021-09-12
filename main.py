from typing import Optional

import uvicorn
from fastapi import APIRouter, Cookie, Depends, FastAPI, Query, WebSocket, status
from fastapi.responses import HTMLResponse

from api import user, websocket
from core.settings import settings

app = FastAPI(title=settings.PROJECT_NAME)

api_router = APIRouter()
api_router.include_router(user.router, tags=["login"])
api_router.include_router(websocket.router)
app.include_router(api_router)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
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
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVER_IP, port=settings.SERVER_PORT)
