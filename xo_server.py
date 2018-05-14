# xo-online game server
# wroted by: Omar Othman
# 2018.12.05 - 03:47 PM




from modules.service.service import WebsocketServer
from modules.json import Json
from threading import Thread
import logging
from colorlog import ColoredFormatter
import os
import sys
import traceback
import random

_SPACE = ["get key", "search", "search random", "data", "accept"]
_GAMES = {}
_RANDOM_SEARCH = []
_SESSION = {}
_ACCEPT = {}


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOG_FORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger()
log.setLevel(LOG_LEVEL)
if log.hasHandlers():
    log.handlers.clear()
log.addHandler(stream)
os.chdir(os.path.dirname(__file__))


class Switch(object):
    value = None

    def __new__(cls, value):
        cls.value = value
        return True


def case(*args):
    return any((arg == Switch.value for arg in args))


def client_left(client, server):
    msg = "Client (%s) left" % str(client['id'])
    if client["id"] in _SESSION:
        del _SESSION[client["id"]]
    if client["id"] in _GAMES:
        del _GAMES[client["id"]]
    if client["id"] in _RANDOM_SEARCH:
        _RANDOM_SEARCH.reomve(client["id"])
    log.info(msg)


def new_client(client, server):
    msg = "New client (%s) connected" % client['id']
    log.info(msg)
    _SESSION[client["id"]] = client
    server.send_message(client, "Welcome to Online XO Game!")

def key_is_created(key):
    for user in _GAMES:
        if key == _GAMES[user]["key"]:
            return True
    return False

def get_client_key(_id):
    if _id in _GAMES:
        return _GAMES[_id]["key"]
    return None

def get_client_id_by_key(key):
    for _id in _GAMES:
        if key == _GAMES[_id]["key"]:
            return _id
    return None

def on_data(packet, client, server):
    json = Json()
    json.set_json(packet)
    space = json.get("space")
    while Switch(space):
        if case("get key"):
            old = get_client_key(client["id"])
            if old:
                data = {"type": "success", "space": "get key", "key": key}
                server.send_message(cleint, str(data))
                return
            key = get_random_key()
            while key_is_created(key):
                key = get_random_key()
            data = {"type": "success", "space": "get key", "key": key}
            server.send_message(client, str(data))
            c = client["id"]
            _GAMES[c] = {}
            _GAMES[c]["key"] = key
            _GAMES[c]["isPlay"] = False
            _GAMES[c]["playWith"] = None
        if case("search"):
            key = json.get("key")
            if key_is_created(key):
                _id = client["id"]
                wid = get_client_id_by_key(key)
                if _GAMES[wid]["isPlay"]:
                    data = {"space": "invite", "status": "playing"}
                    server.send_message(client, str(data))
                else:
                    session = _SESSION[wid]
                    _with = _GAMES[client["id"]]["key"]
                    start_game(_id, wid)
                    data = {"space": "play", "with": _with, "play": _GAMES[_id]["play"], "are": _GAMES[_id]["him"]}
                    server.send_message(session, str(data))
                    data["with"] = _GAMES[_id]["key"]
                    data["play"] = False if _GAMES[_id]["play"] else True
                    data["are"] = "X" if _GAMES[_id]["him"] == "O" else "O"
                    server.send_message(client, str(data))

            else:
                data = {"space": "invite", "status": "offline"}
                server.send_message(client, str(data))
            break
        if case("search random"):
            if _RANDOM_SEARCH:
                _id = _RANDOM_SEARCH[0]
                if _id == client["id"]:
                    return
                if _id in _SESSION:
                    session = _SESSION[_id]
                    _with = _GAMES[client["id"]]["key"]
                    start_game(_id, client["id"])
                    data = {"space": "play", "with": _with, "play": _GAMES[_id]["play"], "are": _GAMES[_id]["him"]}
                    server.send_message(session, str(data))
                    _RANDOM_SEARCH.remove(_id)
                    data["with"] = _GAMES[_id]["key"]
                    data["play"] = False if _GAMES[_id]["play"] else True
                    data["are"] = "X" if _GAMES[_id]["him"] == "O" else "O"
                    server.send_message(client, str(data))
                else:
                    _RANDOM_SEARCH.remove(_id)
            else:
                _RANDOM_SEARCH.append(client["id"])
            break
        if case("data"):
            k = int(json.get("set"))
            _id = client["id"]
            if _id in _GAMES and _GAMES[_id]["isPlay"] == True:
                used = _GAMES[_id]["hasuse"]
                used.append(k)
                _GAMES[_id]["hasuse"] = used
                _GAMES[_id]["play"] = True
                board = _GAMES[_id]["board"]
                k = k -1
                try:
                    board[k] = 1 if _GAMES[_id]["him"] == "X" else 0
                except:
                    pass
                _GAMES[_id]["board"] = board
                wins = check_win(board)
                move = _GAMES[_id]["move"]
                move += 1
                _GAMES[_id]["move"] = move
                if wins != -1:
                    wid = _GAMES[_id]["playWith"]
                    _GAMES[_id]["isPlay"] = False
                    _GAMES[wid]["isPlay"] = False
                    data = {"space": "play", "status": "re", "play": True, "key": k + 1, "you": True}
                    server.send_message(client, str(data))
                    data["play"] = False
                    data["you"] = False
                    session = _SESSION[wid]
                    server.send_message(session, str(data))
                    data = {"space": "play", "status": "win-you", "with": wid}
                    server.send_message(client, str(data))
                    session = _SESSION[wid]
                    data["status"] = "lost-you"
                    data["with"] = _id
                    server.send_message(session, str(data))
                elif move == 9:
                    wid = _GAMES[_id]["playWith"]
                    _GAMES[_id]["isPlay"] = False
                    _GAMES[wid]["isPlay"] = False
                    data = {"space": "play", "status": "re", "play": True, "key": k + 1, "you": True}
                    server.send_message(client, str(data))
                    data["play"] = False
                    data["you"] = False
                    session = _SESSION[wid]
                    server.send_message(session, str(data))
                    data = {"space": "play", "status": "vs", "with": wid}
                    session = _SESSION[wid]
                    server.send_message(client, str(data))
                    data["with"] = _id
                    server.send_message(session, str(data))
                else:
                    wid = _GAMES[_id]["playWith"]
                    _GAMES[wid]["play"] = False
                    _GAMES[wid]["move"] = move
                    data = {"space": "play", "status": "re", "play": True, "key": k + 1, "you": True}
                    server.send_message(client, str(data))
                    data["play"] = False
                    data["you"] = False
                    session = _SESSION[wid]
                    server.send_message(session, str(data))
        if case("accept"):
            _id = json.get("id")
            acc = json.get("status")
            if client["id"] in _ACCEPT and _ACCEPT[client["id"]] == _id:
                wid = get_client_id_by_key(_ACCEPT[client["id"]])
                session = _SESSION[wid]
                _with = _GAMES[client["id"]]["key"]
                start_game(_id, client["id"])
                data = {"space": "play", "with": _with, "play": _GAMES[_id]["play"], "are": _GAMES[_id]["him"]}
                server.send_message(session, str(data))
                _RANDOM_SEARCH.remove(_id)
                data["with"] = _GAMES[_id]["key"]
                data["play"] = False if _GAMES[_id]["play"] else True
                data["are"] = "X" if _GAMES[_id]["him"] == "O" else "O"
                server.send_message(client, str(data))
                del _ACCEPT[client["id"]]
            else:
                data = {"space": "accept", "status": "error"}
                server.send_message(client, str(data))
                
        break

def start_game(_id, _id1):
    board = []
    for x in range(9):
        board.append(-1)
    _GAMES[_id]["board"] = board
    _GAMES[_id]["isPlay"] = True
    _GAMES[_id]["playWith"] = _id1
    _GAMES[_id]["move"] = 0
    _GAMES[_id]["play"] = random.choice([True, False])
    _GAMES[_id]["him"] = random.choice(["X", "O"])
    _GAMES[_id]["hasuse"] = []
    _GAMES[_id1]["board"] = board
    _GAMES[_id1]["isPlay"] = True
    _GAMES[_id1]["playWith"] = _id
    _GAMES[_id1]["move"] = 0
    _GAMES[_id1]["play"] = False if _GAMES[_id]["play"] else True
    _GAMES[_id1]["him"] = "X" if _GAMES[_id]["him"] == "O" else "O"
    _GAMES[_id1]["hasuse"] = []
    return True

def check_win(board):
        win_cond = ((1, 2, 3), (4, 5, 6), (7, 8, 9), (1, 4, 7), (2, 5, 8), (3, 6, 9), (1, 5, 9), (3, 5, 7))
        for each in win_cond:
            try:
                if board[each[0] - 1] == board[each[1] - 1] and board[each[1] - 1] == board[each[2] - 1]:
                    return board[each[0] - 1]
            except:
                pass
        return -1

def get_random_key():
    ran = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    a = random.choice(ran)
    b = random.choice(ran)
    c = random.choice(ran)
    d = random.choice(ran)
    e = random.choice(ran)
    return a+b+c+d+e


def msg_received(client, server, packet):
    try:
        packet = eval(packet)
    except NameError:
        log.warning("can't eval packet! error from client!")
        return
    json = Json()
    json.set_json(packet)
    space = json.get("space")
    if space in _SPACE:
        on_data(packet, client, server)
    else:
        log.warning("client id({}) send unknown space: {}".format(client["id"], packet))


server = WebsocketServer(80)
log.info("start service on post: 80")
log.info("----------------------------------")
log.warning("XO server has been started!")
log.warning("""
  1  |  2  |  3
-----------------
  4  |  5  |  6
-----------------
  7  |  8  |  9

""")
log.warning("This server wroted by: Omar Othman")
log.info("----------------------------------")
server.set_fn_client_left(client_left)
server.set_fn_new_client(new_client)
server.set_fn_message_received(msg_received)
server.run_forever()
