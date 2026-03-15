from typing import Dict, List, Optional, Set, Tuple
from collections import deque
import copy
import logging

logger = logging.getLogger(__name__)

Board = List[List[int]]
Domains = Dict[Tuple[int, int], Set[int]]

PEERS: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}

def _init_peers() -> None:
    for r in range(9):
        for c in range(9):
            peers = set()
            for i in range(9):
                if i != c:
                    peers.add((r, i))
                if i != r:
                    peers.add((i, c))
            box_r, box_c = 3 * (r // 3), 3 * (c // 3)
            for br in range(box_r, box_r + 3):
                for bc in range(box_c, box_c + 3):
                    if br != r or bc != c:
                        peers.add((br, bc))
            PEERS[(r, c)] = peers

_init_peers()

def validate_board(board: Board) -> List[str]:
    conflicts = []

    for r in range(9):
        seen: Dict[int, int] = {}
        for c in range(9):
            v = board[r][c]
            if v != 0:
                if not (1 <= v <= 9):
                    conflicts.append(f"Invalid value {v} at ({r},{c})")
                elif v in seen:
                    conflicts.append(f"Row {r}: duplicate {v} at cols {seen[v]} and {c}")
                else:
                    seen[v] = c

    for c in range(9):
        seen: Dict[int, int] = {}
        for r in range(9):
            v = board[r][c]
            if v != 0:
                if v in seen:
                    conflicts.append(f"Col {c}: duplicate {v} at rows {seen[v]} and {r}")
                else:
                    seen[v] = r

    for box_r in range(3):
        for box_c in range(3):
            seen: Dict[int, Tuple[int, int]] = {}
            for r in range(box_r * 3, box_r * 3 + 3):
                for c in range(box_c * 3, box_c * 3 + 3):
                    v = board[r][c]
                    if v != 0:
                        if v in seen:
                            conflicts.append(
                                f"Box ({box_r},{box_c}): duplicate {v} at {seen[v]} and ({r},{c})"
                            )
                        else:
                            seen[v] = (r, c)

    return conflicts


def create_domains(board: Board) -> Domains:
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                domains[(r, c)] = {board[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
    return domains

def ac3(domains: Domains) -> bool:
    queue = deque()
    for cell in PEERS:
        for peer in PEERS[cell]:
            queue.append((cell, peer))

    while queue:
        cell, peer = queue.popleft()
        if _revise(domains, cell, peer):
            if not domains[cell]:
                return False
            for neighbor in PEERS[cell]:
                if neighbor != peer:
                    queue.append((neighbor, cell))

    return True

def _revise(domains: Domains, cell: Tuple[int, int], peer: Tuple[int, int]) -> bool:
    revised = False
    if len(domains[peer]) == 1:
        peer_value = next(iter(domains[peer]))
        if peer_value in domains[cell]:
            domains[cell].remove(peer_value)
            revised = True
    return revised

def _select_unassigned_variable_mrv(domains: Domains) -> Optional[Tuple[int, int]]:
    min_len = 10
    best_cell = None
    for cell, domain in domains.items():
        if len(domain) > 1 and len(domain) < min_len:
            min_len = len(domain)
            best_cell = cell
    return best_cell

def backtrack(domains: Domains) -> Optional[Domains]:
    cell = _select_unassigned_variable_mrv(domains)
    if cell is None:
        return domains
    for value in copy.copy(domains[cell]):
        new_domains = copy.deepcopy(domains)
        new_domains[cell] = {value}
        if ac3(new_domains):
            result = backtrack(new_domains)
            if result is not None:
                return result
    return None

def solve(board: Board) -> Optional[Board]:
    if len(board) != 9 or any(len(row) != 9 for row in board):
        logger.error("Invalid board dimensions. Must be 9x9.")
        return None

    clues_count = sum(1 for r in range(9) for c in range(9) if board[r][c] != 0)
    if not (17 <= clues_count <= 81):
        logger.warning(f"Sudoku has {clues_count} clues. A valid Sudoku usually has between 17 and 81 clues.")

    domains = create_domains(board)

    if not ac3(domains):
        logger.warning("Board is invalid or unsolvable at initial AC-3 check.")
        return None

    solved_domains = backtrack(domains)
    if solved_domains is None:
        logger.warning("Backtracking failed to find a solution.")
        return None

    result = [[0] * 9 for _ in range(9)]
    for (r, c), domain in solved_domains.items():
        if len(domain) != 1:
            logger.error(f"Cell {(r, c)} does not have exactly one solution: {domain}")
            return None
        result[r][c] = next(iter(domain))

    return result

def pretty(board: Board) -> None:
    print("-" * 25)
    for i, row in enumerate(board):
        row_str = "| "
        for j, val in enumerate(row):
            row_str += "." if val == 0 else str(val)
            if j % 3 == 2 and j < 8:
                row_str += " | "
            else:
                row_str += " "
        row_str += "|"
        print(row_str)
        if i % 3 == 2:
            print("-" * 25)



