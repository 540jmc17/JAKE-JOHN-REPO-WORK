/**
 * Module: easy-ai.test.ts
 *
 * Purpose:
 * Automated tests for the Easy AI implementation added in Project 2.
 *
 * The tests verify that Easy AI:
 * - Makes a valid move
 * - Selects only covered cells
 * - Ignores flagged cells
 * - Can select different covered cells
 * - Stops after a win or loss
 * - Returns false when no legal moves remain
 * - Rejects an invalid random-number source
 * - Can lose by randomly selecting a mine
 * - Can complete a winning move
 *
 * Project 2 Addition
 * Jake Crawford + John
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
    createGame,
    makeEasyAIMove
} from './game.js';


/* ============================================================
   TEST 1
   Easy AI makes a move
   ============================================================ */

test(
    'Easy AI makes one move on a new board',
    () => {

        const board =
            createGame(15);

        /*
         * Returning 0 forces Easy AI to select
         * the first available covered cell.
         */
        const moved =
            makeEasyAIMove(
                board,
                () => 0
            );

        assert.equal(
            moved,
            true
        );

        /*
         * The first AI move should also start
         * the Minesweeper game.
         */
        assert.equal(
            board.gameStatus,
            'playing'
        );

        /*
         * The selected cell should have been revealed.
         */
        assert.equal(
            board.cells[0][0].state,
            'revealed'
        );
    }
);


/* ============================================================
   TEST 2
   Easy AI ignores flagged cells
   ============================================================ */

test(
    'Easy AI does not select a flagged cell',
    () => {

        const board =
            createGame(15);

        /*
         * Flag the first square manually.
         *
         * Easy AI should skip this cell because
         * it only considers cells whose state
         * is "covered".
         */
        board.cells[0][0].state =
            'flagged';


        const moved =
            makeEasyAIMove(
                board,
                () => 0
            );


        assert.equal(
            moved,
            true
        );


        /*
         * The flagged square must stay flagged.
         */
        assert.equal(
            board.cells[0][0].state,
            'flagged'
        );


        /*
         * Since [0][0] was unavailable,
         * the first valid covered cell should
         * be [0][1].
         */
        assert.equal(
            board.cells[0][1].state,
            'revealed'
        );
    }
);


/* ============================================================
   TEST 3
   Easy AI can select another location
   ============================================================ */

test(
    'Easy AI uses the random value to choose among covered cells',
    () => {

        const board =
            createGame(15);


        /*
         * A number very close to 1 causes the AI
         * to select the final available coordinate.
         */
        const moved =
            makeEasyAIMove(
                board,
                () => 0.999999
            );


        assert.equal(
            moved,
            true
        );


        /*
         * On a fresh 10x10 board, the final
         * candidate is row 9, column 9.
         */
        assert.equal(
            board.cells[9][9].state,
            'revealed'
        );
    }
);


/* ============================================================
   TEST 4
   AI stops after game is won
   ============================================================ */

test(
    'Easy AI does not move after the game has been won',
    () => {

        const board =
            createGame(15);


        board.gameStatus =
            'won';


        const moved =
            makeEasyAIMove(
                board,
                () => 0
            );


        assert.equal(
            moved,
            false
        );
    }
);


/* ============================================================
   TEST 5
   AI stops after game is lost
   ============================================================ */

test(
    'Easy AI does not move after the game has been lost',
    () => {

        const board =
            createGame(15);


        board.gameStatus =
            'lost';


        const moved =
            makeEasyAIMove(
                board,
                () => 0
            );


        assert.equal(
            moved,
            false
        );
    }
);


/* ============================================================
   TEST 6
   No legal moves remain
   ============================================================ */

test(
    'Easy AI returns false when no covered cells remain',
    () => {

        const board =
            createGame(15);


        /*
         * Make every cell unavailable to Easy AI.
         */
        for (
            const row of board.cells
        ) {

            for (
                const cell of row
            ) {

                cell.state =
                    'flagged';
            }
        }


        const moved =
            makeEasyAIMove(
                board,
                () => 0
            );


        assert.equal(
            moved,
            false
        );
    }
);


/* ============================================================
   TEST 7
   Invalid random source
   ============================================================ */

test(
    'Easy AI rejects a random value outside the valid range',
    () => {

        const board =
            createGame(15);


        /*
         * Math.random() should always produce:
         *
         * 0 <= value < 1
         *
         * Therefore 1 is invalid.
         */
        assert.throws(
            () => {

                makeEasyAIMove(
                    board,
                    () => 1
                );
            },

            RangeError
        );
    }
);


/* ============================================================
   TEST 8
   Easy AI can hit a mine
   ============================================================ */

test(
    'Easy AI can randomly select a mine and lose the game',
    () => {

        const board =
            createGame(1);


        /*
         * Pretend mine placement has already happened.
         */
        board.gameStatus =
            'playing';


        /*
         * Put a mine in the first coordinate.
         *
         * Since our random function returns 0,
         * Easy AI will choose this square.
         */
        board.cells[0][0].isMine =
            true;


        const moved =
            makeEasyAIMove(
                board,
                () => 0
            );


        assert.equal(
            moved,
            true
        );


        /*
         * Selecting the mine should lose the game.
         */
        assert.equal(
            board.gameStatus,
            'lost'
        );


        /*
         * Mines should be revealed when the
         * game is lost.
         */
        assert.equal(
            board.cells[0][0].state,
            'revealed'
        );
    }
);


/* ============================================================
   TEST 9
   Easy AI can complete the game
   ============================================================ */

test(
    'Easy AI can reveal the final safe cell and win',
    () => {

        const board =
            createGame(1);


        board.gameStatus =
            'playing';


        /*
         * Create a controlled board state where
         * every safe cell has already been revealed.
         */
        for (
            const row of board.cells
        ) {

            for (
                const cell of row
            ) {

                cell.isMine =
                    false;

                cell.adjacentMines =
                    0;

                cell.state =
                    'revealed';
            }
        }


        /*
         * Create one known mine.
         *
         * Flagging it removes it from the Easy AI's
         * list of possible selections.
         */
        board.cells[0][0].isMine =
            true;

        board.cells[0][0].state =
            'flagged';


        /*
         * Leave exactly one safe square covered.
         */
        board.cells[0][1].state =
            'covered';


        /*
         * Since only one legal cell remains,
         * Easy AI must select it.
         */
        const moved =
            makeEasyAIMove(
                board,
                () => 0
            );


        assert.equal(
            moved,
            true
        );


        assert.equal(
            board.cells[0][1].state,
            'revealed'
        );


        /*
         * Revealing the final safe square
         * should win the game.
         */
        assert.equal(
            board.gameStatus,
            'won'
        );
    }
);
