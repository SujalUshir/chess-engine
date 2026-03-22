# ♟️ Chess Engine Web App with Stockfish Analysis

## 🔗 Live Demo (Coming Soon)

A full-stack chess application featuring a custom chess engine, Stockfish integration, and advanced move analysis — inspired by platforms like chess.com and lichess.

---

## 📸 Screenshots

### 🏠 Home Screen

![Home](screenshots/home.png)

### ♟️ Gameplay (Human vs Human)

![Game](screenshots/game.png)

### 🤖 Gameplay with Analysis (Stockfish)

![Analysis](screenshots/analysis.png)

### 🎯 Game Setup & Mode Selection

![Summary](screenshots/summary.png)

### ⚙️ Settings Panel

![Settings](screenshots/settings.png)

### 📖 Project Info Page (Features Overview)

![Info Features](screenshots/info-features.png)

### 🧠 Technologies & Architecture Overview

![Info Tech](screenshots/info-tech.png)

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
* Interactive board UI
* Sound effects

---

## 🧠 Tech Stack

* **Backend:** Python (Flask)
* **Frontend:** JavaScript (SPA)
* **Engine:** Custom chess engine
* **Analysis:** Stockfish

---

## 🏗️ Architecture

* Frontend (JavaScript SPA) communicates with backend via REST API
* Backend (Flask) handles:

  * Move validation
  * Game state management
  * Engine evaluation
  * Stockfish integration
* Move history stores:

  * evaluation before/after
  * best move
  * classification
* Snapshot-based system used for undo/redo

---

## ⚠️ Stockfish Setup

Stockfish binary is **not included** in this repository.

### Steps:

1. Download Stockfish from:
   https://stockfishchess.org/download/

2. Place the executable in the project root directory

3. Ensure your backend points to the correct path:

```python
STOCKFISH_PATH = "stockfish.exe"
```

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
