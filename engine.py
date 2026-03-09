board=[
    ["r","n","b","q","k","b","n","r"],
    ["p","p","p","p","p","p","p","p"],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    ["P","P","P","P","P","P","P","P"],
    ["R","N","B","Q","K","B","N","R"],
]

current_turn="white"
white_king_moved=False
black_king_moved=False

white_rook_a_moved=False
white_rook_h_moved=False

black_rook_a_moved=False
black_rook_h_moved=False

en_passant_target=None

def copy_board(board):
    new_board=[]
    for row in board:
        new_board.append(row[:])
    return new_board

def print_board(board):
    print()
    for i in range(8):
        print(8-i," ".join(board[i]))
    print(" a b c d e f g h")
    print()

def can_capture(piece,target):
    if target==".":
        return True
    if piece.isupper() and target.islower():
        return True
    if piece.islower() and target.isupper():
        return True
    return False


def square_under_attack(board,row,col,color):
    opponent="black" if color=="white" else "white"

    for r in range(8):
        for c in range(8):
            piece=board[r][c]
            if piece==".":
                continue
            if opponent=="white" and piece.isupper():
                if can_attack(board,r,c,row,col,piece):
                    return True
            if opponent=="black" and piece.islower():
                if can_attack(board,r,c,row,col,piece):
                    return True
    return False
                



def is_checkmate(board,color):
    if not is_king_in_check(board,color):
        return False
    if has_any_legal_moves(board,color):
        return False

    return True

def is_stalemate(board,color):
    if is_king_in_check(board,color):
        return False
    if has_any_legal_moves(board,color):
        return False
    
    return True
    



def find_king(board,color):
    king_symbol="K" if color=="white" else "k"
    for r in range(8):
        for c in range(8):
            if board[r][c]==king_symbol:
                return r,c
    return None

def can_attack(board,from_row,from_col,to_row,to_col,piece):
    piece_type=piece.upper()
    if piece_type=="P":
        direction=-1 if piece.isupper() else 1
        return(abs(to_col-from_col)==1 and to_row==from_row+direction)
    elif piece_type=="R":
        return is_valid_rook_move(board,from_row,from_col,to_row,to_col,piece)
    elif piece_type=="B":
        return is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece)
    elif piece_type=="N":
        return is_valid_knight_move(board,from_row,from_col,to_row,to_col,piece)
    elif piece_type=="Q":
        return is_valid_queen_move(board,from_row,from_col,to_row,to_col,piece)
    elif piece_type=="K":
        row_diff=abs(to_row-from_row)
        col_diff=abs(to_col-from_col)
        return row_diff<=1 and col_diff<=1
    return False


def has_any_legal_moves(board,color):
    for from_row in range(8):
        for from_col in range(8):
            piece=board[from_row][from_col]
            if piece==".":
                continue
            if color=="white" and piece.islower():
                continue
            if color=="black" and piece.isupper():
                continue

            for to_row in range(8):
                for to_col in range(8):

                    if not is_valid_move(board,from_row,from_col,to_row,to_col,piece):
                        continue
                    if not move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                        return True
    
    return False
            

def is_valid_move(board,from_row,from_col,to_row,to_col,piece):
    piece_type=piece.upper()
    if piece_type=="P":
        return is_valid_pawn_move(board,from_row,from_col,to_row,to_col,piece)
    if piece_type=="R":
        return is_valid_rook_move(board,from_row,from_col,to_row,to_col,piece)
    if piece_type=="B":
        return is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece)
    if piece_type=="N":
        return is_valid_knight_move(board,from_row,from_col,to_row,to_col,piece)
    if piece_type=="Q":
        return is_valid_queen_move(board,from_row,from_col,to_row,to_col,piece)
    if piece_type=="K":
        return is_valid_king_move(board,from_row,from_col,to_row,to_col,piece)
    return False

def is_king_in_check(board,color):
    king_pos=find_king(board,color)
    if not king_pos:
        return False
    
    king_row,king_col=king_pos
    opponent="black" if color=="white" else "white"

    for r in range(8):
        for c in range(8):
            piece=board[r][c]
            if piece==".":
                    continue
            
            if opponent=="white"and piece.isupper():
                if can_attack(board,r,c,king_row,king_col,piece):
                    return True
            if opponent=="black"and piece.islower():
                if can_attack(board,r,c,king_row,king_col,piece):
                    return True
                        
    return False

def move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
    original_from=board[from_row][from_col]
    original_to=board[to_row][to_col]

    board[to_row][to_col]=piece
    board[from_row][from_col]="."

    color="white" if piece.isupper() else "black"
    in_check=is_king_in_check(board,color)

    board[from_row][from_col]=original_from
    board[to_row][to_col]=original_to

    return in_check

def is_valid_pawn_move(board,from_row,from_col,to_row,to_col,piece):
    if not (0<=to_row<8 and 0<=to_col<8):
        return False
    
    direction=-1 if piece.isupper() else 1
    start_row=6 if piece.isupper() else 1
    
    #single forward
    if to_col==from_col and to_row==from_row+direction:
        if board[to_row][to_col]==".":
            return True
        
    #double forward
    if from_row==start_row and to_row==from_row+2*direction and to_col==from_col:
        if board[from_row+direction][from_col]=="." and board[to_row][to_col]==".":
            return True
        
    #diagonal capture
    if abs(to_col-from_col)==1 and to_row==from_row+direction:
        target=board[to_row][to_col]
        if (target)!=".":
            if piece.isupper() and target.islower():
                return True
            if piece.islower() and target.isupper():
                return True
        if(to_row,to_col)==en_passant_target:
            return True
                
               

    return False

def is_valid_rook_move(board,from_row,from_col,to_row,to_col,piece):

    if not(0<=to_row<8 and 0<=to_col<8):
        return False
    if from_row!=to_row and from_col!=to_col:
        return False
    
    row_step=0
    col_step=0

    if to_row>from_row:
        row_step=1
    elif to_row<from_row:
        row_step=-1

    if to_col>from_col:
        col_step=1
    elif to_col<from_col:
        col_step=-1

    current_row=from_row+row_step
    current_col=from_col+col_step

    while(current_row!=to_row or current_col!=to_col):
        if board[current_row][current_col]!=".":
            return False
        current_row+=row_step
        current_col+=col_step

    target=board[to_row][to_col]
    return can_capture(piece, target)
    

def is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece):
    if not(0<=to_row<8 and 0<=to_col<8):
        return False
    
    if abs(to_row-from_row)!=abs(to_col-from_col):
        return False
    
    row_step=1 if to_row>from_row else -1
    col_step=1 if to_col>from_col else -1

    current_row=from_row+row_step
    current_col=from_col+col_step

    while current_row!=to_row:
        if board[current_row][current_col]!=".":
            return False
        current_row+=row_step
        current_col+=col_step

    target=board[to_row][to_col]
    return can_capture(piece, target)

def is_valid_knight_move(board,from_row,from_col,to_row,to_col,piece):
    if not (0<=to_row<8 and 0<=to_col<8):
        return False
    
    row_diff=abs(to_row-from_row)
    col_diff=abs(to_col-from_col)

    if not ((row_diff==2 and col_diff==1)or(row_diff==1 and col_diff==2)):
        return False
    
    target=board[to_row][to_col]
    return can_capture(piece, target)
    
def is_valid_queen_move(board,from_row,from_col,to_row,to_col,piece):
    return is_valid_rook_move(board,from_row,from_col,to_row,to_col,piece) or is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece)
    
def is_valid_king_move(board,from_row,from_col,to_row,to_col,piece):
    global white_king_moved,black_king_moved
    global white_rook_a_moved,white_rook_h_moved
    global black_rook_a_moved,black_rook_h_moved

    if not (0<=to_row<8 and 0<=to_col<8):
        return False
    
    row_diff=abs(to_row-from_row)
    col_diff=abs(to_col-from_col)

    if row_diff<=1 and col_diff<=1:
        if row_diff==0 and col_diff==0:
            return False
        target=board[to_row][to_col]
        return can_capture(piece, target)
    
    if piece.isupper():
        if white_king_moved:
            return False
        if from_row==7 and from_col==4 and to_row==7 and to_col==6:
            if white_rook_h_moved or board[7][7]!="R":
                return False
            if board[7][5]!="." or board[7][6]!=".":
                return False
            if is_king_in_check(board,"white"):
                return False
            if square_under_attack(board,7,5,"white"):
                return False
            if square_under_attack(board,7,6,"white"):
                return False
            return  True
        
        if from_row==7 and from_col==4 and to_row==7 and to_col==2:
            if white_rook_a_moved or board[7][0]!="R":
                return False
            if board[7][1]!="." or board[7][2]!="." or board[7][3]!=".":
                return False
            if is_king_in_check(board,"white"):
                return False
            if square_under_attack(board,7,3,"white"):
                return False
            if square_under_attack(board,7,2,"white"):
                return False
            return True
    else:
        if black_king_moved:
            return False
        if from_row==0 and from_col==4 and to_row==0 and to_col==6:
            if black_rook_h_moved or board[0][7]!="r":
                return False
            if board[0][5]!="." or board[0][6]!=".":
                return False
            if is_king_in_check(board,"black"):
                return False
            if square_under_attack(board,0,5,"black"):
                return False
            if square_under_attack(board,0,6,"black"):
                return False
            return  True
        
        if from_row==0 and from_col==4 and to_row==0 and to_col==2:
            if black_rook_a_moved or board[0][0]!="r":
                return False
            if board[0][1]!="." or board[0][2]!="." or board[0][3]!=".":
                return False
            if is_king_in_check(board,"black"):
                return False
            if square_under_attack(board,0,3,"black"):
                return False
            if square_under_attack(board,0,2,"black"):
                return False
            return True
                        
    return False


def notation_to_index(square):
    file=square[0]
    rank=int(square[1])

    col=ord(file)-ord('a')  
    row=8-rank

    return row,col

def move_piece(board,from_row,from_col,to_row,to_col):
    piece=board[from_row][from_col]
    board[to_row][to_col]=piece
    board[from_row][from_col]="."

def move_piece_notation(board,from_square,to_square):
    global current_turn
    global en_passant_target
   
    from_row,from_col=notation_to_index(from_square)
    to_row,to_col=notation_to_index(to_square)

    piece=board[from_row][from_col]

    if piece==".":
        print("No piece at source square")
        return

    if current_turn=="white" and piece.islower():
        print("It is white's turn")
        return
    if current_turn=="black" and piece.isupper():
        print("It is black's turn")
        return

    if not is_valid_move(board,from_row,from_col,to_row,to_col,piece):
        print("Invalid move")
        return

    if move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                print("Illeagal move: King would be in check")
                return
            
    previous_en_passant=en_passant_target
    move_piece(board,from_row,from_col,to_row,to_col)
    
    if piece.upper()=="P" and (to_row,to_col)==previous_en_passant:
        if piece.isupper():
            board[to_row+1][to_col]="."
        else:
            board[to_row-1][to_col]="."
    en_passant_target=None
    if piece.upper()=="P" and abs(to_row-from_row)==2:
        en_passant_target=((from_row+to_row)//2,from_col)
    if piece =="P" and to_row==0:
        board[to_row][to_col]="Q"
    if piece =="p" and to_row==7:
        board[to_row][to_col]="q"
    if piece.upper()=="K":
        if from_col==4 and to_col==6:
            move_piece(board,from_row,7,from_row,5)
        elif from_col==4 and to_col==2:
            move_piece(board,from_row,0,from_row,3)

    global white_king_moved,black_king_moved
    global white_rook_a_moved,white_rook_h_moved
    global black_rook_a_moved,black_rook_h_moved

    if piece=="K":
        white_king_moved=True
    if piece=="k":
        black_king_moved=True

    if piece=="R":
        if from_row==7 and from_col==0:
            white_rook_a_moved=True
        if from_row==7 and from_col==7:
            white_rook_h_moved=True
    if piece=="r":
        if from_row==0 and from_col==0:
            black_rook_a_moved=True
        if from_row==0 and from_col==7:
            black_rook_h_moved=True
        
            

    current_turn="black" if current_turn=="white" else "white"
    if is_checkmate(board,current_turn):
        print(f"Checkmate! {'white' if current_turn=='black' else 'black'} wins!")
    elif is_stalemate(board,current_turn):
        print("Stalemate! Draw.")
    elif is_king_in_check(board,current_turn):
        print(f"{current_turn} king is in check!")
        




# move_piece_notation(board,"e2","e4")
# print_board(board)

# move_piece_notation(board,"e7","e5")
# print_board(board)

# move_piece_notation(board,"g1","f3")
# print_board(board)

# move_piece_notation(board,"b8","c6")
# print_board(board)

# move_piece_notation(board,"f1","c4")
# print_board(board)

# move_piece_notation(board,"f8","c5")
# print_board(board)

# move_piece_notation(board,"d1","e2")
# print_board(board)

# move_piece_notation(board,"d8","e7")
# print_board(board)

# move_piece_notation(board,"e1","d1")
# print_board(board)

# move_piece_notation(board,"e8","d8")
# print_board(board)

# move_piece_notation(board,"e2","e4")
# move_piece_notation(board,"f7","f6")
# move_piece_notation(board,"d1","h5")



# move_piece_notation(board,"e2","e4")
# move_piece_notation(board,"d8","h4")
# move_piece_notation(board,"a2","a3")

# move_piece_notation(board,"f2","f3")
# move_piece_notation(board,"e7","e5")
# move_piece_notation(board,"g2","g4")
# move_piece_notation(board,"d8","h4")

# move_piece_notation(board,"e2","e4")
# move_piece_notation(board,"e7","e5")

# move_piece_notation(board,"g1","f3")
# move_piece_notation(board,"b8","c6")

# move_piece_notation(board,"f1","e2")
# move_piece_notation(board,"g8","f6")

# move_piece_notation(board,"e1","g1")


move_piece_notation(board,"e2","e4")
move_piece_notation(board,"a7","a6")

move_piece_notation(board,"e4","e5")
move_piece_notation(board,"d7","d5")

move_piece_notation(board,"e5","d6")

print_board(board)

#ajj to
