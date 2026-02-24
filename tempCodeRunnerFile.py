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
    from_row,from_col=notation_to_index(from_square)
    to_row,to_col=notation_to_index(to_square)
    
    move_piece(board,from_row,from_col,to_row,to_col)


move_piece(board,7,6,5,5)
for  row in board:
    print(" ".join(row))

move_piece_notation(board,"e2","e4")
for  row in board:
    print(" ".join(row))




