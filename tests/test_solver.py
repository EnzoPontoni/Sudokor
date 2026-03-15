import unittest
from src.solver import solve, ac3, create_domains, validate_board

class TestSolver(unittest.TestCase):

    def setUp(self):
        self.easy_board = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        self.evil_board = [
            [8, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 6, 0, 0, 0, 0, 0],
            [0, 7, 0, 0, 9, 0, 2, 0, 0],
            [0, 5, 0, 0, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 4, 5, 7, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 3, 0],
            [0, 0, 1, 0, 0, 0, 0, 6, 8],
            [0, 0, 8, 5, 0, 0, 0, 1, 0],
            [0, 9, 0, 0, 0, 0, 4, 0, 0]
        ]

        self.solved_board = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
        
        self.invalid_board = [
            [5, 5, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        
        self.empty_board = [[0]*9 for _ in range(9)]

    def test_validate_valid_board(self):
        conflicts = validate_board(self.easy_board)
        self.assertEqual(conflicts, [])

    def test_validate_invalid_board(self):
        conflicts = validate_board(self.invalid_board)
        self.assertGreater(len(conflicts), 0)

    def test_validate_solved_board(self):
        conflicts = validate_board(self.solved_board)
        self.assertEqual(conflicts, [])

    def test_validate_empty_board(self):
        conflicts = validate_board(self.empty_board)
        self.assertEqual(conflicts, [])

    def test_solve_easy_puzzle(self):
        result = solve(self.easy_board)
        self.assertIsNotNone(result)
        domains = create_domains(result)
        self.assertTrue(ac3(domains))

    def test_solve_evil_puzzle(self):
        result = solve(self.evil_board)
        self.assertIsNotNone(result)

    def test_solve_already_solved(self):
        result = solve(self.solved_board)
        self.assertEqual(result, self.solved_board)

    def test_solve_invalid_puzzle(self):
        result = solve(self.invalid_board)
        self.assertIsNone(result)
        
    def test_solve_empty_puzzle(self):
        result = solve(self.empty_board)
        self.assertIsNotNone(result)
        domains = create_domains(result)
        self.assertTrue(ac3(domains))
        
if __name__ == '__main__':
    unittest.main()
