import pygame
import engine
import time
import copy
import math
promotion_mode=False
promotion_square=None
promotion_choices=["Q","R","B","N"]

mouse_pos=(0,0)


WIDTH = 700
HEIGHT = 512
BOARD_SIZE = 512
SQ_SIZE = BOARD_SIZE // 8

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

move_sound = pygame.mixer.Sound("sounds/move.wav")

LIGHT = (240,217,181)
DARK = (181,136,99)
BG = (30,30,30)
PANEL = (40,40,40)

IMAGES = {}

selected_square=None
legal_moves=[]
last_move=None

dragging=False
drag_piece=None
drag_from=None
mouse_x=0
mouse_y=0

click_start=None
drag_threshold=5

move_log=[]
undo_stack=[]
redo_stack=[]

eval_score=0
display_score=0
pv_line=""
engine_depth=0
engine_thinking=False

game_over=False
game_result=""

hover_square=None

undo_btn = pygame.Rect(520,450,70,30)
redo_btn = pygame.Rect(600,450,70,30)
restart_btn = pygame.Rect(520, 410, 150, 30)

arrow_start=None
preview_arrow=None
arrows=[]

capture_anim=None

sound_on=True
show_highlights=True


def draw_promotion():
    if not promotion_mode:
        return

    r,c = promotion_square

    for i,p in enumerate(promotion_choices):
        rect = pygame.Rect(c*SQ_SIZE, r*SQ_SIZE+i*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen,(50,50,50),rect)

        board_piece = engine.board[r][c]
        piece = ("w"+p.lower()) if board_piece.isupper() else ("b"+p.lower())
        screen.blit(IMAGES[piece],(rect.x,rect.y))


def draw_history():
    font=pygame.font.SysFont(None,18)
    x=530
    y=70

    for i in range(0,len(move_log),2):
        w=move_log[i]
        b=move_log[i+1] if i+1<len(move_log) else ""
        text=f"{i//2+1}. {w} {b}"
        screen.blit(font.render(text,True,(220,220,220)),(x,y))
        y+=18


def draw_settings():
    font=pygame.font.SysFont(None,18)
    screen.blit(font.render(f"[S] Sound: {'ON' if sound_on else 'OFF'}",True,(200,200,200)),(520,400))
    screen.blit(font.render(f"[H] Highlights: {'ON' if show_highlights else 'OFF'}",True,(200,200,200)),(520,420))

def draw_engine_info():
    font=pygame.font.SysFont(None,18)

    y=350

    screen.blit(font.render(f"Eval: {display_score/100:.2f}",True,(200,200,200)),(520,y))
    y+=18
    screen.blit(font.render(f"Depth: {engine_depth}",True,(200,200,200)),(520,y))
    y+=18
    screen.blit(font.render(f"Best: {pv_line}",True,(200,200,200)),(520,y))
    y+=18

    if engine_thinking:
        screen.blit(font.render("Thinking...",True,(255,200,0)),(520,y))


########################################
def load_images():
    pieces=["wp","wr","wn","wb","wq","wk","bp","br","bn","bb","bq","bk"]
    for p in pieces:
        IMAGES[p]=pygame.transform.scale(
            pygame.image.load("images/"+p+".png"),
            (SQ_SIZE,SQ_SIZE)
        )

########################################
def draw_board():
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r+c)%2==0 else DARK
            pygame.draw.rect(screen,color,(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    pygame.draw.rect(screen,(100,100,100),(0,0,512,512),3)

########################################
def draw_hover():
    if hover_square:
        r,c = hover_square
        s = pygame.Surface((SQ_SIZE,SQ_SIZE), pygame.SRCALPHA)
        s.fill((255,255,255,40))
        screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))

########################################
def draw_last_move():
    if not last_move or not show_highlights:
        return
    (sr,sc),(er,ec)=last_move
    s = pygame.Surface((SQ_SIZE,SQ_SIZE), pygame.SRCALPHA)
    s.fill((255,215,0,120))
    screen.blit(s,(sc*SQ_SIZE,sr*SQ_SIZE))
    screen.blit(s,(ec*SQ_SIZE,er*SQ_SIZE))

########################################
def draw_check():
    if not show_highlights:
        return
    for color in ["white","black"]:
        if engine.is_king_in_check(engine.board,color):
            king_pos=engine.find_king(engine.board,color)
            if king_pos:
                r,c=king_pos
                s=pygame.Surface((SQ_SIZE,SQ_SIZE),pygame.SRCALPHA)
                s.fill((255,0,0,120))
                screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))

########################################
def draw_selected():
    if selected_square and show_highlights:
        s = pygame.Surface((SQ_SIZE,SQ_SIZE), pygame.SRCALPHA)
        s.fill((0,0,255,80))
        r,c = selected_square
        screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))

########################################
# ✅ IMPROVED ARROWS
########################################
def draw_arrows():
    for (sr,sc),(er,ec) in arrows:
        start=(sc*SQ_SIZE+SQ_SIZE//2, sr*SQ_SIZE+SQ_SIZE//2)
        end=(ec*SQ_SIZE+SQ_SIZE//2, er*SQ_SIZE+SQ_SIZE//2)

        pygame.draw.line(screen,(220,50,50),start,end,5)

        dx=end[0]-start[0]
        dy=end[1]-start[1]
        angle=math.atan2(dy,dx)

        length=15
        left=(end[0]-length*math.cos(angle-0.5),
              end[1]-length*math.sin(angle-0.5))
        right=(end[0]-length*math.cos(angle+0.5),
               end[1]-length*math.sin(angle+0.5))

        pygame.draw.polygon(screen,(220,50,50),[end,left,right])

    if preview_arrow:
        (sr,sc),(er,ec)=preview_arrow
        start=(sc*SQ_SIZE+32,sr*SQ_SIZE+32)
        end=(ec*SQ_SIZE+32,er*SQ_SIZE+32)
        pygame.draw.line(screen,(0,255,0),start,end,3)

########################################
def draw_capture_anim():
    global capture_anim
    if not capture_anim:
        return

    r,c,alpha=capture_anim
    s=pygame.Surface((SQ_SIZE,SQ_SIZE),pygame.SRCALPHA)
    s.fill((255,0,0,alpha))
    screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))

    capture_anim=(r,c,alpha-15)
    if capture_anim[2]<=0:
        capture_anim=None

########################################
def draw_pieces():
    for r in range(8):
        for c in range(8):
            piece=engine.board[r][c]
            if piece!=".":
                if dragging and (r,c)==drag_from:
                    continue
                key=("w" if piece.isupper() else "b")+piece.lower()
                screen.blit(IMAGES[key],(c*SQ_SIZE,r*SQ_SIZE))

########################################
def draw_drag_piece():
    if dragging and drag_piece:
        screen.blit(IMAGES[drag_piece],
                    (mouse_x - SQ_SIZE//2 + 2, mouse_y - SQ_SIZE//2 + 2))

########################################
def animate(fr,fc,tr,tc,key):
    sx,sy=fc*SQ_SIZE,fr*SQ_SIZE
    ex,ey=tc*SQ_SIZE,tr*SQ_SIZE
    frames = 20

    for i in range(1,frames+1):
        t=i/frames
        t = t*t*(3-2*t)

        x=sx+(ex-sx)*t
        y=sy+(ey-sy)*t

        draw_board()
        draw_hover()
        draw_last_move()
        draw_arrows()
        draw_selected()
        draw_highlights()
        draw_check()
        draw_pieces()
        screen.blit(IMAGES[key],(x,y))
        draw_panel()

        pygame.display.flip()
        pygame.time.delay(8)

########################################
def get_legal_moves(row,col):
    moves=engine.generate_all_legal_moves(engine.board,engine.current_turn)
    res=[]
    fs=engine.index_to_notation(row,col)

    for m in moves:
        if m[0]==fs:
            r,c=engine.notation_to_index(m[1])
            piece=engine.board[row][col]
            target=engine.board[r][c]

            t="normal"
            if target!=".": t="capture"
            if piece.upper()=="K" and abs(c-col)==2: t="castle"
            if piece.upper()=="P" and (r,c)==engine.en_passant_target: t="enpassant"

            res.append((r,c,t))
    return res

########################################
def draw_highlights():
    if not show_highlights:
        return
    for r,c,t in legal_moves:
        cx=c*SQ_SIZE+32
        cy=r*SQ_SIZE+32

        if t=="normal":
            pygame.draw.circle(screen,(0,200,0),(cx,cy),7)
        elif t=="capture":
            pygame.draw.circle(screen,(0,200,0),(cx,cy),26,4)
        elif t=="castle":
            pygame.draw.circle(screen,(180,0,255),(cx,cy),26,4)
        elif t=="enpassant":
            pygame.draw.circle(screen,(0,120,255),(cx,cy),26,4)

########################################
def update_eval():
    global eval_score
    eval_score = engine.evaluate_board(engine.board)

def draw_eval():
    global display_score
    display_score+=(eval_score-display_score)*0.1

    score=max(-10,min(10,display_score/100))
    percent=(score+10)/20
    h=int(percent*BOARD_SIZE)

    pygame.draw.rect(screen,(60,60,60),(512,0,10,BOARD_SIZE))
    pygame.draw.rect(screen,(255,255,255),(512,BOARD_SIZE-h,10,h))

    font = pygame.font.SysFont(None,20)
    text = f"{display_score/100:.2f}"
    screen.blit(font.render(text,True,(255,255,255)),(525,10))

########################################
def draw_buttons():
    font=pygame.font.SysFont(None,18)

    pygame.draw.rect(screen,(120,60,60),restart_btn)
    screen.blit(font.render("Restart",True,(255,255,255)),(restart_btn.x+40,restart_btn.y+5))

    pygame.draw.rect(screen,(80,80,80),undo_btn)
    pygame.draw.rect(screen,(80,80,80),redo_btn)

    screen.blit(font.render("Undo",True,(255,255,255)),(undo_btn.x+10,undo_btn.y+5))
    screen.blit(font.render("Redo",True,(255,255,255)),(redo_btn.x+10,redo_btn.y+5))


########################################
def draw_turn():
    font = pygame.font.SysFont(None,24)
    turn_text = "White to move" if engine.current_turn=="white" else "Black to move"
    screen.blit(font.render(turn_text,True,(255,255,255)),(520,30))

########################################
def draw_game_over():
    if not game_over:
        return
    font=pygame.font.SysFont(None,40)
    s=pygame.Surface((BOARD_SIZE,BOARD_SIZE),pygame.SRCALPHA)
    s.fill((0,0,0,180))
    screen.blit(s,(0,0))
    text=font.render(game_result,True,(255,255,255))
    screen.blit(text,(120,220))

########################################
def draw_panel():
    pygame.draw.rect(screen,PANEL,(512,0,188,HEIGHT))
    draw_eval()
    draw_buttons()
    draw_turn()
    draw_history()
    draw_settings()
    draw_engine_info()

########################################
def engine_move():
    global eval_score,pv_line,last_move,game_over,game_result
    global engine_depth,engine_thinking

    pygame.display.flip()
    time.sleep(0.2)

    engine_thinking=True
    pygame.display.flip()

    best,score=engine.iterative_deepening(engine.board,engine.ENGINE_DEPTH)

    engine_thinking=False
    engine_depth=engine.ENGINE_DEPTH
    eval_score=score

    if best:
        fr,fc=engine.notation_to_index(best[0])
        tr,tc=engine.notation_to_index(best[1])

        piece=engine.board[fr][fc]
        key=("w" if piece.isupper() else "b")+piece.lower()

        animate(fr,fc,tr,tc,key)

        undo_stack.append((copy.deepcopy(engine.board),move_log.copy()))

        engine.move_piece_notation(engine.board,best[0],best[1])
        move_log.append(best[0]+best[1])

        if sound_on:
            move_sound.play()

        last_move=((fr,fc),(tr,tc))
        arrows.clear()   # ✅ CLEAR AFTER MOVE

        pv_line=best[0]+best[1]

        update_eval()

        if engine.is_checkmate(engine.board,engine.current_turn):
            game_over=True
            game_result="Checkmate!"
        elif engine.is_stalemate(engine.board,engine.current_turn):
            game_over=True
            game_result="Stalemate!"

########################################
def main():
    global dragging,drag_piece,drag_from
    global mouse_x,mouse_y,hover_square
    global selected_square,legal_moves
    global eval_score,pv_line,click_start,last_move,display_score
    global game_over
    global arrow_start,preview_arrow
    global capture_anim
    global sound_on,show_highlights
    global promotion_mode,promotion_square
    global mouse_pos

    load_images()
    running=True

    while running:

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                running=False

            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_s:
                    sound_on = not sound_on
                if event.key==pygame.K_h:
                    show_highlights = not show_highlights

            if event.type==pygame.MOUSEBUTTONDOWN:
                if promotion_mode:
                    mx,my = event.pos
                    r,c = promotion_square

                    for i,p in enumerate(promotion_choices):
                        rect = pygame.Rect(c*SQ_SIZE, r*SQ_SIZE+i*SQ_SIZE, SQ_SIZE, SQ_SIZE)
                        if rect.collidepoint(mx,my):
                            piece = engine.board[r][c]
                            engine.board[r][c] = p if piece.isupper() else p.lower()
                            promotion_mode=False
                    continue

                if event.button == 3:
                    col=event.pos[0]//SQ_SIZE
                    row=event.pos[1]//SQ_SIZE
                    arrow_start=(row,col)

                elif restart_btn.collidepoint(event.pos):
                    engine.board = engine.get_initial_board()
                    engine.current_turn = "white"

                    move_log.clear()
                    undo_stack.clear()
                    redo_stack.clear()

                    selected_square=None
                    legal_moves.clear()
                    arrows.clear()

                    game_over=False
                    game_result=""

                    update_eval()

                    last_move=None
                    promotion_mode=False
                    capture_anim=None
                    pv_line=""
                    engine_depth=0
                    engine_thinking=False
                    display_score=0
                    hover_square=None
                    arrow_start=None
                    preview_arrow=None


                elif undo_btn.collidepoint(event.pos):
                    if undo_stack:
                        redo_stack.append((copy.deepcopy(engine.board),move_log.copy()))
                        engine.board,move_log[:] = undo_stack.pop()
                        engine.current_turn = "white" if len(move_log)%2==0 else "black"
                        update_eval()

                elif redo_btn.collidepoint(event.pos):
                    if redo_stack:
                        undo_stack.append((copy.deepcopy(engine.board),move_log.copy()))
                        engine.board,move_log[:] = redo_stack.pop()
                        engine.current_turn = "white" if len(move_log)%2==0 else "black"
                        update_eval()

                else:
                    col=event.pos[0]//SQ_SIZE
                    row=event.pos[1]//SQ_SIZE

                    if 0<=row<8 and 0<=col<8:
                        piece=engine.board[row][col]

                        if selected_square and (row,col) in [(m[0],m[1]) for m in legal_moves]:

                            target_piece = engine.board[row][col]
                            if target_piece != ".":
                                capture_anim = (row,col,120)

                            undo_stack.append((copy.deepcopy(engine.board),move_log.copy()))

                            fs=engine.index_to_notation(selected_square[0],selected_square[1])
                            ts=engine.index_to_notation(row,col)

                            engine.move_piece_notation(engine.board,fs,ts)
                            move_log.append(fs+ts)

                            if sound_on:
                                move_sound.play()

                            last_move=((selected_square[0],selected_square[1]),(row,col))
                            arrows.clear()   # ✅ CLEAR AFTER MOVE

                            piece = engine.board[row][col]
                            if piece.upper()=="P" and (row==0 or row==7):
                                promotion_mode=True
                                promotion_square=(row,col)

                            selected_square=None
                            legal_moves=[]

                            update_eval()

                            if engine.current_turn=="black":
                                engine_move()

                        elif piece!="." and piece.isupper():
                            selected_square=(row,col)
                            legal_moves=get_legal_moves(row,col)

                            drag_from=(row,col)
                            drag_piece="w"+piece.lower()
                            click_start=event.pos
                        else:
                            selected_square=None
                            legal_moves=[]

            if event.type==pygame.MOUSEMOTION:
                mouse_pos = event.pos
                mouse_x,mouse_y=event.pos

                col = mouse_x // SQ_SIZE
                row = mouse_y // SQ_SIZE

                if 0 <= row < 8 and 0 <= col < 8:
                    hover_square = (row, col)
                else:
                    hover_square = None

                if arrow_start:
                    preview_arrow=(arrow_start,(row,col))

                if drag_piece and click_start:
                    if (abs(mouse_x-click_start[0])>drag_threshold or 
                        abs(mouse_y-click_start[1])>drag_threshold):
                        dragging=True

            if event.type==pygame.MOUSEBUTTONUP:

                if event.button == 3 and arrow_start:
                    col=event.pos[0]//SQ_SIZE
                    row=event.pos[1]//SQ_SIZE
                    arrows.append((arrow_start,(row,col)))
                    arrow_start=None
                    preview_arrow=None

                if dragging:
                    col=event.pos[0]//SQ_SIZE
                    row=event.pos[1]//SQ_SIZE

                    if not (0<=row<8 and 0<=col<8):
                        dragging=False
                        drag_piece=None
                        drag_from=None
                        click_start=None
                        continue

                    if (row,col) in [(m[0],m[1]) for m in legal_moves]:

                        target_piece = engine.board[row][col]
                        if target_piece != ".":
                            capture_anim = (row,col,120)

                        undo_stack.append((copy.deepcopy(engine.board),move_log.copy()))

                        fs=engine.index_to_notation(drag_from[0],drag_from[1])
                        ts=engine.index_to_notation(row,col)

                        engine.move_piece_notation(engine.board,fs,ts)
                        move_log.append(fs+ts)

                        if sound_on:
                            move_sound.play()

                        last_move=((drag_from[0],drag_from[1]),(row,col))
                        arrows.clear()   # ✅ CLEAR AFTER MOVE

                        piece = engine.board[row][col]
                        if piece.upper()=="P" and (row==0 or row==7):
                            promotion_mode=True
                            promotion_square=(row,col)

                        selected_square=None
                        legal_moves=[]

                        update_eval()

                        if engine.current_turn=="black":
                            engine_move()

                dragging=False
                drag_piece=None
                drag_from=None
                click_start=None

        screen.fill(BG)

        draw_board()
        draw_hover()
        draw_last_move()
        draw_arrows()
        draw_selected()
        draw_highlights()
        draw_check()
        draw_pieces()
        draw_capture_anim()
        draw_drag_piece()
        draw_panel()
        draw_game_over()
        draw_promotion()

        pygame.display.flip()

if __name__=="__main__":
    main()