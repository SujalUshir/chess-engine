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

def print_board(board):
    print()
    for i in range(8):
        print(8-i," ".join(board[i]))
    print(" a b c d e f g h")
    print()



def find_king(board,color):
    king_symbol="K" if color=="white" else "k"
    for r in range(8):
        for c in range(8):
            if board[r][c]==king_symbol:
                return r,c
    return None

def can_attack(board,from_row,from_col,to_row,to_col,piece):
    if piece.upper()=="P":
        direction=-1 if piece.isupper() else 1
        if(abs(to_col-from_col)==1 and to_row==from_row+direction):
            return True
        return False
    if piece.upper()=="R":
        return is_valid_rook_move(board,from_row,from_col,to_row,to_col,piece)
    if piece.upper()=="B":
        return is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece)
    if piece.upper()=="N":
        return is_valid_knight_move(board,from_row,from_col,to_row,to_col,piece)
    if piece.upper()=="Q":
        return is_valid_queen_move(board,from_row,from_col,to_row,to_col,piece)
    if piece.upper()=="K":
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

    if target==".":
        return True
    if piece.isupper() and target.islower():
        return True
    if piece.islower() and target.isupper():
        return True
    
    return False

def is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece):
    if not(0<=to_row<8 and 0<=to_col<8):
        return False
    
    if abs(to_row-from_row)!=abs(to_col-from_col):
        return False
    
    row_step=1 if to_row>from_row else -1
    col_step=1 if to_col>from_col else -1

    current_row=from_row+row_step
    current_col=from_col+col_step

    while current_row!=to_row :
        if board[current_row][current_col]!=".":
            return False
        current_row+=row_step
        current_col+=col_step

    target=board[to_row][to_col]

    if target==".":
        return True
    
    if piece.isupper() and target.islower():
        return True
    if piece.islower() and target.isupper():
        return True
    return False

def is_valid_knight_move(board,from_row,from_col,to_row,to_col,piece):
    if not (0<=to_row<8 and 0<=to_col<8):
        return False
    
    row_diff=abs(to_row-from_row)
    col_diff=abs(to_col-from_col)

    if not ((row_diff==2 and col_diff==1)or(row_diff==1 and col_diff==2)):
        return False
    
    target=board[to_row][to_col]

    if target==".":
        return True
    
    if piece.isupper() and target.islower():
        return True
    if piece.islower() and target.isupper():
        return True
    return False
    
def is_valid_queen_move(board,from_row,from_col,to_row,to_col,piece):
    if is_valid_rook_move(board,from_row,from_col,to_row,to_col,piece):
        return True
    if is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece):
        return True
    return False
    
def is_valid_king_move(board,from_row,from_col,to_row,to_col,piece):
    if not (0<=to_row<8 and 0<=to_col<8):
        return False
    
    row_diff=abs(to_row-from_row)
    col_diff=abs(to_col-from_col)

    if row_diff<=1 and col_diff<=1:
        if row_diff==0 and col_diff==0:
            return False
        target=board[to_row][to_col]

        if target==".":
            return True
        
        if piece.isupper() and target.islower():
            return True
        if piece.islower() and target.isupper():
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

    if piece.upper()=="P":
        if is_valid_pawn_move(board,from_row,from_col,to_row,to_col,piece):
            if move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                print("Illeagal move: King would be in check")
                return
            
            move_piece(board,from_row,from_col,to_row,to_col)

            current_turn="black" if current_turn=="white" else "white"
            if is_king_in_check(board,current_turn):
                print(f"{current_turn} king is in check!")
        else:
            print("Invalid pawn move")
    elif piece.upper()=="R":
        if is_valid_rook_move(board,from_row,from_col,to_row,to_col,piece):
            if move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                print("Illeagal move: King would be in check")
                return
            move_piece(board,from_row,from_col,to_row,to_col)
            current_turn ="black" if current_turn=="white" else "white"
            if is_king_in_check(board,current_turn):
                print(f"{current_turn} king is in check!")
        else:
            print("Invalid rook move")
    elif piece.upper()=="B":
        if is_valid_bishop_move(board,from_row,from_col,to_row,to_col,piece):
            if move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                print("Illeagal move: King would be in check")
                return
            move_piece(board,from_row,from_col,to_row,to_col)
            current_turn ="black" if current_turn=="white" else "white"
            if is_king_in_check(board,current_turn):
                print(f"{current_turn} king is in check!")
        else:
            print("Invalid bishop move")

    elif piece.upper()=="N":
        if is_valid_knight_move(board,from_row,from_col,to_row,to_col,piece):
            if move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                print("Illeagal move: King would be in check")
                return
            move_piece(board,from_row,from_col,to_row,to_col)
            current_turn ="black" if current_turn=="white" else "white"
            if is_king_in_check(board,current_turn):
                print(f"{current_turn} king is in check!")
        else:
            print("Invalid knight move")
    elif piece.upper()=="Q":
        if is_valid_queen_move(board,from_row,from_col,to_row,to_col,piece):
            if move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                print("Illeagal move: King would be in check")
                return
            move_piece(board,from_row,from_col,to_row,to_col)
            current_turn ="black" if current_turn=="white" else "white"
            if is_king_in_check(board,current_turn):
                print(f"{current_turn} king is in check!")
        else:
            print("Invalid queen move")
    elif piece.upper()=="K":
        if is_valid_king_move(board,from_row,from_col,to_row,to_col,piece):
            if move_puts_own_king_in_check(board,from_row,from_col,to_row,to_col,piece):
                print("Illeagal move: King would be in check")
                return
            move_piece(board,from_row,from_col,to_row,to_col)
            current_turn ="black" if current_turn=="white" else "white"
            if is_king_in_check(board,current_turn):
                print(f"{current_turn} king is in check!")
        else:
            print("Invalid king move")

    else:
        print("Piece validation is not implemented yet.")

    




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



move_piece_notation(board,"e2","e4")
move_piece_notation(board,"d8","h4")
move_piece_notation(board,"a2","a3")















