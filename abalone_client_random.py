import socket
import sys
import json
import threading
import json
import jsonNetwork
from random import choice

class abaloneAI:
    def __init__(self, targetIP="localHost", port=5201, name = 'olingo'):
        #initie la premiere connexion et crée certaine variables
        s = socket.socket()
        s.connect((targetIP,3000))
        self.__s = s
        self.port = port
        self.name = name
        self.round = 0
#         self.get_play({
#    "players": ["LUR", "LRG"],
#    "current": 0,
#    "board": [
#       ["W", "W", "W", "W", "W", "X", "X", "X", "X"],
#       ["W", "W", "W", "W", "W", "W", "X", "X", "X"],
#       ["E", "E", "W", "W", "W", "E", "E", "X", "X"],
#       ["E", "E", "E", "E", "E", "E", "E", "E", "X"],
#       ["E", "E", "E", "E", "E", "E", "E", "E", "E"],
#       ["X", "E", "E", "E", "E", "E", "E", "E", "E"],
#       ["X", "X", "E", "E", "B", "B", "B", "E", "E"],
#       ["X", "X", "X", "B", "B", "B", "B", "B", "B"],
#       ["X", "X", "X", "X", "B", "B", "B", "B", "B"]
#    ]
# })

    def run(self):
        #Lance les differents threads, un pour gerer les demande de ping et un autre pour gerer le reste
        self.__running=True
        threading.Thread(target= self.rec).start()
        threading.Thread(target= self.handlePing).start()
        res = json.dumps({"request": "subscribe","port": self.port,"name": self.name,"matricules": ["12345", "67890"]})
        self.__s.send(res.encode('utf8'))

    def rec(self):
        #est censé recevoir toutes els autres demande que le ping mais le code du prof est différents de ce que je pensais du coup ca sert a rien
        while self.__running:
            print("aa")
            data = ''
            try:
                ended =  False
                while not ended:
                    data += self.__s.recv(4096).decode('utf8')
                    if data != '':
                        print(data)
                        if data[0]=='{' and data[-1] == '}':
                            ended = True
                            data = json.loads(data)
            except socket.timeout:
                print('time')
            except OSError:
                print('timeoutos')
        return
    
    def handlePing(self):
        #repond a toutes les demandes de ping et les autres request (play
        # Crée un nouveau socket car le prof lance une connexion tcp
        #voir jsonNetwork pour les fonction
        while self.__running:
            pingSocket = socket.socket()
            pingSocket.bind(("localhost", self.port))
            pingSocket.listen()
            try:
                pingS, pingAdd = pingSocket.accept()
                data = ''
                ended =  False
                while not ended:
                    data += pingS.recv(4096).decode('utf8')
                    if data != '':
                        print(data)
                        if data[0]=='{' and data[-1] == '}':
                            ended = True
                            data = json.loads(data)
                if data == {"request": "ping"}:
                    print('in the fucking if')
                    jsonNetwork.sendJSON(pingS,{"response":"pong"})
                    print('after')
                if "request" in data.keys():
                    if data["request"] == "play":
                        print('request play')
                        move = self.get_play(data["state"])
                        print(move)
                        jsonNetwork.sendJSON(pingS,{"response": "move","move": move,"message": "counter this you casu"})
                        #jsonNetwork.sendJSON(pingS,{"response": "move","move": {"marbles": [[6, 4]],"direction": "NE"},"message": "counter this you casu"})
                pingS.close()
            except EOFError as error:
                print(error)

    def get_play(self, status):
        # renvoie un mouvement "legal" pour ce faire appelle get_plays et analyse le status de la game pour savoir qui on est 
        if status["players"].index(self.name)==0:
            self.us = "B"
            self.enemy = "W"
        else:
            self.us = "W"
            self.enemy = "B"
        if status["board"] == [
            ["W", "W", "W", "W", "W", "X", "X", "X", "X"],
            ["W", "W", "W", "W", "W", "W", "X", "X", "X"],
            ["E", "E", "W", "W", "W", "E", "E", "X", "X"],
            ["E", "E", "E", "E", "E", "E", "E", "E", "X"],
            ["E", "E", "E", "E", "E", "E", "E", "E", "E"],
            ["X", "E", "E", "E", "E", "E", "E", "E", "E"],
            ["X", "X", "E", "E", "B", "B", "B", "E", "E"],
            ["X", "X", "X", "B", "B", "B", "B", "B", "B"],
            ["X", "X", "X", "X", "B", "B", "B", "B", "B"]]:
            self.round = 0
        else:
            self.round+=1
        print(self.us)
        return self.get_plays(status["board"])
        

    def get_plays(self, board):
        #crée un dictionaire avec tout les move legaux possible selon la structure {bille de base:[([bille a bouger], direction)]}
        Xline = ["X", "X", "X", "X", "X", "X", "X", "X", "X","X", "X"]
        possible_moves = {}
        for line in board:
            line.insert(0,"X")
            line.append("X")
        board.insert(0,Xline)
        board.append(Xline)
        for line in range(len(board)):
            for row in range(len(board[line])):
                if board[line][row] == self.us:
                    for dire in ["NE", "NW", "E", "SE", "SW", "W"]:
                        temp_move = self.test_move(board, [line, row], dire)
                        if len(temp_move[0]) !=0:
                            if (line,row) in possible_moves.keys():
                                possible_moves[(line-1,row-1)].append(temp_move)
                            else:
                                possible_moves[(line-1,row-1)]=[temp_move]
        print(possible_moves)
        move = list(possible_moves.values())
        move = choice(move)
        move = choice(move)
        print('my mive is', end= ':')
        print(move)
        return {"marbles":move[0], "direction": move[1]}

    def move_dire(self, board, marble, dire, num = 1):
        #calcule les index de la case suivante dans la direction spécifiée
        line =  marble[0]
        row = marble[1]
        if dire == "NE":
            line = line-num
        if dire == "NW":
            line = line-num
            row = row-num
        if dire == "E":
            row = row+num
        if dire == "SE":
            line = line+num
            row = row+num
        if dire == "SW":
            line = line+num
        if dire == "W":
            row = row-num
        if line ==-1 or row==-1:
            raise IndexError
        return board[line][row], line, row


    def test_move(self, board, marble, dire):
        #vérifie si la direction indiquée pour la bille indiquée permet de faire un mouvement
        marbles = []
        chain_lenght = 1
        try:
            next_marble_1, next_marble_1_l, next_marble_1_r = self.move_dire(board, marble, dire)
            chain_lenght+=1
            next_marble_2, next_marble_2_l, next_marble_2_r = self.move_dire(board, marble, dire, num=2)
            chain_lenght+=1
            next_marble_3, next_marble_3_l, next_marble_3_r = self.move_dire(board, marble, dire, num=3)
            chain_lenght+=1
            next_marble_4, next_marble_4_l, next_marble_4_r = self.move_dire(board, marble, dire, num=4)
            chain_lenght+=1
            next_marble_5, next_marble_5_l, next_marble_5_r = self.move_dire(board, marble, dire, num=5)
            chain_lenght+=1
        except IndexError:
            pass
        if chain_lenght>=2:
            if next_marble_1 == "E":
                marbles.append([marble[0]-1,marble[1]-1])
        if chain_lenght>=3:
            if next_marble_1 == self.us and next_marble_2=="E":
                marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1]))
        if chain_lenght>=4:
            if next_marble_1 == self.us and next_marble_2==self.us and next_marble_3=="E":
                marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
            elif next_marble_1 == self.us and next_marble_2 == self.enemy and (next_marble_3=="E" or next_marble_3=="X"): 
                marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1,next_marble_1_r-1]))
        if chain_lenght>=5:
            if next_marble_1 == self.us and next_marble_2 == self.us and next_marble_3==self.enemy and (next_marble_4=="E" or next_marble_4=="X"):
                marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
        if chain_lenght >= 6:
            if next_marble_1 == self.us and next_marble_2 == self.us and next_marble_3==self.enemy and next_marble_4==self.enemy and (next_marble_5=="E" or next_marble_5=="X"):
                marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
        return (marbles, dire)

                 


abaloneAI(port = int(sys.argv[1]), name = str(sys.argv[2])).run()


start_board_extended=[
["X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
["X", "W", "W", "W", "W", "W", "X", "X", "X", "X", "X"],
["X", "W", "W", "W", "W", "W", "W", "X", "X", "X", "X"],
["X", "E", "E", "W", "W", "W", "E", "E", "X", "X", "X"],
["X", "E", "E", "E", "E", "E", "E", "E", "E", "X", "X"],
["X", "E", "E", "E", "E", "E", "E", "E", "E", "E", "X"],
["X", "X", "E", "E", "E", "E", "E", "E", "E", "E", "X"],
["X", "X", "X", "E", "E", "B", "B", "B", "E", "E", "X"],
["X", "X", "X", "X", "B", "B", "B", "B", "B", "B", "X"],
["X", "X", "X", "X", "X", "B", "B", "B", "B", "B", "X"],
["X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X"]]