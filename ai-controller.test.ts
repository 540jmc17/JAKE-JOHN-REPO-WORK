/**
 * Module: ai-controller.test.ts
 *
 * Purpose:
 * Automated tests for the AIController added in Project 2.
 *
 * These tests verify:
 * - Manual mode behavior
 * - One-step Easy AI behavior
 * - Player + Easy AI alternating turns
 * - Automatic Easy AI mode
 * - Pause behavior
 * - Controller cleanup/disposal
 * - Invalid timer delays
 *
 * Project 2 Addition
 * Jake Crawford + John
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { AIController } from './ai-controller.js';
import { createGame } from './game.js';


/* ============================================================
   HELPER
   ============================================================ */

/**
 * Waits for a specified number of milliseconds.
 *
 * This is useful because AIController uses setTimeout()
 * for delayed AI turns.
 */
function wait(
    milliseconds: number
): Promise<void> {

    return new Promise(
        (resolve) => {

            setTimeout(
                resolve,
                milliseconds
            );
        }
    );
}


/* ============================================================
   TEST 1
   Default manual mode
   ============================================================ */

test(
    'AIController begins in manual mode',
    () => {

        const board =
            createGame(15);


        const controller =
            new AIController(
                board,
                () => {}
            );


        assert.equal(
            controller.mode,
            'manual'
        );


        assert.equal(
            controller.canPlayerAct,
            true
        );


        assert.equal(
            controller.canStep,
            true
        );


        assert.equal(
            controller.isAutoRunning,
            false
        );


        assert.equal(
            controller.isWaitingForAI,
            false
        );


        controller.dispose();
    }
);


/* ============================================================
   TEST 2
   Manual one-step AI
   ============================================================ */

test(
    'manual step performs exactly one AI move',
    () => {

        const board =
            createGame(15);


        let solverCalls =
            0;


        let updateCalls =
            0;


        /**
         * Fake AI solver.
         *
         * Instead of choosing a real random square,
         * this simply records that the solver was called.
         */
        const fakeSolver =
            (): boolean => {

                solverCalls += 1;

                return true;
            };


        const controller =
            new AIController(
                board,

                () => {

                    updateCalls += 1;
                },

                fakeSolver
            );


        const moved =
            controller.step();


        assert.equal(
            moved,
            true
        );


        assert.equal(
            solverCalls,
            1
        );


        assert.equal(
            updateCalls,
            1
        );


        controller.dispose();
    }
);


/* ============================================================
   TEST 3
   Alternating player + AI turns
   ============================================================ */

test(
    'alternating mode schedules one AI move after a player move',
    async () => {

        const board =
            createGame(15);


        /**
         * Put the board into playing mode manually so
         * this test does not depend on random mine placement.
         */
        board.gameStatus =
            'playing';


        /**
         * Prevent the selected square from triggering
         * the empty-cell flood reveal.
         */
        board.cells[0][0].adjacentMines =
            1;


        let solverCalls =
            0;


        const fakeSolver =
            (): boolean => {

                solverCalls += 1;

                return true;
            };


        const controller =
            new AIController(
                board,
                () => {},
                fakeSolver,

                /**
                 * Use a very short delay during testing.
                 */
                10
            );


        controller.setMode(
            'alternating'
        );


        assert.equal(
            controller.mode,
            'alternating'
        );


        /**
         * Human player reveals one square.
         */
        const playerMoved =
            controller.reveal(
                0,
                0
            );


        assert.equal(
            playerMoved,
            true
        );


        /**
         * Immediately after the player moves,
         * the player should be locked out.
         */
        assert.equal(
            controller.isWaitingForAI,
            true
        );


        assert.equal(
            controller.canPlayerAct,
            false
        );


        /**
         * Wait long enough for the scheduled AI turn.
         */
        await wait(
            30
        );


        assert.equal(
            solverCalls,
            1
        );


        assert.equal(
            controller.isWaitingForAI,
            false
        );


        /**
         * Control should return to the player.
         */
        assert.equal(
            controller.canPlayerAct,
            true
        );


        controller.dispose();
    }
);


/* ============================================================
   TEST 4
   Automatic AI mode
   ============================================================ */

test(
    'automatic mode starts the AI and stops when no move is available',
    async () => {

        const board =
            createGame(15);


        let solverCalls =
            0;


        /**
         * Return false immediately.
         *
         * This simulates an AI that cannot make
         * another legal move.
         */
        const fakeSolver =
            (): boolean => {

                solverCalls += 1;

                return false;
            };


        const controller =
            new AIController(
                board,
                () => {},
                fakeSolver,
                10
            );


        controller.setMode(
            'automatic'
        );


        assert.equal(
            controller.mode,
            'automatic'
        );


        const started =
            controller.startAuto();


        assert.equal(
            started,
            true
        );


        assert.equal(
            controller.isAutoRunning,
            true
        );


        /**
         * Automatic mode blocks human moves.
         */
        assert.equal(
            controller.canPlayerAct,
            false
        );


        await wait(
            30
        );


        /**
         * Solver should have run once.
         */
        assert.equal(
            solverCalls,
            1
        );


        /**
         * Because the solver returned false,
         * automatic mode should stop.
         */
        assert.equal(
            controller.isAutoRunning,
            false
        );


        controller.dispose();
    }
);


/* ============================================================
   TEST 5
   Pause automatic AI
   ============================================================ */

test(
    'pauseAuto cancels a scheduled automatic AI move',
    async () => {

        const board =
            createGame(15);


        let solverCalls =
            0;


        const fakeSolver =
            (): boolean => {

                solverCalls += 1;

                return true;
            };


        const controller =
            new AIController(
                board,
                () => {},
                fakeSolver,

                /**
                 * Give us enough time to pause
                 * before the solver runs.
                 */
                40
            );


        controller.setMode(
            'automatic'
        );


        controller.startAuto();


        /**
         * Pause immediately.
         */
        controller.pauseAuto();


        assert.equal(
            controller.isAutoRunning,
            false
        );


        /**
         * Wait longer than the original timer.
         */
        await wait(
            70
        );


        /**
         * The cancelled timer should never
         * have called the solver.
         */
        assert.equal(
            solverCalls,
            0
        );


        controller.dispose();
    }
);


/* ============================================================
   TEST 6
   Starting automatic AI twice
   ============================================================ */

test(
    'automatic AI cannot be started twice at the same time',
    () => {

        const board =
            createGame(15);


        const controller =
            new AIController(
                board,
                () => {},
                () => true,
                100
            );


        controller.setMode(
            'automatic'
        );


        const firstStart =
            controller.startAuto();


        const secondStart =
            controller.startAuto();


        assert.equal(
            firstStart,
            true
        );


        assert.equal(
            secondStart,
            false
        );


        controller.dispose();
    }
);


/* ============================================================
   TEST 7
   Dispose controller
   ============================================================ */

test(
    'dispose cancels pending AI work and blocks future player actions',
    async () => {

        const board =
            createGame(15);


        board.gameStatus =
            'playing';


        board.cells[0][0].adjacentMines =
            1;


        let solverCalls =
            0;


        const fakeSolver =
            (): boolean => {

                solverCalls += 1;

                return true;
            };


        const controller =
            new AIController(
                board,
                () => {},
                fakeSolver,
                40
            );


        controller.setMode(
            'alternating'
        );


        /**
         * Player move schedules an AI response.
         */
        controller.reveal(
            0,
            0
        );


        assert.equal(
            controller.isWaitingForAI,
            true
        );


        /**
         * Dispose before the timer gets a chance
         * to execute.
         */
        controller.dispose();


        await wait(
            70
        );


        /**
         * The AI solver should never have run.
         */
        assert.equal(
            solverCalls,
            0
        );


        /**
         * Disposed controllers cannot accept
         * additional player actions.
         */
        assert.equal(
            controller.canPlayerAct,
            false
        );


        assert.equal(
            controller.canStep,
            false
        );
    }
);


/* ============================================================
   TEST 8
   Invalid delay
   ============================================================ */

test(
    'AIController rejects an invalid AI delay',
    () => {

        const board =
            createGame(15);


        assert.throws(
            () => {

                new AIController(
                    board,
                    () => {},
                    () => true,
                    0
                );
            },

            RangeError
        );
    }
);
