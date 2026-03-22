# ♟️ Chess Engine Web App with Stockfish Analysis

A full-stack chess application featuring a custom chess engine, Stockfish integration, and advanced move analysis — similar to chess.com / lichess analysis tools.

---

## 🚀 Features

### 🎮 Game Modes

* Human vs Human
* Human vs Stockfish
* Human vs Custom Engine

---

### 📊 Analysis System

* Move classification:

  * Brilliant 💎
  * Best
  * Excellent
  * Good
  * Inaccuracy
  * Mistake
  * Blunder
* Best move suggestions:

  * Current position
  * Previous move

---

### 📈 Post-Game Insights

* Accuracy system:

  * Accuracy % for both White and Black
  * Blunders, Mistakes, Inaccuracies
* Evaluation graph (Stockfish-based)
* Full move-by-move analysis

---

### 🔁 Game Features

* Undo / Redo with full state restoration
* Save game functionality
* Interactive board (click + drag)
* Sound effects

---

## 🧠 Tech Stack

* **Backend:** Python (Flask)
* **Frontend:** JavaScript (SPA)
* **Engine:** Custom chess engine
* **Analysis:** Stockfish

---

## ⚡ Key Highlights

* Snapshot-based undo/redo system
* Dual evaluation (custom engine vs Stockfish)
* Real-time analysis pipeline
* REST API architecture

---

## 🛠️ Run Locally

```bash
pip install flask
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## 📌 Future Improvements

* Performance optimization (reduce Stockfish calls)
* Multiplayer support
* Cloud save system
* Deployment

---

## 💡 Project Status

> Near complete — minor debugging and performance improvements remaining.

---

## 👤 Author

Sujal Ushir
