# Minesweeper System Design Summary

## Purpose

This project is a browser-based Minesweeper game implemented in TypeScript. The player selects a mine count, reveals safe cells, flags suspected mines, and starts a new game after a win or loss. 

The new enhanced system supports Normal mode with a timer, Easy AI, Medium AI, Hard AI, Basic Self-Solving mode, and Advanced Self-Solving mode. Project 2 extends the original system with multiple new AI features and a high-score tracking timer for Normal mode. 

## Architecture

```mermaid
flowchart TD
    HTML[index.html] --> Main[src/main.ts]
    Main --> UI[src/ui.ts]

    UI --> DOM[Browser DOM]
    UI --> Canvas[Canvas 2D win animation]
    UI -->|reveal / flag| Game[src/game.ts<br/>game engine]
    UI -->|Easy, Medium, or Hard mode| Turn[Turn controller in ui.ts<br/>AI_MOVES table + 1s delay]
    UI -->|Self-solving mode| Solver[Self-solver loop in ui.ts<br/>one move every 0.5s]
    UI -->|start / finish| Timer[src/new_suggestion/<br/>timerHighScore.ts]

    Turn -->|one move per turn| AI[AI solver in src/game.ts<br/>Easy + Medium + Hard]
    Solver -->|makeBasicSelfSolvingMove| AI
    AI -->|revealCell / toggleFlag| Game
    Timer -->|best time per mine count| Storage[(Browser localStorage)]

    Game --> Types[src/types.ts]
    UI --> Types

    classDef added fill:#fff4e5,stroke:#f59e0b,color:#111;
    class Turn,Solver,AI,Timer,Storage added;
```

Orange boxes were added in Project 2.

- `index.html` provides the application root and loads the compiled entry point.
- `src/main.ts` starts the application by rendering the start screen, then passes the chosen mine count and game mode to the game screen.
- `src/ui.ts` owns screen rendering, browser events, board-cell interaction, HUD updates, and the win animation. The start screen has a game mode dropdown (Normal, Easy AI, Medium AI, Hard AI, Basic Self-Solving).
- **Turn controller** (inside `src/ui.ts`): in an AI mode, it waits one second after each player move, then calls the AI move function for the selected mode from the `AI_MOVES` table. The board is locked while the AI move is pending, and starting a new game cancels it. Adding a new difficulty only needs one new entry in `AI_MOVES` and one dropdown option.
- **Self-solver loop** (inside `src/ui.ts`): in Basic Self-Solving mode, the computer plays the whole game alone. It calls `makeBasicSelfSolvingMove` every half second until the game is won or lost, and player clicks are ignored. A pending move is cancelled when a new game starts.
- **AI solver** (inside `src/game.ts`): `makeEasyAIMove`, `makeMediumAIMove`, and `makeHardAIMove` each make exactly one move per call. Easy reveals a random covered cell, never picking a flagged or already revealed one. Medium applies the two basic rules (flag all hidden neighbors when they must all be mines, open the rest when a number's flags are satisfied) and otherwise clicks a random covered cell. Hard adds the 1-2-1 pattern rule before falling back to a random click. `makeBasicSelfSolvingMove` reuses the Easy logic. The AI only reads what a player can see (cell state and numbers), never `isMine`, and acts through the same `revealCell` and `toggleFlag` functions the player uses.
- `src/game.ts` owns board creation, mine placement, adjacent-mine counts, revealing, flagging, win detection, and loss handling.
- `src/new_suggestion/timerHighScore.ts` is the custom addition. It starts the clock on the first reveal, freezes it on a win or loss, and saves the fastest winning time for each mine count in the browser's `localStorage`. The HUD shows the current time and the best time. Its UML diagram is in `src/new_suggestion/documents_uml/minesweeper_addition_uml.pdf`.
- `src/types.ts` defines shared constants, data structures, coordinate helpers, and bounds checking.
- `style.css` supplies the visual design and responsive board layout.
- Tests: `src/game.test.ts` covers the game rules and the AI levels, and `src/new_suggestion/timerHighScore.test.ts` covers the timer and high scores.

## Data Model

A `Board` contains:

```text
Board {
  cells: Cell[][]
  rows: number
  cols: number
  mineCount: number
  gameStatus: 'ready' | 'playing' | 'won' | 'lost'
}
```

Each `Cell` contains:

```text
Cell {
  isMine: boolean
  adjacentMines: number
  state: 'covered' | 'flagged' | 'revealed'
}
```

Coordinates are zero-indexed internally. The UI renders a 10-by-10 board, with columns A-J and rows 1-10 for player-facing labels.

### Key Data Structures - Additions

**1. Game Modes and AI Move Mapping**   
The `GameMode` type in `src/ui.ts` identifies the selected game mode: Normal, Easy AI, Medium AI, Hard AI, Basic Self-Solving, or Advanced Self-Solving.
The `AI_MOVES` record maps each interactive AI mode to the correct move function. This allows the UI to use the right AI strategy and promotes reusability by preventing a separate turn control for each type.

**2. AI Medium and Hard Sets**   
The AI logic in `src/game.ts` uses two sets of strings to track cells for medium and hard AI interactive modes:
- **Mine set (`Set<string>`):** Stores coordinates of cells the AI has determined are mines.
- **Safe-cell set (`Set<string>`):** Stores the coordinates of cells that AI determined are safe.

**3. Candidate Cell Lists**     
The AI uses arrays of row-and-column coordinate pairs (`Array<[number, number]>`), to store covered cells. This allows modes, such as Easy-AI, to keep track of which cells may be selected.

**4. AI Turn and Self-Solver Control**    
The UI uses the `aiControl` object with a pending timer and a Boolean to show whether an AI move is waiting to execute. This disallows a player to move while an interactive AI turn is pending. 

**5. Timer and High-Score Data**    
The custom timer feature is managed by `TimerHighScoreController` in `src/new_suggestion/timerHighScore.ts`. The UI uses a `TimerSnapshot` that uses the elapsed time, the best recorded time (or `null` if no record exists), and a Boolean to show whether the current result is a new best score. This feature operates in Normal mode and stores the winning time in `localStorage` to allow records to remain in the browser for each mine count.

## Interface Description - with additions
### User Input   
The user interacts through the browser-based interface, which is implemented in `src/ui.ts`.
- Game Setup: The player will select a mine count from 10 to 20 using the slider and then choose one of the six available game modes using the dropdown selector.
- Cell Revealing: In Normal mode, the player can left-click to reveal a covered cell. In the interactive AI modes, the player and AI alternate turns. This means when it is the AI's turn, the user may not reveal a cell. Also, in the self-solving modes, the user cannot change or click the board.
- Flagging: In Normal mode, the player may right-click to flag a covered cell or remove a flag. Flagging is disabled in the other modes.
- Self-Solving Modes: In Basic and Advanced Self-Solving modes, the computer performs moves automatically.
- New Game: The New Game button cancels pending AI or self-solver moves, disposes of the timer in Normal mode, and returns the player to the start screen.
### User Interface
The user interface displays the board state and provides feedback to the user. The following is related to the new modes developed:
- **Game Mode Selector:** Adds a dropdown to the start screen with six options.
- **Interactive AI Modes:** Displays the selected AI difficulty and allows alternating player and AI turns.
- **Timer and High Scores:** In Normal mode, shows the elapsed game time and the best recorded winning time for the selected mine count.
- **AI Result Messages:** Displays the winner or loss message when an interactive AI game ends or a self-solving attempt fails.

These additions extend the original interface while allowing the original controls and game board to stay.

### Component Interfaces
The system components communicate through imported functions and shared callbacks.
- `main.ts` and `ui.ts`: `main.ts` calls `renderStartScreen()` to display the initial screen. The callback passes the selected mine count and game mode to `renderGameScreen()` to initialize the appropriate mode.
- 

## Game Flow

1. `renderStartScreen` displays the mine-count slider from 10 through 20.
2. Starting a game calls `createGame`, which creates an empty 10-by-10 board in `ready` status.
3. The first `revealCell` call places mines randomly while excluding the clicked cell and its surrounding eight-cell safe area.
4. Mine placement increments `adjacentMines` on neighboring cells and changes the board to `playing`.
5. Revealing a safe zero-count cell performs an iterative flood reveal of neighboring safe cells.
6. Revealing a mine reveals every mine and changes the board to `lost`.
7. Revealing every non-mine cell changes the board to `won` and flags remaining mines.
8. Right-clicking a covered cell toggles its flag. The number of flags cannot exceed `mineCount`.
9. After every action, the UI rerenders the board and displays `mineCount - flaggedCount` as the remaining-mine counter.
10. The New Game button returns the player to the configuration screen.

## State Rules

- `ready`: mines have not been generated; the first reveal initializes the board.
- `playing`: the player can reveal and flag cells.
- `won`: all safe cells are revealed; further actions are ignored.
- `lost`: a mine was revealed; further actions are ignored.
- A revealed cell cannot be flagged.
- A flagged cell cannot be revealed.
- Flagging is capped at the selected mine count, but flags may always be removed.

## Extension Points

- Board dimensions and mine limits are centralized in `src/types.ts`.
- Game rules are isolated from the DOM in `src/game.ts`, allowing unit tests or another UI to reuse them.
- Rendering is isolated in `src/ui.ts`, allowing future keyboard controls, touch controls, or alternate layouts.
- The current `Board` model can be extended with timers, player metadata, difficulty names, or persisted game state without changing the cell interaction API.
- `src/game.test.ts` provides a starting point for expanding automated rule coverage.

## Verification

Run the complete build and gameplay tests with:

```bash
npm test
```

The test command compiles TypeScript and runs the Node test suite in `dist/game.test.js`.
