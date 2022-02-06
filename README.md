# battleship
Python implementation of [Battleship](https://en.wikipedia.org/wiki/Battleship_(game) "Battleship Wikipedia Page"), a strategy type guessing game for two players played on ruled grids on which each player's fleet of ships are marked.

# Setup

## Requirements

- Python 3.8
- FastAPI 0.68.1
- SQLAlchemy 1.4.27

## Installation

In order to setup Python virtual environment:
```
# Set up a new virtual environment.
python3 -m venv myenv
# Activate the virtual environment
source "myenv/bin/activate"
```

Install all dependencies:
```
pip install --upgrade -r requirements.txt
```

To deactivate the virtual environment:
```
# Deactivate virtual environment
deactivate
# Delete virtual environment
rm -rf myenv
```

## Running

Project is run by command, which in turn runs uvicorn application:

```
python3 main.py
```
You need to see the log if everything goes smoothly:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

# Features

- Pydantic

Every incoming request and outgoing response go through directly pydantic objects (including websocket ones). 

- JWT Token System

When a user logs in, a JWT token is created for that user with the following metadata:
```
{
  "id": user.id,
  "username": user.username,
  "exp": datetime.utcnow() + timedelta(minutes=settings.token_expire_min),
}
```


# To-Do:
- ~~Type: Ready~~
  - Check whether server sends the boards after each user sends ready
- Type: Turn
  - Check if server sends turn object to both sides
- Game ending
  - Check board after hit
- Send game end result
  - If board is finished after hit, send game end result to users
- Release game related objects after game is over
  - websockets, boards in active games
- AI
  - Simplistic AI for playing the game
