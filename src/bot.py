import time
import argparse
import logging
from src.vision import read_board, get_empty_cells
from src.solver import solve, pretty, validate_board
from src.automator import Automator

logger = logging.getLogger(__name__)

class SudokuError(Exception):
    pass

class SudokuBot:
    def __init__(self, mode="normal"):
        self.mode = mode
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

    def run(self):
        logger.info("Starting Sudoku Bot. Please focus the Microsoft Sudoku window.")
        logger.info("You have 5 seconds...")
        time.sleep(5)
        
        start_time = time.time()
        
        logger.info("Reading board from screen...")
        read_start = time.time()
        result = read_board()
        
        if result[0] is None:
            raise SudokuError("Failed to detect Sudoku grid on screen.")
            
        board, cell_coords, grid_bbox = result
        read_time = time.time() - read_start
        
        logger.info("Board read successfully:")
        pretty(board)
        
        conflicts = validate_board(board)
        if conflicts:
            logger.error("=== BOARD VALIDATION FAILED ===")
            for conflict in conflicts:
                logger.error(f"  {conflict}")
            raise SudokuError(
                f"OCR read an invalid board with {len(conflicts)} conflict(s). "
                "The OCR likely misread digits. Check the log for details."
            )
        
        clues = sum(1 for r in range(9) for c in range(9) if board[r][c] != 0)
        if clues < 17 or clues > 80:
            raise SudokuError(f"Invalid Sudoku: detected {clues} clues. Expected between 17 and 80.")
            
        logger.info("Solving puzzle...")
        solve_start = time.time()
        solved_board = solve(board)
        solve_time = time.time() - solve_start
        
        if solved_board is None:
            raise SudokuError("Solver failed to find a valid solution. OCR might have misread a number.")
            
        logger.info("Puzzle solved!")
        pretty(solved_board)
        
        logger.info(f"Filling solution in '{self.mode}' mode...")
        fill_start = time.time()
        automator = Automator(cell_coords, delay=0.05)
        
        if self.mode == "fast":
            automator.fill_solution_fast(board, solved_board)
        else:
            automator.fill_solution(board, solved_board)
            
        fill_time = time.time() - fill_start

        logger.info("Double-checking board for missed cells...")
        time.sleep(0.5)
        empty_cells = get_empty_cells(grid_bbox)
        missed = [(r, c) for (r, c) in empty_cells if board[r][c] == 0]
        if missed:
            logger.warning(f"Found {len(missed)} missed cell(s): {missed}. Filling now...")
            for r, c in missed:
                logger.info(f"Re-filling ({r},{c}) -> {solved_board[r][c]}")
                automator.click_cell(r, c)
                time.sleep(0.15)
                automator.type_digit(solved_board[r][c])
                time.sleep(0.12)
            logger.info("Missed cells filled.")
        else:
            logger.info("Double-check passed — all cells are filled!")
        
        total_time = time.time() - start_time
        logger.info("=== STATISTICS ===")
        logger.info(f"Read time:  {read_time:.2f}s")
        logger.info(f"Solve time: {solve_time:.2f}s")
        logger.info(f"Fill time:  {fill_time:.2f}s")
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info("==================")

    def run_loop(self, puzzles=5):
        for i in range(puzzles):
            logger.info(f"--- Starting Puzzle {i+1}/{puzzles} ---")
            try:
                self.run()
            except SudokuError as e:
                logger.error(f"Error during puzzle {i+1}: {e}")
                
            if i < puzzles - 1:
                logger.info("Waiting 2 seconds before next puzzle...")
                time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microsoft Sudoku Bot")
    parser.add_argument("--mode", choices=["normal", "fast"], default="normal")
    parser.add_argument("--loop", type=int, default=1, help="Número de puzzles")
    args = parser.parse_args()
    
    bot = SudokuBot(mode=args.mode)
    if args.loop > 1:
        bot.run_loop(args.loop)
    else:
        bot.run()
