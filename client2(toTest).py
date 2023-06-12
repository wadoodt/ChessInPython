import socket
import pygame
import os
import time
import datetime
import threading
from enum import Enum

HOST = socket.gethostname()
PORT = 8000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def receive():
    global pieces, Piece, board, whiteTurn
    while True:
            m = client.recv(1024).decode('utf-8')
            if m[0] == "[":
                pieces[(int(m[1]), int(m[4]))].move([int(m[8]), int(m[11])], True)
            else:
                pieces[(int(m[2]), int(m[5]))].board[int(m[2])][int(m[5])] = ""
                if pieces[(int(m[2]), int(m[5]))].board[int(m[9])][int(m[12])] != "":
                    Piece.removedCounter += 1
                    pieces[Piece.removedCounter] = pieces.pop((int(m[9]), int(m[12])))
                    pieces[Piece.removedCounter].setoffboard()
                if m[0] == 'Q':
                    pieces[(int(m[9]), int(m[12]))] = Queen(pieces[(int(m[2]), int(m[5]))].colour, (int(m[9]), int(m[12])), board.board)
                elif m[0] == 'K':
                    pieces[(int(m[9]), int(m[12]))] = Knight(pieces[(int(m[2]), int(m[5]))].colour, (int(m[9]), int(m[12])), board.board)
                elif m[0] == 'R':
                    pieces[(int(m[9]), int(m[12]))] = Rook(pieces[(int(m[2]), int(m[5]))].colour, (int(m[9]), int(m[12])), board.board)
                elif m[0] == 'B':
                    pieces[(int(m[9]), int(m[12]))] = Bishop(pieces[(int(m[2]), int(m[5]))].colour, (int(m[9]), int(m[12])), board.board)
                Piece.removedCounter += 1
                pieces[Piece.removedCounter] = pieces.pop((int(m[2]), int(m[5])))
                pieces[Piece.removedCounter].setoffboard()
                whiteTurn = False if whiteTurn else True
                Piece.movesAll()


pygame.init()

white, black, red, blue, brown = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255), (150, 75, 0)
WIDTH, HEIGHT, = 925, 800
pieceWidth, pieceHeight = 90, 100

wl = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEKING.png')),
                            (pieceWidth, pieceHeight))
wq = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEQUEEN.png')),
                            (pieceWidth, pieceHeight))
wr = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEROOK.png')),
                            (pieceWidth, pieceHeight))
wp = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEPAWN.png')),
                            (pieceWidth, pieceHeight))
wb = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEBISHOP.png')),
                            (pieceWidth, pieceHeight))
wk = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEKNIGHT.png')),
                            (pieceWidth, pieceHeight))
wqs = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEQUEEN.png')),
                             (pieceWidth / 2, pieceHeight / 2))
wrs = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEROOK.png')),
                             (pieceWidth / 2, pieceHeight / 2))
wbs = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEBISHOP.png')),
                             (pieceWidth / 2, pieceHeight / 2))
wks = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'WHITEKNIGHT.png')),
                             (pieceWidth / 2, pieceHeight / 2))

bl = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKKING.png')),
                            (pieceWidth, pieceHeight))
bq = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKQUEEN.png')),
                            (pieceWidth, pieceHeight))
br = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKROOK.png')),
                            (pieceWidth, pieceHeight))
bp = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKPAWN.png')),
                            (pieceWidth, pieceHeight))
bb = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKBISHOP.png')),
                            (pieceWidth, pieceHeight))
bk = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKKNIGHT.png')),
                            (pieceWidth, pieceHeight))
bqs = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKQUEEN.png')),
                             (pieceWidth / 2, pieceHeight / 2))
brs = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKROOK.png')),
                             (pieceWidth / 2, pieceHeight / 2))
bbs = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKBISHOP.png')),
                             (pieceWidth / 2, pieceHeight / 2))
bks = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'BLACKKNIGHT.png')),
                             (pieceWidth / 2, pieceHeight / 2))
greycircle = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'greycircle.png')),
                                    (pieceWidth, pieceHeight))

my_font = pygame.font.SysFont('Comic Sans MS', 30)
End_font = pygame.font.SysFont('Comic Sans MS', 50)
promotion = False
promotionTile = [0, 0]


class Check(Enum):
    KNIGHT = "Knight"
    PAWN = "Pawn"


class Board:
    def __init__(self):
        self.board = [["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""],
                      ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""],
                      ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""],
                      ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""]]


class Piece:
    counterW, counterB = -1, -1
    listOfPiecesW, listOfPiecesB = {}, {}
    piece = None
    theMoves, protectedPieces, checks = [[], []], [[], []], [[], []]
    removedCounter = -1
    boardHistory = {}

    def __init__(self, colour, position, board):
        self.colour = colour
        self.position = position
        self.moves = []
        self.board = board
        self.hasMoved = False
        self.offboard = False
        if colour == "w":
            Piece.counterW += 1
            Piece.listOfPiecesW[Piece.counterW] = self
            self.Pieces = Piece.listOfPiecesW
            self.enemyPieces = Piece.listOfPiecesB
        else:
            Piece.counterB += 1
            Piece.listOfPiecesB[Piece.counterB] = self
            self.Pieces = Piece.listOfPiecesB
            self.enemyPieces = Piece.listOfPiecesW
        board[position[0]][position[1]] = colour + self.piece

    def getPosition(self):
        return self.position

    @staticmethod
    def kingProtector(king, point, direction):
        dummy = [point[0] + direction[0], point[1] + direction[1]]
        while -1 < dummy[0] < 8 and -1 < dummy[1] < 8:
            if king.board[dummy[0]][dummy[1]] == "":
                pass
            elif king.board[dummy[0]][dummy[1]][0] == king.colour:
                king.enemyPieces[15].kingLine.append([dummy, direction])
            else:
                return
            dummy = [dummy[0] + direction[0], dummy[1] + direction[1]]

    @staticmethod
    def interKing(listOfKings):
        a, b = [], []
        for i in listOfKings:
            i.kingLine = []
            for direction in King.directions:
                x, y = i.getPosition()[0] + direction[0], i.getPosition()[1] + direction[1]
                if 0 <= x <= 7 and 0 <= y <= 7:
                    i.moves.append([x, y])
                    if i.board[x][y] == "":
                        b.append([x, y])
                        Piece.kingProtector(i, [x, y], direction)
                    elif i.board[x][y][0] != i.colour:
                        b.append([x, y])
                    else:
                        i.enemyPieces[15].kingLine.append([[x, y], direction])
        for i in listOfKings[0].moves:
            if i in listOfKings[1].moves:
                a.append(i)
        for i in listOfKings:
            i.moves = [move for move in i.moves if (move not in a and move in b)]

    def setPosition(self, position):
        self.position = position
        self.board[position[0]][position[1]] = self.colour + self.piece

    def setoffboard(self):
        self.offboard = True
        self.position = [-1, -1]

    def isItCovering(self):
        for i in self.Pieces[15].protectors:
            if i[1] == self.position:
                return i[0]

    def checkRemoverMoves(self):
        checks = Piece.checks[1] if self.colour == 'w' else Piece.checks[0]
        restrictor = Piece.isItCovering(self)
        if restrictor and isinstance(self, Knight) is True:
            self.moves = []
        elif restrictor:
            self.moves = [move for move in self.moves if (move in restrictor)]
        elif len(checks) == 2:
            self.moves = []
        elif len(checks) == 1:
            length = len(self.moves)
            if checks[0][-1] == Check.KNIGHT:  # Enum to be added
                for i in range(length):
                    if self.moves[length - 1 - i] != checks[0][0]:
                        self.moves.pop(length - 1 - i)
            elif checks[0][-1] == Check.PAWN:
                for i in range(length):
                    if self.moves[length - 1 - i] != checks[0][0]:
                        self.moves.pop(length - 1 - i)
            else:
                self.moves = [move for move in self.moves if (move in checks[0][0])]

    @staticmethod
    def movesAll():
        Piece.theMoves, Piece.protectedPieces, Piece.checks = [[], []], [[], []], [[], []]
        for i in pieces.values():
            i.moves = []
        Piece.interKing([Piece.listOfPiecesW[15], Piece.listOfPiecesB[15]])
        [i.getMoves() if (isinstance(i, King) is False and i.offboard is False) else None for i in pieces.values()]
        Piece.listOfPiecesW[15].getMoves()
        Piece.listOfPiecesB[15].getMoves()
        for i in pieces.values():
            if (isinstance(i, King) is False and i.offboard is False):
                i.checkRemoverMoves()
        Piece.winOrDraw()

    @staticmethod
    def winOrDraw():
        global whiteWon, blackWon, draw, theEnd
        listW, listB, noMovesW, noMovesB = [[], []], [[], []], True, True
        for key, value in Piece.listOfPiecesB.items():
            if value.offboard == False:
                listB[0].append(value)
                listB[1].append(value.piece)
        for key, value in Piece.listOfPiecesW.items():
            if value.offboard == False:
                listW[0].append(value)
                listW[1].append(value.piece)
        if any(len(i.moves) > 0 for i in listB[0]):
            noMovesB = False
        if any(len(i.moves) > 0 for i in listW[0]):
            noMovesW = False
        if noMovesB and not whiteTurn:
            if Piece.checks[0]:
                whiteWon = "White Won with Checkmate"
            else:
                draw = "Draw by Stalemate"
        elif noMovesW and whiteTurn:
            if Piece.checks[1]:
                blackWon = "Black Won with Checkmate"
            else:
                draw = "Draw by Stalemate"
        elif len(listB[1]) == len(listW[1]) == 1:
            draw = "Insufficient Material Draw"
        elif (len(listW[1]) == 2 and "b" in listW[1] and len(listB[1]) == 1) or (
                len(listB[1]) == 2 and "b" in listB[1] and len(listW[1]) == 1):
            draw = "Insufficient Material Draw"
        elif (len(listW[1]) == 2 and "k" in listW[1] and len(listB[1]) == 1) or (
                len(listB[1]) == 2 and "k" in listB[1] and len(listW[1]) == 1):
            draw = "Insufficient Material Draw"
        elif len(listB[1]) == len(listW[1]) == 2 and "b" in listW[1] and "b" in listB[1]:
            a = listW[1][listW.index("b")].getPosition()
            b = listB[1][listB.index("b")].getPosition()
            if abs(a[0] - a[1]) % 2 == abs(b[0] - b[1]) % 2:
                draw = "Insufficient Material Draw"
        if whiteWon:
            theEnd = End_font.render(whiteWon, False, (0, 0, 0))
        elif blackWon:
            theEnd = End_font.render(blackWon, False, (0, 0, 0))
        elif draw:
            theEnd = End_font.render(draw, False, (0, 0, 0))

    def move(self, place, isEnemyMove=False):
        global whiteTurn, firstchoice, secondtile, pieces, promotion, promotionTile, draw, theEnd, promotionPos
        a = str(self.getPosition()) + ":" + str(place)
        if place not in self.moves:
            return
        for key, value in pieces.items():
            if isinstance(value, Pawn):
                value.enPassant = False
        if isinstance(self, Pawn) is True and abs(self.getPosition()[1] - place[1]) == 2:
            self.enPassant = True
        if isinstance(self, Pawn):
            self.board[self.getPosition()[0]][self.getPosition()[1]] = ""
            self.hasMoved = True
            if self.getPosition()[0] - place[0] != 0 and self.board[place[0]][place[1]] == "":
                Piece.removedCounter += 1
                if self.colour == "b":
                    self.board[place[0]][place[1] - 1] = ""
                    pieces[(place[0], place[1] - 1)].setoffboard()
                    pieces[Piece.removedCounter] = pieces.pop((place[0], place[1] - 1))
                else:
                    self.board[place[0]][place[1] + 1] = ""
                    pieces[(place[0], place[1] + 1)].setoffboard()
                    pieces[Piece.removedCounter] = pieces.pop((place[0], place[1] + 1))
            if (self.colour == 'w' and place[1] == 0) or (self.colour == 'b' and place[1] == 7):
                promotionPos = str(self.getPosition())
                if self.board[place[0]][place[1]] != "":
                    pieces[tuple(place)].setoffboard()
                    Piece.removedCounter += 1
                    pieces[Piece.removedCounter] = pieces.pop(tuple(place))
                promotion = True
                promotionTile = place
                Piece.removedCounter += 1
                pieces[Piece.removedCounter] = pieces.pop(tuple(self.getPosition()))
                pieces[Piece.removedCounter].setoffboard()
                self.board[place[0]][place[1]] = ""
            else:
                if self.board[place[0]][place[1]] != "":
                    pieces[tuple(place)].setoffboard()
                    Piece.removedCounter += 1
                    pieces[Piece.removedCounter] = pieces.pop(tuple(place))
                pieces[tuple(place)] = pieces.pop(tuple(self.getPosition()))
                self.setPosition(place)
                whiteTurn = False if whiteTurn else True
                Piece.movesAll()
                firstchoice, secondtile = 1, 0
                if isEnemyMove is False:
                    client.send(a.encode('utf-8'))
        elif abs(w := self.getPosition()[0] - place[0]) == 2 and isinstance(self, King):
            if w == -2:
                pieces[tuple(place)] = pieces.pop(tuple(self.getPosition()))
                pieces[(self.getPosition()[0] + 1, self.getPosition()[1])] = pieces.pop((7, self.getPosition()[1]))
                self.board[self.getPosition()[0]][self.getPosition()[1]] = ""
                self.board[7][self.getPosition()[1]] = ""
                self.setPosition(place)
                self.Pieces[13].setPosition([self.position[0] - 1, self.position[1]])
                self.Pieces[13].hasMoved = True
            else:
                pieces[tuple(place)] = pieces.pop(tuple(self.getPosition()))
                pieces[(self.getPosition()[0] - 1, self.getPosition()[1])] = pieces.pop((0, self.getPosition()[1]))
                self.board[self.getPosition()[0]][self.getPosition()[1]] = ""
                self.board[0][self.getPosition()[1]] = ""
                self.setPosition(place)
                self.Pieces[12].setPosition([self.position[0] + 1, self.position[1]])
                self.Pieces[12].hasMoved = True
            self.hasMoved = True
            whiteTurn = False if whiteTurn else True
            Piece.movesAll()
            firstchoice, secondtile = 1, 0
            if isEnemyMove is False:
                client.send(a.encode('utf-8'))
        else:
            if self.board[place[0]][place[1]] != "":
                pieces[tuple(place)].setoffboard()
                Piece.removedCounter += 1
                pieces[Piece.removedCounter] = pieces.pop(tuple(place))
            pieces[tuple(place)] = pieces.pop(tuple(self.getPosition()))
            self.board[self.getPosition()[0]][self.getPosition()[1]] = ""
            self.setPosition(place)
            self.hasMoved = True
            whiteTurn = False if whiteTurn else True
            Piece.movesAll()
            firstchoice, secondtile = 1, 0
            if isEnemyMove is False:
                client.send(a.encode('utf-8'))
        boardc = tuple(tuple(sub) for sub in self.board)
        if boardc in Piece.boardHistory:
            Piece.boardHistory[boardc] += 1
        else:
            Piece.boardHistory[boardc] = 1
        if 3 in Piece.boardHistory.values():
            draw = "Draw by Repetition"
            theEnd = End_font.render(draw, False, (0, 0, 0))


class Knight(Piece):
    directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]
    worth = 3
    piece = "k"

    def getMoves(self):
        enemyCol = "w" if self.colour == "b" else "b"
        for direction in Knight.directions:
            x, y = self.position[0] + direction[0], self.position[1] + direction[1]
            if 0 <= x <= 7 and 0 <= y <= 7:
                if self.board[x][y] != "" and self.board[x][y] == enemyCol + "l":
                    Piece.checks[0].append([self.getPosition(), Check.PAWN]) if self.colour == 'w' else Piece.checks[
                        1].append([self.getPosition(), Check.KNIGHT])
                elif (self.board[x][y] == "" or self.board[x][y][0] == enemyCol):
                    self.moves.append([x, y])
                else:
                    Piece.protectedPieces[0].append([x, y]) if self.colour == 'w' else Piece.protectedPieces[1].append(
                        [x, y])
        Piece.theMoves[0].append(self.moves) if self.colour == 'w' else Piece.theMoves[1].append(self.moves)


class King(Piece):
    directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]
    piece = "l"

    def __init__(self, colour: str, position: list, board: list):
        super().__init__(colour, position, board)
        self.kingLine = []
        self.protectors = []

    def getMoves(self):
        if self.colour == 'w':
            enemymoves, restrictors, checks = Piece.theMoves[1], Piece.protectedPieces[1], Piece.checks[1]
        else:
            enemymoves, restrictors, checks = Piece.theMoves[0], Piece.protectedPieces[0], Piece.checks[0]
        if checks:
            for u in checks:
                if u[-1] != Check.KNIGHT and u[-1] != Check.PAWN:
                    if (-1 < self.position[0] + u[1][0] < 8 and -1 < self.position[1] + u[1][1] < 8):
                        restrictors.append([self.position[0] + u[1][0], self.position[1] + u[1][1]])
        elif len(checks) == 0 and self.hasMoved == False:
            if self.board[self.position[0] + 1][self.position[1]] == "" and self.board[self.position[0] + 2][
                self.position[1]] == "" and self.Pieces[13].hasMoved == False:
                self.moves.append([self.position[0] + 2, self.position[1]])
            if self.board[self.position[0] - 1][self.position[1]] == "" and self.board[self.position[0] - 2][
                self.position[1]] == "" and self.board[self.position[0] - 3][self.position[1]] == "" and self.Pieces[
                12].hasMoved == False:
                self.moves.append([self.position[0] - 2, self.position[1]])
        for piece in enemymoves:
            for move in piece:
                if move in self.moves:
                    self.moves.remove(move)
                if (a := [self.position[0] + 2, self.position[1]]) in self.moves:
                    if move == [self.position[0] + 1, self.position[1]] or move == [self.position[0] + 2,
                                                                                    self.position[1]]:
                        self.moves.remove(a)
                if (b := [self.position[0] - 2, self.position[1]]) in self.moves:
                    if move == [self.position[0] - 1, self.position[1]] or move == [self.position[0] - 2,
                                                                                    self.position[1]]:
                        self.moves.remove(b)
        self.moves = [move for move in self.moves if move not in restrictors]


class Pawn(Piece):
    def __init__(self, colour: str, position: list, board: list):
        super().__init__(colour, position, board)
        self.enPassant = False

    worth = 1
    piece = "p"

    def getMoves(self):
        pos = self.getPosition()
        enemyCol = 'b' if self.colour == 'w' else 'w'
        dir = -1 if self.colour == 'w' else 1
        if -1 < pos[0] - 1 < 8 and -1 < pos[1] + dir < 8:
            if self.board[pos[0] - 1][pos[1] + dir] != "" and self.board[pos[0] - 1][pos[1] + dir][0] == enemyCol:
                if (self.board[pos[0] - 1][pos[1] + dir][1] == "l"):
                    Piece.checks[0].append([pos, Check.PAWN]) if self.colour == 'w' else Piece.checks[1].append(
                        [pos, [1, - dir], 'Pawn'])
                else:
                    self.moves.append([pos[0] - 1, pos[1] + dir])
            elif self.board[pos[0] - 1][pos[1] + dir] == "" and self.board[pos[0] - 1][pos[1]] != "" and \
                    self.board[pos[0] - 1][pos[1]] == enemyCol + "p" and pieces[(pos[0] - 1, pos[1])].enPassant is True:
                self.moves.append([pos[0] - 1, pos[1] + dir])
            elif self.board[pos[0] - 1][pos[1] + dir] == "" or self.board[pos[0] - 1][pos[1] + dir][0] == self.colour:
                Piece.protectedPieces[0].append([pos[0] - 1, pos[1] + dir]) if self.colour == 'w' else \
                    Piece.protectedPieces[1].append([pos[0] - 1, pos[1] + dir])
        if -1 < pos[0] + 1 < 8 and -1 < pos[1] + dir < 8:
            if self.board[pos[0] + 1][pos[1] + dir] != "" and self.board[pos[0] + 1][pos[1] + dir][0] == enemyCol:
                if (self.board[pos[0] + 1][pos[1] + dir][1] == "l"):
                    Piece.checks[0].append([pos, Check.PAWN]) if self.colour == 'w' else Piece.checks[1].append(
                        [pos, [-1, - dir], Check.PAWN])
                else:
                    self.moves.append([pos[0] + 1, pos[1] + dir])
            elif self.board[pos[0] + 1][pos[1] + dir] == "" and self.board[pos[0] + 1][pos[1]] != "" and \
                    self.board[pos[0] + 1][pos[1]] == enemyCol + "p" and pieces[(pos[0] + 1, pos[1])].enPassant is True:
                self.moves.append([pos[0] + 1, pos[1] + dir])
            elif self.board[pos[0] + 1][pos[1] + dir] == "" or self.board[pos[0] + 1][pos[1] + dir][0] == self.colour:
                Piece.protectedPieces[0].append([pos[0] + 1, pos[1] + dir]) if self.colour == 'w' else \
                    Piece.protectedPieces[1].append([pos[0] + 1, pos[1] + dir])
        if -1 < pos[1] + dir < 8 and self.board[pos[0]][pos[1] + dir] == '':
            self.moves.append([pos[0], pos[1] + dir])
            if -1 < pos[1] + 2 * dir < 8 and self.board[pos[0]][pos[1] + 2 * dir] == '' and (
                    pos[1] == 1 or pos[1] == 6):
                self.moves.append([pos[0], pos[1] + 2 * dir])


class Rook(Piece):
    worth = 5
    piece = "r"

    def getMoves(self):
        enemyCol = 'b' if self.colour == 'w' else 'w'
        listForIteration = [[0, 1], [0, -1], [-1, 0], [1, 0]]

        for i in range(0, 4):
            checkLines = [self.getPosition()]
            dummy = [self.position[0] + listForIteration[i][0], self.position[1] + listForIteration[i][1]]
            while -1 < dummy[0] < 8 and -1 < dummy[1] < 8:
                checkLines.append(dummy.copy())
                if self.board[dummy[0]][dummy[1]] == '':
                    self.moves.append(dummy.copy())
                elif self.board[dummy[0]][dummy[1]][0] == enemyCol:
                    if self.board[dummy[0]][dummy[1]][1] == 'l':
                        checkLines.pop()
                        if self.colour == 'w':
                            Piece.checks[0].append([checkLines.copy(), listForIteration[i]])
                        else:
                            Piece.checks[1].append([checkLines.copy(), listForIteration[i]])
                    elif [dummy, [-listForIteration[i][0], -listForIteration[i][1]]] in self.Pieces[15].kingLine:
                        checkLines.pop()
                        self.enemyPieces[15].protectors.append([checkLines.copy(), dummy.copy()])
                        self.moves.append(dummy.copy())
                    else:
                        self.moves.append(dummy.copy())
                    break
                else:
                    Piece.protectedPieces[0].append(dummy.copy()) if self.colour == 'w' else Piece.protectedPieces[
                        1].append(dummy.copy())
                    break
                dummy[0] += listForIteration[i][0]
                dummy[1] += listForIteration[i][1]
        Piece.theMoves[0].append(self.moves.copy()) if self.colour == 'w' else Piece.theMoves[1].append(
            self.moves.copy())


class Bishop(Piece):
    worth = 3
    piece = "b"

    def getMoves(self):
        enemyCol = 'b' if self.colour == 'w' else 'w'
        listForIteration = [[1, 1], [-1, 1], [-1, -1], [1, -1]]

        for i in range(0, 4):
            checkLines = [self.getPosition()]
            dummy = [self.position[0] + listForIteration[i][0], self.position[1] + listForIteration[i][1]]
            while -1 < dummy[0] < 8 and -1 < dummy[1] < 8:
                checkLines.append(dummy.copy())
                if self.board[dummy[0]][dummy[1]] == '':
                    self.moves.append(dummy.copy())
                elif self.board[dummy[0]][dummy[1]][0] == enemyCol:
                    if self.board[dummy[0]][dummy[1]][1] == 'l':
                        checkLines.pop()
                        if self.colour == 'w':
                            Piece.checks[0].append([checkLines.copy(), listForIteration[i]])
                        else:
                            Piece.checks[1].append([checkLines.copy(), listForIteration[i]])
                    elif [dummy, [-listForIteration[i][0], -listForIteration[i][1]]] in self.Pieces[15].kingLine:
                        checkLines.pop()
                        self.enemyPieces[15].protectors.append([checkLines.copy(), dummy.copy()])
                        self.moves.append(dummy.copy())
                    else:
                        self.moves.append(dummy.copy())
                    break
                else:
                    Piece.protectedPieces[0].append(dummy.copy()) if self.colour == 'w' else Piece.protectedPieces[
                        1].append(dummy.copy())
                    break
                dummy[0] += listForIteration[i][0]
                dummy[1] += listForIteration[i][1]
        Piece.theMoves[0].append(self.moves) if self.colour == 'w' else Piece.theMoves[1].append(self.moves)


class Queen(Piece):
    worth = 9
    piece = "q"

    def getMoves(self):
        enemyCol = 'b' if self.colour == 'w' else 'w'
        listForIteration = [[0, 1], [0, -1], [-1, 0], [1, 0], [1, 1], [-1, 1], [-1, -1], [1, -1]]

        for i in range(0, 8):
            checkLines = [self.getPosition()]
            dummy = [self.position[0] + listForIteration[i][0], self.position[1] + listForIteration[i][1]]
            while -1 < dummy[0] < 8 and -1 < dummy[1] < 8:
                checkLines.append(dummy.copy())
                if self.board[dummy[0]][dummy[1]] == '':
                    self.moves.append(dummy.copy())
                elif self.board[dummy[0]][dummy[1]][0] == enemyCol:
                    if self.board[dummy[0]][dummy[1]][1] == 'l':
                        checkLines.pop()
                        if self.colour == 'w':
                            Piece.checks[0].append([checkLines.copy(), listForIteration[i]])
                        else:
                            Piece.checks[1].append([checkLines.copy(), listForIteration[i]])
                    elif [dummy, [-listForIteration[i][0], -listForIteration[i][1]]] in self.Pieces[15].kingLine:
                        checkLines.pop()
                        self.enemyPieces[15].protectors.append([checkLines.copy(), dummy.copy()])
                        self.moves.append(dummy.copy())
                    else:
                        self.moves.append(dummy.copy())
                    break
                else:
                    Piece.protectedPieces[0].append(dummy.copy()) if self.colour == 'w' else Piece.protectedPieces[
                        1].append(dummy.copy())
                    break
                dummy[0] += listForIteration[i][0]
                dummy[1] += listForIteration[i][1]
        Piece.theMoves[0].append(self.moves) if self.colour == 'w' else Piece.theMoves[1].append(self.moves)


def timer_thread():
    global run, whiteTurn, whiteTimer, blackTimer, blackWon, whiteWon, theEnd
    reset = True
    whitesTime = 300
    blacksTime = 300
    whitesTimeToPrint = str(datetime.timedelta(seconds=whitesTime))
    whiteTimer = my_font.render(whitesTimeToPrint, False, (0, 0, 0))
    blacksTimeToPrint = str(datetime.timedelta(seconds=blacksTime))
    blackTimer = my_font.render(blacksTimeToPrint, False, (0, 0, 0))
    while run:
        if draw == "" and blackWon == "" and whiteWon == "":
            time.sleep(1)
            if whitesTime == 300:
                whitesTimeToPrint = str(datetime.timedelta(seconds=whitesTime))
                whiteTimer = my_font.render(whitesTimeToPrint, False, (0, 0, 0))
                blacksTimeToPrint = str(datetime.timedelta(seconds=blacksTime))
                blackTimer = my_font.render(blacksTimeToPrint, False, (0, 0, 0))
                reset = True
            if draw == "" and blackWon == "" and whiteWon == "":
                if whiteTurn:
                    whitesTime -= 1
                else:
                    blacksTime -= 1
            whitesTimeToPrint = str(datetime.timedelta(seconds=whitesTime))
            whiteTimer = my_font.render(whitesTimeToPrint, False, (0, 0, 0))
            blacksTimeToPrint = str(datetime.timedelta(seconds=blacksTime))
            blackTimer = my_font.render(blacksTimeToPrint, False, (0, 0, 0))
            if whitesTime <= 0:
                blackWon = "Black won by time"
                theEnd = End_font.render(blackWon, False, (0, 0, 0))
            elif blacksTime <= 0:
                whiteWon = "White won by time"
                theEnd = End_font.render(whiteWon, False, (0, 0, 0))
        elif reset:
            whitesTime = 300
            blacksTime = 300
            reset = False


def createPieces(board):
    global pieces
    for i in range(0, 8):
        pieces[(i, 6)] = Pawn('w', [i, 6], board)
    pieces[(1, 7)], pieces[(6, 7)] = Knight('w', [1, 7], board), Knight('w', [6, 7], board)
    pieces[(2, 7)], pieces[(5, 7)] = Bishop('w', [2, 7], board), Bishop('w', [5, 7], board)
    pieces[(0, 7)], pieces[(7, 7)] = Rook('w', [0, 7], board), Rook('w', [7, 7], board)
    pieces[(3, 7)] = Queen('w', [3, 7], board)
    pieces[(4, 7)] = King('w', [4, 7], board)
    for i in range(16, 24):
        pieces[(i - 16, 1)] = Pawn('b', [i - 16, 1], board)
    pieces[(1, 0)], pieces[(6, 0)] = Knight('b', [1, 0], board), Knight('b', [6, 0], board)
    pieces[(2, 0)], pieces[(5, 0)] = Bishop('b', [2, 0], board), Bishop('b', [5, 0], board)
    pieces[(0, 0)], pieces[(7, 0)] = Rook('b', [0, 0], board), Rook('b', [7, 0], board)
    pieces[(3, 0)] = Queen('b', [3, 0], board)
    pieces[(4, 0)] = King('b', [4, 0], board)


def placePieces(piece, x, y):
    if piece == 'wp':
        Display.blit(wp, (x * 100 + 5, y * 100))
    elif piece == 'wl':
        Display.blit(wl, (x * 100 + 5, y * 100))
    elif piece == 'wq':
        Display.blit(wq, (x * 100 + 5, y * 100))
    elif piece == 'wr':
        Display.blit(wr, (x * 100 + 5, y * 100))
    elif piece == 'wk':
        Display.blit(wk, (x * 100 + 5, y * 100))
    elif piece == 'wb':
        Display.blit(wb, (x * 100 + 5, y * 100))
    elif piece == 'bl':
        Display.blit(bl, (x * 100 + 5, y * 100))
    elif piece == 'bq':
        Display.blit(bq, (x * 100 + 5, y * 100))
    elif piece == 'bp':
        Display.blit(bp, (x * 100 + 5, y * 100))
    elif piece == 'bk':
        Display.blit(bk, (x * 100 + 5, y * 100))
    elif piece == 'br':
        Display.blit(br, (x * 100 + 5, y * 100))
    elif piece == 'bb':
        Display.blit(bb, (x * 100 + 5, y * 100))


def piecesLoop():
    [[placePieces(k, indx, indy) for indy, k in enumerate(i)] for indx, i in enumerate(board.board)]


def draw_window():
    pygame.draw.rect(Display, (200, 200, 200), (0, 0, 800, 800))
    [[pygame.draw.rect(Display, brown, (0 + x * 100, 0 + i * 100, 100, 100)) for x in range(1, 9, 2)] for i in
     range(0, 8, 2)]
    [[pygame.draw.rect(Display, brown, (0 + j * 100, 0 + i * 100, 100, 100)) for j in range(0, 8, 2)] for i in
     range(1, 9, 2)]
    pygame.draw.rect(Display, (150, 150, 150), (800, 0, 200, 800))
    piecesLoop()
    Display.blit(whiteTimer, (808, 500))
    Display.blit(blackTimer, (808, 300))
    if promotion is True:
        if promotionTile[1] == 0:
            Display.blit(wqs, (promotionTile[0] * 100, promotionTile[1] * 100))
            Display.blit(wks, (promotionTile[0] * 100, promotionTile[1] * 100 + 50))
            Display.blit(wbs, (promotionTile[0] * 100 + 50, promotionTile[1] * 100))
            Display.blit(wrs, (promotionTile[0] * 100 + 50, promotionTile[1] * 100 + 50))
        else:
            Display.blit(bqs, (promotionTile[0] * 100, promotionTile[1] * 100))
            Display.blit(bks, (promotionTile[0] * 100, promotionTile[1] * 100 + 50))
            Display.blit(bbs, (promotionTile[0] * 100 + 50, promotionTile[1] * 100))
            Display.blit(brs, (promotionTile[0] * 100 + 50, promotionTile[1] * 100 + 50))
    if whiteWon or blackWon or draw:
        Display.blit(theEnd, (100, 400))
    pygame.display.update()


colMes = client.recv(1024).decode('utf-8')
yourSideW = True if colMes == "W" else False

receive_thread = threading.Thread(target=receive)
receive_thread.start()

Display = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
board, pieces = Board(), {}
createPieces(board.board)
timer = threading.Thread(target=timer_thread)
whiteWon, blackWon, draw, firsttile, firstclick, secondtile, firstchoice, whiteTurn = "", "", "", 0, 0, 0, 1, True
run = True
Piece.movesAll()
timer.start()
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            mousepos = pygame.mouse.get_pos()
            if mousepos[0] < 800:
                if whiteWon == "" and blackWon == "" and draw == "":
                    if promotion:
                        promotionCoord = [promotionTile[0] * 100, promotionTile[1] * 100]
                        if promotionCoord[0] < mousepos[0] < promotionCoord[0] + 100 and promotionCoord[1] < mousepos[
                            1] < promotionCoord[1] + 100:
                            col = 'w' if promotionTile[1] == 0 else 'b'
                            b = ""
                            if promotionCoord[0] <= mousepos[0] < promotionCoord[0] + 50 and promotionCoord[1] <= \
                                    mousepos[1] < promotionCoord[1] + 50:
                                pieces[tuple(promotionTile)] = Queen(col, promotionTile, board.board)
                                b = "Q"
                            elif promotionCoord[0] <= mousepos[0] < promotionCoord[0] + 50 and promotionCoord[1] + 50 <= \
                                    mousepos[1] < promotionCoord[1] + 100:
                                pieces[tuple(promotionTile)] = Knight(col, promotionTile, board.board)
                                b = "K"
                            elif promotionCoord[0] + 50 <= mousepos[0] < promotionCoord[0] + 100 and promotionCoord[
                                1] <= mousepos[1] < promotionCoord[1] + 50:
                                pieces[tuple(promotionTile)] = Bishop(col, promotionTile, board.board)
                                b = "B"
                            elif promotionCoord[0] + 50 <= mousepos[0] < promotionCoord[0] + 100 and promotionCoord[
                                1] + 50 <= mousepos[1] < promotionCoord[1] + 100:
                                pieces[tuple(promotionTile)] = Rook(col, promotionTile, board.board)
                                b = "R"
                            promotion = False
                            whiteTurn = False if whiteTurn else True
                            a = b + str(promotionPos) + ":" + str(promotionTile)
                            client.send(a.encode('utf-8'))
                            Piece.movesAll()
                    elif firstchoice == 1:
                        firstchoice, firstclick = 0, mousepos
                        firsttile = [mousepos[0] // 100, mousepos[1] // 100]
                        if secondtile != 0:
                            a = board.board[secondtile[0]][secondtile[1]]
                            if (not promotion) and a != "" and ((a[0] == 'w' and whiteTurn and yourSideW) or (a[0] == 'b' and not yourSideW and not whiteTurn)):
                                    pieces[tuple(secondtile)].move(firsttile)
                    elif firstchoice == 0:
                        firstchoice, secondclick = 1, mousepos
                        secondtile = [mousepos[0] // 100, mousepos[1] // 100]
                        a = board.board[firsttile[0]][firsttile[1]]
                        if (not promotion) and a != "" and a != "" and ((a[0] == 'w' and whiteTurn and yourSideW) or (a[0] == 'b' and not yourSideW and not whiteTurn)):
                            pieces[tuple(firsttile)].move(secondtile)
                else:
                    draw, blackWon, whiteWon = "", "", ""
                    yourSideW = False if yourSideW else True
                    board = Board()
                    Piece.listOfPiecesB = {}
                    Piece.listOfPiecesW = {}
                    Piece.boardHistory.clear()
                    Piece.counterB, Piece.counterW, Piece.removedCounter = -1, -1, -1
                    pieces = {}
                    createPieces(board.board)
                    whiteTurn = True
                    Piece.movesAll()
    draw_window()