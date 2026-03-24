"""
Chess Engine — Flask Backend
Run locally:  python app.py
Production:   gunicorn app:app
"""
import copy, traceback, os, json, datetime, threading, logging
from flask import Flask, jsonify, request, render_template, send_from_directory
import engine

# ── Logging (replaces all print statements) ───────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
MATE_SCORE   = -999.99
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_SAVE_PATH   = os.path.join(_PROJECT_DIR, "saved_games.json")
_SOUNDS_DIR  = os.path.join(_PROJECT_DIR, "sounds")
_SF_PATH     = os.path.join(_PROJECT_DIR, "stockfish", "stockfish")

# ── Serve sounds ───────────────────────────────────────────────────────────────
@app.route("/sounds/<path:filename>")
def serve_sound(filename):
    return send_from_directory(_SOUNDS_DIR, filename)

# ── Stockfish init ─────────────────────────────────────────────────────────────
_sf           = None
_sf_lock      = threading.Lock()
STOCKFISH_OK  = False
STOCKFISH_ERR = ""

def _init_stockfish():
    global _sf, STOCKFISH_OK, STOCKFISH_ERR

    if not os.path.exists(_SF_PATH):
        STOCKFISH_ERR = f"Binary not found at {_SF_PATH}"
        log.warning("[Stockfish] %s", STOCKFISH_ERR)
        log.warning("[Stockfish] Place the Linux binary at: stockfish/stockfish")
        return

    if not os.access(_SF_PATH, os.X_OK):
        STOCKFISH_ERR = f"Binary not executable — run: chmod +x {_SF_PATH}"
        log.warning("[Stockfish] %s", STOCKFISH_ERR)
        return

    try:
        from stockfish import Stockfish
        sf = Stockfish(path=_SF_PATH)
        sf.set_depth(12)
        sf.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        move = sf.get_best_move()
        if move:
            _sf = sf
            STOCKFISH_OK = True
            log.info("[Stockfish] Ready — path=%s, test_move=%s", _SF_PATH, move)
    except Exception as e:
        STOCKFISH_ERR = str(e)
        log.warning("[Stockfish] Init failed: %s", e)

_init_stockfish()

# ── Saved-games file: create if missing ──────────────────────────────────────
def _ensure_save_file():
    if not os.path.exists(_SAVE_PATH):
        try:
            with open(_SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
        except OSError:
            log.warning("[SaveGames] Cannot create %s — saves will not persist (ephemeral storage).", _SAVE_PATH)

_ensure_save_file()

# ── Undo / Redo stacks ────────────────────────────────────────────────────────
_undo_stack = []
_redo_stack = []

# ── Move history ──────────────────────────────────────────────────────────────
_move_history = []

# ── Fullmove counter ──────────────────────────────────────────────────────────
_fullmove_counter = 1

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _snap():
    return {
        "board":              copy.deepcopy(engine.board),
        "current_turn":       engine.current_turn,
        "en_passant_target":  engine.en_passant_target,
        "halfmove_clock":     engine.halfmove_clock,
        "white_king_moved":   engine.white_king_moved,
        "black_king_moved":   engine.black_king_moved,
        "white_rook_a_moved": engine.white_rook_a_moved,
        "white_rook_h_moved": engine.white_rook_h_moved,
        "black_rook_a_moved": engine.black_rook_a_moved,
        "black_rook_h_moved": engine.black_rook_h_moved,
    }

def _restore(s):
    engine.board[:]            = s["board"]
    engine.current_turn        = s["current_turn"]
    engine.en_passant_target   = s["en_passant_target"]
    engine.halfmove_clock      = s["halfmove_clock"]
    engine.white_king_moved    = s["white_king_moved"]
    engine.black_king_moved    = s["black_king_moved"]
    engine.white_rook_a_moved  = s["white_rook_a_moved"]
    engine.white_rook_h_moved  = s["white_rook_h_moved"]
    engine.black_rook_a_moved  = s["black_rook_a_moved"]
    engine.black_rook_h_moved  = s["black_rook_h_moved"]

def _snap_full():
    return (_snap(), copy.deepcopy(_move_history))

def _restore_full(entry):
    board_snap, history_snap = entry
    _restore(board_snap)
    _move_history.clear()
    _move_history.extend(history_snap)

def _game_status():
    turn = engine.current_turn
    if engine.is_checkmate(engine.board, turn):
        return {"status": "checkmate", "winner": "black" if turn == "white" else "white"}
    if engine.is_stalemate(engine.board, turn):
        return {"status": "stalemate", "winner": None}
    if engine.halfmove_clock >= 100:
        return {"status": "draw_50_move", "winner": None}
    if _is_insufficient_material():
        return {"status": "draw_material", "winner": None}
    if any(v >= 3 for v in engine.position_history.values()):
        return {"status": "draw_repetition", "winner": None}
    if engine.is_king_in_check(engine.board, turn):
        return {"status": "check", "winner": None}
    return {"status": "ongoing", "winner": None}

def _is_insufficient_material():
    pieces = {}
    for row in engine.board:
        for cell in row:
            if cell != ".":
                pieces[cell] = pieces.get(cell, 0) + 1
    white = {k: v for k, v in pieces.items() if k.isupper() and k != "K"}
    black = {k: v for k, v in pieces.items() if k.islower() and k != "k"}
    def only_minor(d):
        total = sum(d.values())
        if total == 0: return True
        if total == 1 and ("N" in d or "B" in d or "n" in d or "b" in d): return True
        return False
    return only_minor(white) and only_minor(black)

_PIECE_VALUES = {
    "P": 100, "N": 320, "B": 330, "R": 500, "Q": 900,
    "p": 100, "n": 320, "b": 330, "r": 500, "q": 900,
}

def _material_score(board, color):
    total = 0
    for row in board:
        for cell in row:
            if cell == ".": continue
            if color == "white" and cell.isupper() and cell != "K":
                total += _PIECE_VALUES.get(cell, 0)
            elif color == "black" and cell.islower() and cell != "k":
                total += _PIECE_VALUES.get(cell.upper(), 0)
    return total

def _engine_eval():
    try:
        return engine.evaluate_board(engine.board)
    except Exception:
        return 0

def _fen():
    rows = []
    for row in engine.board:
        e, s = 0, ""
        for cell in row:
            if cell == ".":
                e += 1
            else:
                if e: s += str(e); e = 0
                s += cell
        if e: s += str(e)
        rows.append(s)
    t  = "w" if engine.current_turn == "white" else "b"
    ca = ""
    if not engine.white_king_moved:
        if not engine.white_rook_h_moved: ca += "K"
        if not engine.white_rook_a_moved: ca += "Q"
    if not engine.black_king_moved:
        if not engine.black_rook_h_moved: ca += "k"
        if not engine.black_rook_a_moved: ca += "q"
    ca = ca or "-"
    ep = engine.index_to_notation(*engine.en_passant_target) \
         if engine.en_passant_target else "-"
    return f"{'/'.join(rows)} {t} {ca} {ep} {engine.halfmove_clock} {_fullmove_counter}"

def _sf_eval_at_fen(fen_str):
    if not STOCKFISH_OK or _sf is None:
        return None
    try:
        with _sf_lock:
            _sf.set_fen_position(fen_str)
            info = _sf.get_evaluation()
        if not info:
            return None
        side = fen_str.split()[1] if " " in fen_str else "w"
        if info["type"] == "cp":
            cp = info["value"]
            if side == "b": cp = -cp
            return cp
        if info["type"] == "mate":
            sign = 1 if info["value"] > 0 else -1
            if side == "b": sign = -sign
            return sign * 99999
    except Exception:
        pass
    return None

def _sf_eval():
    return _sf_eval_at_fen(_fen())

def _sf_best_move_and_eval(fen_str):
    if not STOCKFISH_OK or _sf is None:
        return None, None
    try:
        with _sf_lock:
            _sf.set_fen_position(fen_str)
            best_uci = _sf.get_best_move()
            if not best_uci or len(best_uci) < 4:
                return None, None
            best_eval = None
            try:
                _sf.set_fen_position(fen_str)
                _sf.make_moves_from_current_position([best_uci])
                info = _sf.get_evaluation()
                if info:
                    side = fen_str.split()[1] if " " in fen_str else "w"
                    if info["type"] == "cp":
                        cp = info["value"]
                        if side == "w": cp = -cp
                        best_eval = cp
                    elif info["type"] == "mate":
                        sign = 1 if info["value"] > 0 else -1
                        if side == "w": sign = -sign
                        best_eval = sign * 99999
            except Exception:
                best_eval = None
        return best_uci[:4], best_eval
    except Exception:
        pass
    return None, None

def _sf_best_move_from_fen(fen_str):
    if not STOCKFISH_OK or _sf is None:
        return None
    try:
        with _sf_lock:
            _sf.set_fen_position(fen_str)
            uci = _sf.get_best_move()
        if uci and len(uci) >= 4:
            return uci[:4]
    except Exception:
        pass
    return None

def _classify_move(eval_before, best_eval, eval_after, moving_color, sacrificed_material=0):
    if best_eval is None or eval_after is None:
        return None
    if moving_color == "white":
        played_val, best_val = eval_after, best_eval
    else:
        played_val, best_val = -eval_after, -best_eval
    delta = best_val - played_val
    if sacrificed_material > 0 and delta <= 30: return "Brilliant"
    if delta <= 20:  return "Best"
    if delta <= 50:  return "Excellent"
    if delta <= 100: return "Good"
    if delta <= 200: return "Inaccuracy"
    if delta <= 400: return "Mistake"
    return "Blunder"

def _is_book_move(move_number, eval_before):
    if eval_before is None:
        return False
    return move_number <= 10 and abs(eval_before) <= 30

def _payload(with_sf=False):
    return {
        "board":          engine.board,
        "current_turn":   engine.current_turn,
        "eval_engine":    _engine_eval(),
        "eval_sf":        _sf_eval() if with_sf else None,
        "can_undo":       len(_undo_stack) > 0,
        "can_redo":       len(_redo_stack) > 0,
        "stockfish_ok":   STOCKFISH_OK,
        **_game_status(),
    }

def _reset_globals():
    global _fullmove_counter
    engine.board[:] = [
        ["r","n","b","q","k","b","n","r"],
        ["p","p","p","p","p","p","p","p"],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        ["P","P","P","P","P","P","P","P"],
        ["R","N","B","Q","K","B","N","R"],
    ]
    engine.current_turn        = "white"
    engine.white_king_moved    = False
    engine.black_king_moved    = False
    engine.white_rook_a_moved  = False
    engine.white_rook_h_moved  = False
    engine.black_rook_a_moved  = False
    engine.black_rook_h_moved  = False
    engine.en_passant_target   = None
    engine.halfmove_clock      = 0
    engine.position_history.clear()
    engine.transposition_table.clear()
    engine.history_heuristic.clear()
    engine.principal_variation_move = None
    engine.killer_moves = [[None, None] for _ in range(50)]
    engine.position_history[engine.hash_board(engine.board, engine.current_turn)] = 1
    _fullmove_counter = 1

def _best_move_from_snap(s):
    saved = _snap()
    _restore(s)
    try:
        moves = engine.generate_all_legal_moves(engine.board, engine.current_turn)
        if not moves:
            return None
        result = engine.iterative_deepening(engine.board, engine.ENGINE_DEPTH)
        if not result or not result[0]:
            return None
        best, _ = result
        return best[0] + best[1]
    except Exception:
        return None
    finally:
        _restore(saved)

def _build_move_review_entry(pre_snap, played_uci, move_number):
    saved = _snap()
    try:
        _restore(pre_snap)
        fen_before   = _fen()
        moving_color = engine.current_turn
        eval_before  = _sf_eval_at_fen(fen_before)
        best_uci, best_eval = _sf_best_move_and_eval(fen_before)

        own_material_before = _material_score(engine.board, moving_color)
        temp_board          = copy.deepcopy(engine.board)
        temp_fr, temp_fc    = engine.notation_to_index(played_uci[:2])
        temp_tr, temp_tc    = engine.notation_to_index(played_uci[2:4])
        _p = temp_board[temp_fr][temp_fc]
        temp_board[temp_tr][temp_tc] = _p
        temp_board[temp_fr][temp_fc] = "."
        sacrificed_material = max(0, own_material_before - _material_score(temp_board, moving_color))

        engine.move_piece_notation(engine.board, played_uci[:2], played_uci[2:4])
        eval_after = _sf_eval_at_fen(_fen())

        classification = _classify_move(eval_before, best_eval, eval_after, moving_color, sacrificed_material)
        if classification not in ("Brilliant", "Best") and _is_book_move(move_number, eval_before):
            classification = "Book"

        return {
            "move_number":         move_number,
            "played":              played_uci,
            "best":                best_uci,
            "eval_before":         round(eval_before / 100, 2) if eval_before is not None else None,
            "eval_after":          round(eval_after  / 100, 2) if eval_after  is not None else None,
            "best_eval":           round(best_eval   / 100, 2) if best_eval   is not None else None,
            "classification":      classification,
            "moving_color":        moving_color,
            "sacrificed_material": sacrificed_material,
            "eval_before_cp":      eval_before,
            "eval_after_cp":       eval_after,
            "best_eval_cp":        best_eval,
        }
    except Exception:
        return {
            "move_number":         move_number,
            "played":              played_uci,
            "best":                None,
            "eval_before":         None,
            "eval_after":          None,
            "best_eval":           None,
            "classification":      None,
            "moving_color":        engine.current_turn,
            "sacrificed_material": 0,
            "eval_before_cp":      None,
            "eval_after_cp":       None,
            "best_eval_cp":        None,
        }
    finally:
        _restore(saved)

def _history_for_client():
    return [
        {
            "move":           e.get("played"),
            "best":           e.get("best"),
            "eval_before":    e.get("eval_before"),
            "eval_after":     e.get("eval_after"),
            "best_eval":      e.get("best_eval"),
            "classification": e.get("classification"),
            "moving_color":   e.get("moving_color", "white"),
            "eval_before_cp": e.get("eval_before_cp"),
            "eval_after_cp":  e.get("eval_after_cp"),
            "best_eval_cp":   e.get("best_eval_cp"),
        }
        for e in _move_history
    ]

def _review_payload(review, played_uci):
    return {
        "move":           played_uci,
        "best":           review["best"],
        "eval_before":    review["eval_before"],
        "eval_after":     review["eval_after"],
        "best_eval":      review["best_eval"],
        "classification": review["classification"],
        "moving_color":   review["moving_color"],
        "eval_before_cp": review["eval_before_cp"],
        "eval_after_cp":  review["eval_after_cp"],
        "best_eval_cp":   review["best_eval_cp"],
    }

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.get("/state")
def get_state():
    return jsonify(_payload(with_sf=False))

@app.get("/eval")
def get_eval():
    return jsonify({"eval_engine": _engine_eval(), "eval_sf": _sf_eval()})

@app.get("/moves")
def legal_moves():
    sq    = request.args.get("square")
    moves = engine.generate_all_legal_moves(engine.board, engine.current_turn)
    if sq:
        moves = [m for m in moves if m[0] == sq]
    return jsonify({"turn": engine.current_turn, "moves": [{"from": f, "to": t} for f, t in moves]})

@app.get("/fen")
def get_fen():
    return jsonify({"fen": _fen()})

@app.get("/best_move")
def best_move_hint():
    try:
        moves = engine.generate_all_legal_moves(engine.board, engine.current_turn)
        if not moves:
            return jsonify({"error": "no legal moves"}), 400
        result = engine.iterative_deepening(engine.board, engine.ENGINE_DEPTH)
        if not result:
            return jsonify({"error": "no move found"}), 500
        best, score = result
        return jsonify({"from": best[0], "to": best[1], "score": score})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.get("/bestmove/current")
def bestmove_current():
    try:
        moves = engine.generate_all_legal_moves(engine.board, engine.current_turn)
        if not moves:
            return jsonify({"engine": None, "stockfish": None})
        eng_best = None
        try:
            result = engine.iterative_deepening(engine.board, engine.ENGINE_DEPTH)
            if result and result[0]:
                eng_best = result[0][0] + result[0][1]
        except Exception:
            pass
        return jsonify({"engine": eng_best, "stockfish": _sf_best_move_from_fen(_fen())})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.get("/bestmove/played")
def bestmove_played():
    try:
        if not _move_history:
            return jsonify({"played": None, "best_engine": None, "best_sf": None, "move_number": 0})
        last    = _move_history[-1]
        snap    = last["snap"]
        best_eng = _best_move_from_snap(snap)
        saved = _snap(); _restore(snap); fen_before = _fen(); _restore(saved)
        return jsonify({
            "played":      last["played"],
            "best_engine": best_eng,
            "best_sf":     _sf_best_move_from_fen(fen_before),
            "move_number": last["move_number"],
        })
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.get("/review")
def get_review():
    try:
        n_param = request.args.get("n")
        entries = _move_history if not n_param else _move_history[-int(n_param):]
        return jsonify([
            {
                "move_number":    e["move_number"],
                "played":         e["played"],
                "best":           e.get("best"),
                "eval_before":    e.get("eval_before"),
                "eval_after":     e.get("eval_after"),
                "best_eval":      e.get("best_eval"),
                "classification": e.get("classification"),
                "moving_color":   e.get("moving_color", "white"),
            }
            for e in entries
        ])
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# ── Move endpoints ────────────────────────────────────────────────────────────

@app.post("/move/human")
def human_move():
    global _fullmove_counter
    d  = request.get_json(force=True)
    fr = d.get("from", "")
    to = d.get("to",   "")
    if not fr or not to:
        return jsonify({"error": "need from+to"}), 400

    r1, c1 = engine.notation_to_index(fr)
    piece  = engine.board[r1][c1]
    if piece == ".":
        return jsonify({"error": "no piece on source square"}), 400
    if engine.current_turn == "white" and piece.islower():
        return jsonify({"error": "it is white's turn"}), 400
    if engine.current_turn == "black" and piece.isupper():
        return jsonify({"error": "it is black's turn"}), 400
    r2, c2 = engine.notation_to_index(to)
    if not engine.is_valid_move(engine.board, r1, c1, r2, c2, piece):
        return jsonify({"error": "invalid move"}), 400
    if engine.move_puts_own_king_in_check(engine.board, r1, c1, r2, c2, piece):
        return jsonify({"error": "move leaves king in check"}), 400

    pre_snap    = _snap()
    move_number = len(_move_history) + 1
    played_uci  = fr + to
    review      = _build_move_review_entry(pre_snap, played_uci, move_number)

    _undo_stack.append(_snap_full())
    _redo_stack.clear()
    engine.move_piece_notation(engine.board, fr, to)
    if engine.current_turn == "white":
        _fullmove_counter += 1

    entry = dict(review); entry["snap"] = pre_snap
    _move_history.append(entry)

    payload = _payload(with_sf=True)
    payload["eval_before_sf"]     = review["eval_before_cp"]
    payload["eval_before_engine"] = _engine_eval()
    payload["move_from"]          = fr
    payload["move_to"]            = to
    payload["review"]             = _review_payload(review, played_uci)
    return jsonify(payload)

@app.post("/move/engine")
def engine_move():
    global _fullmove_counter
    d     = request.get_json(force=True, silent=True) or {}
    depth = int(d.get("depth", engine.ENGINE_DEPTH))
    if not engine.generate_all_legal_moves(engine.board, engine.current_turn):
        return jsonify({"error": "no legal moves"}), 400

    result = engine.iterative_deepening(engine.board, depth)
    if not result:
        return jsonify({"error": "engine found no move"}), 500
    best, _ = result
    fr, to  = best
    played_uci = fr + to

    pre_snap    = _snap()
    move_number = len(_move_history) + 1
    review      = _build_move_review_entry(pre_snap, played_uci, move_number)

    _undo_stack.append(_snap_full())
    _redo_stack.clear()
    engine.move_piece_notation(engine.board, fr, to)
    if engine.current_turn == "white":
        _fullmove_counter += 1

    entry = dict(review); entry["snap"] = pre_snap
    _move_history.append(entry)

    payload = {"engine_move": {"from": fr, "to": to}, **_payload(with_sf=True)}
    payload["eval_before_sf"]     = review["eval_before_cp"]
    payload["eval_before_engine"] = _engine_eval()
    payload["move_from"]          = fr
    payload["move_to"]            = to
    payload["review"]             = _review_payload(review, played_uci)
    return jsonify(payload)

@app.post("/move/stockfish")
def sf_move():
    global _fullmove_counter
    if not STOCKFISH_OK or _sf is None:
        return jsonify({"error": f"Stockfish not available: {STOCKFISH_ERR}"}), 501
    if not engine.generate_all_legal_moves(engine.board, engine.current_turn):
        return jsonify({"error": "no legal moves"}), 400
    try:
        fen_str = _fen()
        with _sf_lock:
            _sf.set_fen_position(fen_str)
            uci = _sf.get_best_move()
        if not uci or len(uci) < 4:
            return jsonify({"error": "Stockfish returned no move"}), 500

        fr, to  = uci[0:2], uci[2:4]
        r1, c1  = engine.notation_to_index(fr)
        r2, c2  = engine.notation_to_index(to)
        piece   = engine.board[r1][c1]
        if piece == ".":
            return jsonify({"error": f"Stockfish picked empty square {fr}"}), 500

        played_uci  = fr + to
        pre_snap    = _snap()
        move_number = len(_move_history) + 1
        review      = _build_move_review_entry(pre_snap, played_uci, move_number)

        _undo_stack.append(_snap_full())
        _redo_stack.clear()
        engine.move_piece_notation(engine.board, fr, to)
        if len(uci) == 5:
            promo = uci[4].upper()
            engine.board[r2][c2] = promo if engine.current_turn == "black" else promo.lower()
        if engine.current_turn == "white":
            _fullmove_counter += 1

        entry = dict(review); entry["snap"] = pre_snap
        _move_history.append(entry)

        payload = {"engine_move": {"from": fr, "to": to}, **_payload(with_sf=True)}
        payload["eval_before_sf"]     = review["eval_before_cp"]
        payload["eval_before_engine"] = _engine_eval()
        payload["move_from"]          = fr
        payload["move_to"]            = to
        payload["review"]             = _review_payload(review, played_uci)
        return jsonify(payload)
    except Exception as ex:
        log.error("[sf_move] %s", traceback.format_exc())
        return jsonify({"error": f"Stockfish error: {str(ex)}"}), 500

# ── Undo / Redo / Reset ───────────────────────────────────────────────────────

@app.post("/undo")
def undo():
    if not _undo_stack:
        return jsonify({"error": "nothing to undo"}), 400
    _redo_stack.append(_snap_full())
    _restore_full(_undo_stack.pop())
    payload = _payload(with_sf=False)
    payload["move_history"] = _history_for_client()
    return jsonify(payload)

@app.post("/redo")
def redo():
    if not _redo_stack:
        return jsonify({"error": "nothing to redo"}), 400
    _undo_stack.append(_snap_full())
    _restore_full(_redo_stack.pop())
    payload = _payload(with_sf=False)
    payload["move_history"] = _history_for_client()
    return jsonify(payload)

@app.post("/reset")
def reset():
    _reset_globals()
    _undo_stack.clear()
    _redo_stack.clear()
    _move_history.clear()
    return jsonify(_payload(with_sf=False))

# ── Eval history + Accuracy ───────────────────────────────────────────────────

@app.get("/eval_history")
def eval_history():
    return jsonify([
        round(e["eval_after"], 2) if e.get("eval_after") is not None else None
        for e in _move_history
    ])

def _compute_side_stats(moves):
    scores = []
    blunders = mistakes = inaccuracies = brilliants = 0
    for e in moves:
        cl = e.get("classification")
        if   cl == "Blunder":    blunders     += 1
        elif cl == "Mistake":    mistakes     += 1
        elif cl == "Inaccuracy": inaccuracies += 1
        elif cl == "Brilliant":  brilliants   += 1
        b, a = e.get("best_eval_cp"), e.get("eval_after_cp")
        if b is not None and a is not None:
            sign  = 1 if e.get("moving_color", "white") == "white" else -1
            delta = max(0, sign * (b - a))
            scores.append(max(0.0, 100.0 - delta / 10.0))
    return {
        "accuracy":     round(sum(scores) / len(scores)) if scores else 100,
        "blunders":     blunders,
        "mistakes":     mistakes,
        "inaccuracies": inaccuracies,
        "brilliants":   brilliants,
        "moves_scored": len(scores),
    }

@app.get("/accuracy")
def get_accuracy():
    white_moves = [e for e in _move_history if e.get("moving_color") == "white"]
    black_moves = [e for e in _move_history if e.get("moving_color") == "black"]
    overall = _compute_side_stats(_move_history)
    return jsonify({
        **{k: overall[k] for k in ("accuracy","blunders","mistakes","inaccuracies","brilliants","moves_scored")},
        "white": _compute_side_stats(white_moves),
        "black": _compute_side_stats(black_moves),
    })

# ── Save game ─────────────────────────────────────────────────────────────────

@app.post("/save_game")
def save_game():
    try:
        body   = request.get_json(force=True, silent=True) or {}
        record = {
            "date":     body.get("date") or datetime.datetime.utcnow().isoformat() + "Z",
            "result":   body.get("result", "?"),
            "moves":    body.get("moves", []),
            "accuracy": body.get("accuracy", {}),
            "review": [
                {
                    "move":           e.get("played"),
                    "best":           e.get("best"),
                    "eval_before":    e.get("eval_before"),
                    "eval_after":     e.get("eval_after"),
                    "best_eval":      e.get("best_eval"),
                    "classification": e.get("classification"),
                    "moving_color":   e.get("moving_color"),
                }
                for e in _move_history
            ],
        }
        games = []
        try:
            with open(_SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    games = data
        except (OSError, json.JSONDecodeError):
            games = []

        games.append(record)
        try:
            with open(_SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(games, f, indent=2, ensure_ascii=False)
        except OSError:
            log.warning("[save_game] Could not write %s — ephemeral storage?", _SAVE_PATH)

        return jsonify({"saved": True, "total_games": len(games)})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# ── Debug endpoint ────────────────────────────────────────────────────────────

@app.get("/debug")
def debug():
    return jsonify({
        "stockfish_ok":     STOCKFISH_OK,
        "stockfish_error":  STOCKFISH_ERR,
        "stockfish_path":   _SF_PATH,
        "save_path":        _SAVE_PATH,
        "sounds_dir":       _SOUNDS_DIR,
        "cwd":              os.getcwd(),
        "move_history_len": len(_move_history),
        "fullmove_counter": _fullmove_counter,
    })

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False)