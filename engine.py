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
# for row in board:
#     print(row)

# for row in board:
#     print("This row is",row)

# for i in range(8):
#     print("Row Number:",i,"is",board[i])

current_turn="white"




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
            move_piece(board,from_row,from_col,to_row,to_col)

            current_turn="black" if current_turn=="white" else "white"
        else:
            print("Invalid pawn move")
    else:
        print("Only white pawn validation implemented")


# move_piece(board,7,6,5,5)
for  row in board:
    print(" ".join(row))

move_piece_notation(board,"e2","e4")
for  row in board:
    print(" ".join(row))


move_piece_notation(board,"d7","d5")
for  row in board:
    print(" ".join(row))


move_piece_notation(board,"e4","d5")
for  row in board:
    print(" ".join(row))




