import unittest
import numpy as np
import cv2
from unittest.mock import patch
from src.vision import extract_board

class TestVision(unittest.TestCase):
    
    def setUp(self):
        self.grid_size = 900
        self.cell_size = 100
        self.synthetic_frame = np.ones((1000, 1000, 3), dtype=np.uint8) * 255
        self.grid_bbox = (50, 50, 900, 900)
        for i in range(10):
            cv2.line(self.synthetic_frame, (50 + i*100, 50), (50 + i*100, 950), (0,0,0), 2)
            cv2.line(self.synthetic_frame, (50, 50 + i*100), (950, 50 + i*100), (0,0,0), 2)
            
    def test_extract_board_empty(self):
        board = extract_board(self.synthetic_frame, self.grid_bbox)
        for r in range(9):
            for c in range(9):
                self.assertEqual(board[r][c], 0, f"Cell ({r}, {c}) should be empty")
                
    @patch('src.vision.pytesseract.image_to_data')
    def test_extract_board_with_mocked_ocr(self, mock_ocr):
        mock_ocr.return_value = {
            'text': ['5'],
            'conf': [95],
        }
        cv2.rectangle(self.synthetic_frame, (70, 70), (130, 130), (0, 0, 0), -1)
        board = extract_board(self.synthetic_frame, self.grid_bbox)
        self.assertEqual(board[0][0], 5)
        self.assertEqual(board[0][1], 0)

if __name__ == '__main__':
    unittest.main()
