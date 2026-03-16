import pygame
import engine

WIDTH = 512
HEIGHT = 512
SQ_SIZE = WIDTH // 8

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Engine")

colors = [(240,217,181),(181,136,99)]

IMAGES = {}

move_sound = pygame.mixer.Sound("sounds/move.wav")
capture_sound = pygame.mixer.Sound("sounds/capture.wav")
check_sound = pygame.mixer.Sound("sounds/check.wav")

selected_square = None
legal_moves = []
last_move = None

dragging = False
drag_piece = None
drag_from = None
mouse_x = 0
mouse_y = 0

click_start = None


########################################
# LOAD IMAGES
########################################

def load_images():

    pieces = ["wp","wr","wn","wb","wq","wk","bp","br","bn","bb","bq","bk"]

    for piece in pieces:

        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load("images/"+piece+".png"),
            (SQ_SIZE,SQ_SIZE)
        )


########################################
# DRAW BOARD
########################################

def draw_board():

    for r in range(8):
        for c in range(8):

            color = colors[(r+c)%2]

            pygame.draw.rect(
                screen,
                color,
                (c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE)
            )


########################################
# DRAW PIECES
########################################

def draw_pieces():

    for r in range(8):
        for c in range(8):

            piece = engine.board[r][c]

            if piece != ".":

                if dragging and (r,c)==drag_from:
                    continue

                color = "w" if piece.isupper() else "b"
                key = color + piece.lower()

                screen.blit(IMAGES[key],(c*SQ_SIZE,r*SQ_SIZE))


########################################
# DRAW DRAG PIECE
########################################

def draw_drag_piece():

    if dragging and drag_piece:

        screen.blit(
            IMAGES[drag_piece],
            (mouse_x - SQ_SIZE//2, mouse_y - SQ_SIZE//2)
        )


########################################
# LEGAL MOVES
########################################

def get_legal_moves(row,col):

    moves = engine.generate_all_legal_moves(
        engine.board,
        engine.current_turn
    )

    result=[]

    from_sq = engine.index_to_notation(row,col)

    for move in moves:

        if move[0]==from_sq:

            r,c = engine.notation_to_index(move[1])

            piece = engine.board[row][col]
            target = engine.board[r][c]

            move_type="normal"

            if target!=".":
                move_type="capture"

            if piece.upper()=="K" and abs(c-col)==2:
                move_type="castle"

            if piece.upper()=="P" and (r,c)==engine.en_passant_target:
                move_type="enpassant"

            result.append((r,c,move_type))

    return result


########################################
# DRAW HIGHLIGHTS
########################################

def draw_highlights():

    if last_move:

        start,end = last_move

        pygame.draw.rect(
            screen,(255,255,120),
            (start[1]*SQ_SIZE,start[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        )

        pygame.draw.rect(
            screen,(255,255,120),
            (end[1]*SQ_SIZE,end[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        )


    if selected_square:

        r,c = selected_square

        pygame.draw.rect(
            screen,(0,255,0),
            (c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE),3
        )


    for move in legal_moves:

        r,c,move_type = move

        color=(0,200,0)

        if move_type=="capture":
            color=(220,0,0)

        elif move_type=="castle":
            color=(0,120,255)

        elif move_type=="enpassant":
            color=(180,0,180)

        pygame.draw.rect(
            screen,
            color,
            (c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE),
            3
        )


########################################
# SOUND
########################################

def play_sound(target_piece):

    if target_piece!=".":
        capture_sound.play()
    else:
        move_sound.play()

    if engine.is_king_in_check(engine.board,engine.current_turn):
        check_sound.play()


########################################
# MAIN LOOP
########################################

def main():

    global dragging,drag_piece,drag_from
    global mouse_x,mouse_y
    global selected_square,legal_moves,last_move
    global click_start

    load_images()

    running=True

    while running:

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                running=False


            ################################
            # MOUSE DOWN
            ################################

            if event.type==pygame.MOUSEBUTTONDOWN:

                col=event.pos[0]//SQ_SIZE
                row=event.pos[1]//SQ_SIZE

                piece = engine.board[row][col]

                # CLICK DESTINATION
                if click_start:

                    from_sq = engine.index_to_notation(
                        click_start[0],
                        click_start[1]
                    )

                    to_sq = engine.index_to_notation(row,col)

                    target_piece = engine.board[row][col]

                    engine.move_piece_notation(
                        engine.board,
                        from_sq,
                        to_sq
                    )

                    play_sound(target_piece)

                    last_move=(click_start,(row,col))

                    click_start=None
                    selected_square=None
                    legal_moves=[]

                else:

                    if piece!=".":
                        click_start=(row,col)

                        selected_square=(row,col)
                        legal_moves=get_legal_moves(row,col)

                        dragging=True
                        drag_from=(row,col)

                        color="w" if piece.isupper() else "b"
                        drag_piece=color+piece.lower()


            ################################
            # MOUSE UP (DRAG)
            ################################

            if event.type==pygame.MOUSEBUTTONUP and dragging:

                col=event.pos[0]//SQ_SIZE
                row=event.pos[1]//SQ_SIZE

                from_sq = engine.index_to_notation(
                    drag_from[0],drag_from[1]
                )

                to_sq = engine.index_to_notation(row,col)

                target_piece = engine.board[row][col]

                engine.move_piece_notation(
                    engine.board,
                    from_sq,
                    to_sq
                )

                play_sound(target_piece)

                last_move=(drag_from,(row,col))

                dragging=False
                click_start=None
                selected_square=None
                legal_moves=[]


                ################################
                # ENGINE MOVE
                ################################

                if engine.current_turn=="black":

                    best=engine.iterative_deepening(
                        engine.board,
                        engine.ENGINE_DEPTH
                    )

                    if best:

                        fr,fc=engine.notation_to_index(best[0])
                        tr,tc=engine.notation_to_index(best[1])

                        target_piece = engine.board[tr][tc]

                        engine.move_piece_notation(
                            engine.board,
                            best[0],
                            best[1]
                        )

                        play_sound(target_piece)

                        last_move=((fr,fc),(tr,tc))


            ################################
            # MOUSE MOTION
            ################################

            if event.type==pygame.MOUSEMOTION:

                mouse_x,mouse_y=event.pos


        draw_board()
        draw_highlights()
        draw_pieces()
        draw_drag_piece()

        pygame.display.flip()


if __name__=="__main__":
    main()