import pyautogui
import time
import logging
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)

CoordDict = Dict[Tuple[int, int], Tuple[int, int]]
Board = List[List[int]]

def calc_cell_centers(grid_bbox: Tuple[int, int, int, int], offset: Tuple[int, int] = (0, 0)) -> CoordDict:
    gx, gy, gw, gh = grid_bbox
    offset_x, offset_y = offset
    cell_w = gw / 9.0
    cell_h = gh / 9.0
    cell_coords = {}
    for r in range(9):
        for c in range(9):
            center_x = offset_x + gx + int((c + 0.5) * cell_w)
            center_y = offset_y + gy + int((r + 0.5) * cell_h)
            cell_coords[(r, c)] = (center_x, center_y)
    return cell_coords

class Automator:
    def __init__(self, cell_coords: CoordDict, delay: float = 0.05):
        self.cell_coords = cell_coords
        self.delay = delay
        pyautogui.PAUSE = delay

    def click_cell(self, row: int, col: int) -> None:
        if (row, col) in self.cell_coords:
            x, y = self.cell_coords[(row, col)]
            pyautogui.click(x=x, y=y)
        else:
            logger.error(f"Cannot click cell {(row, col)}: coordinates not found.")

    def type_digit(self, digit: int) -> None:
        if 1 <= digit <= 9:
            pyautogui.press(str(digit))
            logger.debug(f"Pressionou {digit}")
        else:
            logger.warning(f"Invalid digit to type: {digit}. Expected 1-9.")

    def fill_solution(self, original_board: Board, solved_board: Board) -> None:
        logger.info("Starting to fill the solution...")
        old_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0.02
        for r in range(9):
            for c in range(9):
                if original_board[r][c] != 0:
                    continue
                correct_digit = solved_board[r][c]
                logger.info(f"Preenchendo ({r},{c}) -> {correct_digit}")
                self.click_cell(r, c)
                time.sleep(0.12)
                self.type_digit(correct_digit)
                time.sleep(0.10)
        pyautogui.PAUSE = old_pause
        logger.info("Solution filling completed.")

    def fill_solution_fast(self, original_board: Board, solved_board: Board) -> None:
        logger.info("Starting fast fill mode...")
        old_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0.02
        for r in range(9):
            for c in range(9):
                if original_board[r][c] == 0:
                    correct_digit = solved_board[r][c]
                    self.click_cell(r, c)
                    time.sleep(0.10)
                    self.type_digit(correct_digit)
                    time.sleep(0.08)
        pyautogui.PAUSE = old_pause
        logger.info("Fast fill completed.")

