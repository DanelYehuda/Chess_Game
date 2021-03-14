
# דף שאחראי על פעולות השחקן


import pygame as p
from Chess import ChessEngine
from network import Network
import pickle
import conf

WIDTH = HEIGHT = 512
DIMENSION = 8 # dimensions of chess board are 8*8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15 # בישביל אנימציות,תמונות לשניה
IMAGES = {}
WHITE = conf.WHITE
BLACK = conf.BLACK
COLORS = [WHITE, BLACK]
DISPLAY_COLORS = ["white", "black"]

# פעולה שטוענת את התמונות
def loadImages():
    pieces = ["wp","wR","wN","wB","wQ","wK","bp","bR","bN","bB","bQ","bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"),(SQ_SIZE,SQ_SIZE)) #  המילון יכיל את שמות החיילים כמפתחות והערכים יהיו התמונה שמתאימה לכל חייל, נכניס את החיילים למילון שנוכל להשתמש בו אחר כך

# הפונקציה הראשית אותה נריץ בסופו של דבר
def main():
    chess_client = Network()
    player = int(chess_client.getP())
    p.display.set_caption(str(DISPLAY_COLORS[player]))
    print(f"the player is now {player}")
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT)) # פעולה שיוצרת מסך
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState(player)
    validMoves = gs.getValidMoves() # שם במשתנה את כל הצעדים האפשריים כרגע
    moveMade = False # flag varible for when a move is made
    animate = False #flag var for when we should animate
    loadImages() # only do this once , before the while
    running = True
    sqSelected = () # ישמור את הריבוע הראשון שנלחץ עליו
    playerClicks = [] # [(6,4),(4,4)] יכיל את הקליקים של השחקן של המיקום הראשון והשני כך:
    gameOver = False
    black_first_move = True

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            #לחיצה על העכבר
            elif e.type == p.MOUSEBUTTONDOWN: #מזהה קליק של העכבר
                if not gameOver:
                    location = p.mouse.get_pos() # המיקום של העכבר ב x ו y
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col): # בדיקה אם המשתמש לחץ פעמים על אותו ריבוע
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) # מכניס את הקליק הראשון והשני
                    if len(playerClicks) == 2: # אחרי  הקליק השני
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board) #יוצר את ההמרה בין הנקודה בפיתון לנקודה ב לוח שחמט
                        #print(move.getChessNotation()) # מדפיס את הצעד בנוסח שחמט
                        if move in validMoves: # בןדק אם הצעד אפשרי
                            gs.makeMove(move)
                            moveMade = True # אומר שבוצע צעד
                            animate = True
                            sqSelected = () # נרסט את הקליקים
                            playerClicks = []
                        else:
                            playerClicks = [sqSelected]
            # לחיצה על מקלדת
            elif e.type == p.KEYDOWN:
                if e.key == p.K_r:  #reset the board when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade and player == conf.WHITE: # אם בוצע צעד
            print(f"the player is now {player}")
            if animate:
                animateMove(gs.movelog[-1], screen, gs.board, clock, gs)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            drawGameState(screen, gs, validMoves, sqSelected)
            p.display.flip()
            gs.editBoard(chess_client.send_data(gs.board))
            validMoves = gs.getValidMoves()

        elif moveMade and player == conf.BLACK: # אם בוצע צעד
            print(f"the player is now {player}")
            if animate:
                animateMove(gs.movelog[-1], screen, gs.board, clock, gs)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            drawGameState(screen, gs, validMoves, sqSelected)
            p.display.flip()
            gs.editBoard(chess_client.send_data(gs.board))
            validMoves = gs.getValidMoves()

        elif player == conf.BLACK and black_first_move:
            black_first_move = False
            gs.editBoard(pickle.loads(chess_client.client.recv(4096)))

        if gs.checkMate:
            gameOver = True
            if gs.color == conf.WHITE:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        drawGameState(screen, gs, validMoves, sqSelected)
        p.display.flip()


# מסמן את החייל שמזיזים ואת המהלכים שלו
def highLightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c =sqSelected
        if gs.board[r][c][0] == ('w' if gs.color == conf.WHITE else 'b'): #בודקים אם הריבוע שנבחר הוא חייל שיכול לזוז
            #highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #כמה הצבע יהיה שקוף
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from this square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))

def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen) # מצייר ריבועים על הלוח
    highLightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board) # מצייר חיילים על אותם ריבועים


def drawBoard(screen): #פעולה שמציירת את הלוח (ללא החיילים)
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE)) # פעולה שמקבלת את המסך,צבע,ועוד פעולה שמקבלת את מידות הריבוע

def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# יצירת אנימציה לחיילים

def animateMove(move, screen, board, clock ,gs):
    colors = [p.Color("white"), p.Color("gray")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #מספר ההזזות על ריבוע אחד
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        #erase the piace moves from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        #draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
        if move.pieceMoved == "--":
            gs.color = COLORS[1 - gs.color]
            break
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Heivitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Purple'))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2,2))


main()
