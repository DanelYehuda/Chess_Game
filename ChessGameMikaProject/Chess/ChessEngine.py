
# קלאס שיהיה אחראי על לוח המשחק ועל מצב השחקנים בו בכל עת
class GameState():
    def __init__(self):
        # 8*8 מערך דו מימדי שכל איבר מאפיין שחקן,השחקנים שחורים יתחילו ב אות b והשחקנים הלבנים
        # באות w כל האותיות השניות מייצגות כל אחת שחקן שונה נגיד bQ זה black quinn ואיפה שיש "--" זה מייצג מקום ריק
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]

        self.moveFunctions = {'p': self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,
                              'B':self.getBishopeMoves,'Q':self.getQueenMoves,'K':self.getKingMoves} # מילון שעוזר לנו לקחת מידע על המהלכים לכל שחקן

        self.whiteToMove = True # משתנה שאומר מתי תור השחקנים הלבנים
        self.movelog = [] #רשימה שנכיל בה את כל המהלכים בלוגים
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False # אין למלך לאן לזוז והוא ב CHESS
        self.staleMate = False # יש למלך לאן לזוז אבל הוא יהיה ב CHESS אם הוא יזוז


    def makeMove(self,move): # פעולה שמחליפה בין המיקומים של הריבועים בלוח מבחינת הסטרינגים
        self.board[move.startRow][move.startCol] = "--" # הופך את הנקודה שבה היה השחקן לריקה
        self.board[move.endRow][move.endCol] = move.pieceMoved # שם בנקודה אליה השחקן זז את הסטרינג של השחקן
        self.movelog.append(move) # נשמור את הצעד לרשימת ה לוגים כדי להראות את ההיסטוריה של הצעדים או להחזיר צעד אחורה
        self.whiteToMove = not self.whiteToMove # מחליף תורות
        # update the king location
        if move.pieceMoved == "wK": #אם זה המלך הלבן
            self.whiteKingLocation = (move.endRow,move.endCol) #תעדכן את מיקום המלך הלבן
        elif move.pieceMoved == "bK": # אם זה המלך השחור
            self.blackKingLocation = (move.endRow,move.endCol) # תעדכן את מיקום המלך השחור

        # להפוך חייל למלכה אם הוא מגיע לסוף הלוח
        if move.pieceMoved == "wp" and move.endRow == 0:
         self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'


    def undoMove(self): #מבטל את הצעד האחרון
        if len(self.movelog) != 0:
            move = self.movelog.pop() # מוציא את הצעד האחרון מהרשימה של הלוגים לתוך move
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the king location
            if move.pieceMoved == "wK":  # אם זה המלך הלבן
                self.whiteKingLocation = (move.startRow, move.startCol)  # תעדכן את מיקום המלך הלבן
            elif move.pieceMoved == "bK":  # אם זה המלך השחור
                self.blackKingLocation = (move.startRow, move.startCol)  # תעדכן את מיקום המלך השחור



    # כל המהלכים שדורשים בדיקה של שח מט
    def getValidMoves(self):

        # 1.למצוא את כל הצעדים האפשריים
        moves = self.getAllPossibleMoves()
        # 2.נבצע את הצעדים
        for i in range(len(moves)-1,-1,-1): # רצים על הרשימה המסוף להתחלה כדי לא לדלג על משתנים
            self.makeMove(moves[i])
       #   3.נמצא את כל הצעדים האפשריים של היריב ונבדוק אם הוא מאיים לנו על המלך
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) # מוציא את הפעולה אם היא לא חוקית
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # בודק אם אין צעדים אפשריים למלך
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    # בודק אם השחקן הנוכחי בשח
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    # בודק אם האויב יכול לתקוף ריבוע מסוים
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove # נשנה את התור לתור היריב כדי לראות את המהלכים שלו
        oppMoves = self.getAllPossibleMoves() # בודק את כל הצעדים של היריב
        self.whiteToMove = not self.whiteToMove # מחזיר את התור חזרה
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False



    # בדיקה למהלכים רגילים
    def getAllPossibleMoves(self): # פעולה שרצה על כל הלוח כל תור ובודקת איזה פעולות אפשריות לכל שחקן
        moves = []
        for r in range(len(self.board)): # רץ על כמות שורות
            for c in range(len(self.board[r])): # רץ על כמות עמודות בשורה
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) # קורא לפעולת ההזזה לפי החייל
        return moves



    # פעולות שבודקות את הצעדים האפשריים לכל חייל
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--": #אם ריבוע אחד קדימה ריק
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--": # אם שני ריבועים קדימה ריקים
                    moves.append(Move((r, c),(r - 2, c), self.board))
            if c-1 >= 0: # בודק שהחייל לא יצא מהגבול בצד שמאל
                if self.board[r-1][c-1][0] == 'b': # אם יש חייל שחור באלכסון שמאל
                    moves.append(Move((r, c), (r - 1, c-1), self.board))

            if c+1 <= 7: # בודק שהחייל לא יצא מהגבול בצד ימין
                if self.board[r - 1][c + 1][0] == 'b': #אם יש חייל שחור באלכסון ימין
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:
            if self.board[r+1][c] == "--": #אם ריבוע אחד קדימה ריק
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--": # אם שני ריבועים קדימה ריקים
                    moves.append(Move((r, c),(r + 2, c), self.board))
            if c-1 >= 0: # בודק שהחייל לא יצא מהגבול בצד שמאל
                if self.board[r+1][c-1][0] == 'w': # אם יש חייל לבן באלכסון שמאל
                    moves.append(Move((r, c), (r + 1, c-1), self.board))

            if c+1 <= 7: # בודק שהחייל לא יצא מהגבול בצד ימין
                if self.board[r + 1][c + 1][0] == 'w': #אם יש חייל לבן באלכסון ימין
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))


    def getRookMoves(self,r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1)) # up,left,down,right
        enemyColor = 'b' if self.whiteToMove else 'w' #בודק מי האויב שלי
        for d in directions:
            for i in range(1,8):
                endRow = r +d[0] * i
                endCol = c +d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--" :
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # friendly piece
                        break
                else: # off board
                    break

    def getBishopeMoves(self,r,c,moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # up,lest,down,right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    def getQueenMoves(self,r,c,moves): # משתמש בפעולות של הצריח והרץ ביחד
        self.getRookMoves(r,c,moves)
        self.getBishopeMoves(r,c,moves)

    def getKingMoves(self,r,c,moves):
        kingMoves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyColor = 'w' if self.whiteToMove else 'b' # בודק את צבע העמית שלי
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKnightMoves(self,r,c,moves):
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor = 'w' if self.whiteToMove else 'b' # בודק את צבע העמית שלי
        for m in knightMoves:
            endRow = r+m[0]
            endCol = c+m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # empty or enemy piece
                    moves.append(Move((r,c),(endRow,endCol),self.board))



class Move():  #קלאס שכל המטרה שלו היא לשמור צעד ולתרגם נקודות מפיתון לנקודות בלוח שחמט
    #  מילונים שמאפשרים לנו להתייחס ללוח השחמט בשיטת ספירה של שחמט במקום בשיטת ספירה של פיתון או כל שפת תוכנה
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()} # מכניס למילון את השורה למעלה אבל הפוך
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}


    def __init__(self,startSq,endSq,board):
        self.startRow = startSq[0]  # ערך ה שורה במיקום הראשון שלחצנו
        self.startCol = startSq[1]  # ערך העמודה במיקום הראשון שלחצנו
        self.endRow = endSq[0] # ערך העמודה במיקום השני שלחצנו
        self.endCol = endSq[1] # ערך העמודה במיקום השני שלחצנו
        self.pieceMoved = board[self.startRow][self.startCol] #הריבוע שאני רוצה להזיז
        self.pieceCaptured = board[self.endRow][self.endCol]  #הריבוע אליו אני רוצה להזיז
        self.moveID = self.startRow * 1000 + self.startCol * 1000 + self.endRow * 10 + self.endCol * 10


    def __eq__(self, other): # דורס את פעולת השווה הרגילה והופך אותה לפעולת שווה בין אובייקטים של Move
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self): # פעולה שמביאה לי שתי נקודות אחרי תירגום בעזרת הפעולה getRankFile
        return self.getRankFile(self.startRow,self.startCol)+self.getRankFile(self.endRow,self.endCol)  #לדוגמא b2b4 אומר b2 ל b4

    def getRankFile(self,r,c): # פעולה שמתרגמת לי נקודה בפיתון לנקודה בלוח שחמט לפי הספירה שם
        return self.colsToFiles[c]+self.rowsToRanks[r]






