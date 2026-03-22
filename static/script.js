let selected = null;
let legalMoves = [];
loadBoard();

// piece symbols
function getImage(piece) {
    if (piece === ".") return null;

    const color = piece === piece.toUpperCase() ? "w" : "b";

    const map = {
        "P": "p",
        "R": "r",
        "N": "n",
        "B": "b",
        "Q": "q",
        "K": "k"
    };

    const type = map[piece.toUpperCase()];

    return `/static/${color}${type}.png`;
}

function loadBoard() {
    fetch("/state")
    .then(res => res.json())
    .then(data => drawBoard(data.board));
}

function drawBoard(board) {
    const boardDiv = document.getElementById("board");
    boardDiv.innerHTML = "";

    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {

            const square = document.createElement("div");
            square.className = "square " + ((r + c) % 2 === 0 ? "white" : "black");

            const notation = indexToNotation(r, c);

            // highlight selected
            if (selected === notation) {
                square.style.border = "3px solid red";
            }

            // highlight legal moves
            if (legalMoves.includes(notation)) {
                const dot = document.createElement("div");
                dot.style.width = "15px";
                dot.style.height = "15px";
                dot.style.background = "green";
                dot.style.borderRadius = "50%";
                square.appendChild(dot);
            }

            const piece = board[r][c];
            if (piece !== ".") {
                const img = document.createElement("img");
                img.src = getImage(piece);
                img.style.width = "50px";
                img.style.height = "50px";
                square.appendChild(img);
            }

            square.onclick = () => handleClick(r, c);

            boardDiv.appendChild(square);

            
        }
    }
}
function handleClick(r, c) {
    const square = indexToNotation(r, c);

    console.log("Clicked:", square);

    // FIRST CLICK → select + fetch moves
    if (!selected) {
        selected = square;

        fetch(`/moves?square=${square}`)
        .then(res => res.json())
        .then(data => {
            legalMoves = data.moves.map(m => m.to);
            loadBoard();
        });

        return;
    }

    // ❌ INVALID CLICK → reset
    if (!legalMoves.includes(square)) {
        selected = null;
        legalMoves = [];
        loadBoard();
        return;
    }

    // ✅ VALID MOVE
    fetch("/move/human", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ from: selected, to: square })
    })
    .then(res => res.json())
    .then(data => {
        console.log("Response:", data);

        if (data.error) {
            alert(data.error);
            selected = null;
            legalMoves = [];
            loadBoard();
            return;
        }

        selected = null;
        legalMoves = [];
        loadBoard();
        engineMove();
    });
}

function engineMove() {
    fetch("/move/engine", { method: "POST" })
    .then(res => res.json())
    .then(() => loadBoard());
}

function resetGame() {
    fetch("/reset", { method: "POST" })
    .then(() => loadBoard());
}

function indexToNotation(r, c) {
    return "abcdefgh"[c] + (8 - r);
}

// initial load
loadBoard();