import cv2
import numpy as np
import pygetwindow as gw
from PIL import ImageGrab
import pytesseract
import logging
from typing import Tuple, List, Dict, Optional
from src.automator import calc_cell_centers

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

logger = logging.getLogger(__name__)

Board = List[List[int]]
CoordDict = Dict[Tuple[int, int], Tuple[int, int]]
BBox = Tuple[int, int, int, int]

def find_sudoku_window() -> Optional[BBox]:
    try:
        windows = gw.getWindowsWithTitle("Microsoft Sudoku")
        if not windows:
            logger.warning("Microsoft Sudoku window not found.")
            return None
        win = windows[0]
        if win.width <= 0 or win.height <= 0:
            return None
        return (win.left, win.top, win.width, win.height)
    except Exception as e:
        logger.error(f"Error querying window: {e}")
        return None

def capture_window(bbox: Optional[BBox] = None) -> Tuple[np.ndarray, Tuple[int, int]]:
    if bbox is None:
        logger.info("Capturing fullscreen as fallback.")
        img = ImageGrab.grab()
        offset_x, offset_y = 0, 0
    else:
        x, y, w, h = bbox
        try:
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            offset_x, offset_y = x, y
        except Exception as e:
            logger.error(f"Error capturing bbox {bbox}: {e}. Falling back to fullscreen.")
            img = ImageGrab.grab()
            offset_x, offset_y = 0, 0
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return frame, (offset_x, offset_y)

def detect_grid(frame: np.ndarray) -> BBox:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 90)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    img_area = frame.shape[0] * frame.shape[1]
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 0.10 * img_area:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                if 0.85 <= aspect_ratio <= 1.15:
                    inset = max(4, int(min(w, h) * 0.01))
                    x, y = x + inset, y + inset
                    w, h = w - 2 * inset, h - 2 * inset
                    logger.info(f"Found Sudoku grid (inset={inset}): ({x},{y}) {w}x{h}")
                    return (x, y, w, h)
    logger.warning("Could not detect grid contour. Falling back to center 70%.")
    h_img, w_img = frame.shape[:2]
    w = int(w_img * 0.7)
    h = int(h_img * 0.7)
    x = int((w_img - w) / 2)
    y = int((h_img - h) / 2)
    return (x, y, w, h)

def _is_original_clue(cell_bgr: np.ndarray) -> bool:
    hsv = cv2.cvtColor(cell_bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(cell_bgr, cv2.COLOR_BGR2GRAY)
    dark_mask = gray < 120
    if np.sum(dark_mask) < 10:
        b, g, r = cv2.split(cell_bgr)
        blue_mask = (b > 150) & (r < 120) & (g < 120)
        if np.sum(blue_mask) > 20:
            return False
        red_mask = (r > 150) & (b < 120)
        if np.sum(red_mask) > 20:
            return False
        gray_text_mask = (hsv[:, :, 1] < 30) & (hsv[:, :, 2] > 100) & (hsv[:, :, 2] < 200)
        if np.sum(gray_text_mask) > np.sum(dark_mask) * 2:
            return False
        return True
    dark_saturation = hsv[:, :, 1][dark_mask]
    mean_sat = float(np.mean(dark_saturation))
    return mean_sat < 60


def _count_holes(binary_img: np.ndarray) -> int:
    inv = cv2.bitwise_not(binary_img)
    contours, hierarchy = cv2.findContours(inv, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return 0
    n_holes = 0
    for i in range(len(hierarchy[0])):
        if hierarchy[0][i][3] != -1:
            area = cv2.contourArea(contours[i])
            total_area = binary_img.shape[0] * binary_img.shape[1]
            if area > total_area * 0.03:
                n_holes += 1
    return n_holes


def _verify_digit_structure(binary_img: np.ndarray, ocr_digit: int) -> int:
    if ocr_digit == 0:
        return 0
    
    h, w = binary_img.shape
    total_white = int(np.sum(binary_img > 0))
    if total_white == 0:
        return 0
    
    n_holes = _count_holes(binary_img)
    top_white = int(np.sum(binary_img[:h // 2, :] > 0))
    top_ratio = top_white / max(total_white, 1)
    if n_holes >= 2 and ocr_digit != 8:
        logger.debug(f"Structure fix: {ocr_digit} → 8 (2 holes)")
        return 8
    if n_holes == 1:
        if ocr_digit in (1, 2, 3, 5, 7):
            if top_ratio > 0.55:
                logger.debug(f"Structure fix: {ocr_digit} → 9 (1 hole, top-heavy)")
                return 9
            elif top_ratio < 0.45:
                logger.debug(f"Structure fix: {ocr_digit} → 6 (1 hole, bottom-heavy)")
                return 6
            else:
                logger.debug(f"Structure fix: {ocr_digit} → 4 (1 hole, balanced)")
                return 4
        if ocr_digit == 6 and top_ratio > 0.55:
            logger.debug(f"Structure fix: 6 → 9 (top-heavy)")
            return 9
        if ocr_digit == 9 and top_ratio < 0.45:
            logger.debug(f"Structure fix: 9 → 6 (bottom-heavy)")
            return 6
    if n_holes == 0:
        if ocr_digit == 8:
            logger.debug(f"Structure fix: 8 → 3 (0 holes)")
            return 3
        if ocr_digit in (6, 9):
            logger.debug(f"Structure fix: {ocr_digit} → 5 (0 holes)")
            return 5
    return ocr_digit


def _ocr_cell(gray_img: np.ndarray) -> Tuple[int, int]:
    config = r'--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'
    data = pytesseract.image_to_data(
        gray_img, config=config, output_type=pytesseract.Output.DICT
    )
    best_digit = 0
    best_conf = 0
    for i, text in enumerate(data['text']):
        conf = int(data['conf'][i])
        t = text.strip()
        if t and t in '123456789' and conf > best_conf:
            best_digit = int(t)
            best_conf = conf
    return best_digit, best_conf


def extract_board(frame: np.ndarray, grid_bbox: BBox) -> Board:
    x, y, w, h = grid_bbox
    grid_img = frame[y:y+h, x:x+w]
    
    board = [[0 for _ in range(9)] for _ in range(9)]
    
    cell_w = w / 9.0
    cell_h = h / 9.0
    
    for r in range(9):
        for c in range(9):
            cx = int(c * cell_w)
            cy = int(r * cell_h)
            cw = int(cell_w)
            ch = int(cell_h)
            
            cell_img = grid_img[cy:cy+ch, cx:cx+cw]
            
            is_block_left = (c % 3 == 0)
            is_block_right = (c % 3 == 2)
            is_block_top = (r % 3 == 0)
            is_block_bottom = (r % 3 == 2)
            
            base_mx = 0.12
            base_my = 0.12
            ml = base_mx + (0.03 if is_block_left else 0)
            mr = base_mx + (0.03 if is_block_right else 0)
            mt = base_my + (0.03 if is_block_top else 0)
            mb = base_my + (0.03 if is_block_bottom else 0)
            
            x1 = int(cw * ml)
            x2 = cw - int(cw * mr)
            y1 = int(ch * mt)
            y2 = ch - int(ch * mb)
            
            inner_cell = cell_img[y1:y2, x1:x2]
            
            if inner_cell.size == 0 or inner_cell.shape[0] < 5 or inner_cell.shape[1] < 5:
                board[r][c] = 0
                continue
            
            gray = cv2.cvtColor(inner_cell, cv2.COLOR_BGR2GRAY)
            
            mean_val = float(np.mean(gray))
            dark_threshold = max(mean_val * 0.55, 80)
            dark_pixels = int(np.sum(gray < dark_threshold))
            total_pixels = gray.shape[0] * gray.shape[1]
            dark_ratio = dark_pixels / total_pixels
            
            if dark_ratio < 0.04:
                board[r][c] = 0
                continue
                
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts:
                board[r][c] = 0
                continue
                
            significant = [cnt for cnt in cnts if cv2.contourArea(cnt) > 30]
            if not significant:
                board[r][c] = 0
                continue
            
            total_digit_area = sum(cv2.contourArea(cnt) for cnt in significant)
            if total_digit_area < 50:
                board[r][c] = 0
                continue
                
            mask = np.zeros_like(thresh)
            cv2.drawContours(mask, significant, -1, 255, -1)
            
            digit_binary = np.zeros_like(thresh)
            digit_binary[(thresh > 0) & (mask > 0)] = 255
            clean_cell = np.ones_like(gray, dtype=np.uint8) * 255
            clean_cell[(thresh > 0) & (mask > 0)] = 0
            
            pad = 15
            padded = cv2.copyMakeBorder(clean_cell, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)
            resized = cv2.resize(padded, (64, 64), interpolation=cv2.INTER_AREA)
            
            digit, conf = _ocr_cell(resized)
            if digit == 0 or conf < 50:
                adaptive = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 15, 5
                )
                padded2 = cv2.copyMakeBorder(adaptive, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)
                resized2 = cv2.resize(padded2, (64, 64), interpolation=cv2.INTER_AREA)
                digit2, conf2 = _ocr_cell(resized2)
                if conf2 > conf:
                    digit, conf = digit2, conf2
            
            if digit != 0 and conf < 50:
                digit_resized = cv2.resize(digit_binary, (48, 48), interpolation=cv2.INTER_AREA)
                _, digit_resized = cv2.threshold(digit_resized, 127, 255, cv2.THRESH_BINARY)
                verified = _verify_digit_structure(digit_resized, digit)
                if verified != digit:
                    logger.info(f"Cell ({r},{c}): OCR={digit} conf={conf} → structural fix to {verified}")
                    digit = verified
            
            if digit == 0 and dark_ratio > 0.08:
                reduced_inner = cell_img[
                    int(ch * 0.07):ch - int(ch * 0.07),
                    int(cw * 0.07):cw - int(cw * 0.07)
                ]
                if reduced_inner.size > 0 and reduced_inner.shape[0] >= 5 and reduced_inner.shape[1] >= 5:
                    gray2 = cv2.cvtColor(reduced_inner, cv2.COLOR_BGR2GRAY)
                    _, thr2 = cv2.threshold(gray2, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
                    clean2 = cv2.bitwise_not(thr2)
                    pad2 = cv2.copyMakeBorder(clean2, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
                    rsz2 = cv2.resize(pad2, (64, 64), interpolation=cv2.INTER_AREA)
                    d2, c2 = _ocr_cell(rsz2)
                    if d2 != 0 and c2 > 20:
                        logger.info(f"Cell ({r},{c}): retry reduced margin → {d2} (conf={c2})")
                        digit, conf = d2, c2
            
            if digit == 0 and dark_ratio > 0.08:
                for psm in [7, 6, 8]:
                    cfg = f'--psm {psm} --oem 3 -c tessedit_char_whitelist=123456789'
                    data = pytesseract.image_to_data(
                        resized, config=cfg, output_type=pytesseract.Output.DICT
                    )
                    for i, text in enumerate(data['text']):
                        t = text.strip()
                        c_val = int(data['conf'][i])
                        if t and t in '123456789' and c_val > 0:
                            logger.info(f"Cell ({r},{c}): psm={psm} → {t} (conf={c_val})")
                            digit, conf = int(t), c_val
                            break
                    if digit != 0:
                        break
            
            if digit == 0 and dark_ratio > 0.08:
                dil_kernel = np.ones((2, 2), np.uint8)
                inv_resized = cv2.bitwise_not(resized)
                dilated_inv = cv2.dilate(inv_resized, dil_kernel, iterations=1)
                dilated = cv2.bitwise_not(dilated_inv)
                d3, c3 = _ocr_cell(dilated)
                if d3 != 0:
                    logger.info(f"Cell ({r},{c}): dilation retry → {d3} (conf={c3})")
                    digit, conf = d3, c3
            
            if digit == 0 and dark_ratio > 0.08:
                raw_padded = cv2.copyMakeBorder(
                    gray, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255
                )
                raw_resized = cv2.resize(raw_padded, (64, 64), interpolation=cv2.INTER_AREA)
                for psm in [10, 7, 6]:
                    cfg = f'--psm {psm} --oem 3 -c tessedit_char_whitelist=123456789'
                    data = pytesseract.image_to_data(
                        raw_resized, config=cfg, output_type=pytesseract.Output.DICT
                    )
                    for i, text in enumerate(data['text']):
                        t = text.strip()
                        c_val = int(data['conf'][i])
                        if t and t in '123456789' and c_val > 0:
                            logger.info(f"Cell ({r},{c}): raw gray psm={psm} → {t} (conf={c_val})")
                            digit, conf = int(t), c_val
                            break
                    if digit != 0:
                        break
            
            if digit == 0 and dark_ratio > 0.08:
                logger.error(f"Cell ({r},{c}): STILL FAILED after all retries (dark_ratio={dark_ratio:.2f}) — clue may be lost!")
            
            board[r][c] = digit
            
    return board


def validate_ocr_board(board: Board) -> List[str]:
    conflicts = []
    
    for r in range(9):
        seen: Dict[int, int] = {}
        for c in range(9):
            v = board[r][c]
            if v != 0:
                if v in seen:
                    conflicts.append(f"Row {r}: duplicate {v} at cols {seen[v]} and {c}")
                else:
                    seen[v] = c
    
    for c in range(9):
        seen_r: Dict[int, int] = {}
        for r in range(9):
            v = board[r][c]
            if v != 0:
                if v in seen_r:
                    conflicts.append(f"Col {c}: duplicate {v} at rows {seen_r[v]} and {r}")
                else:
                    seen_r[v] = r
    
    for box_r in range(3):
        for box_c in range(3):
            seen_b: Dict[int, Tuple[int, int]] = {}
            for r in range(box_r * 3, box_r * 3 + 3):
                for c in range(box_c * 3, box_c * 3 + 3):
                    v = board[r][c]
                    if v != 0:
                        if v in seen_b:
                            conflicts.append(
                                f"Box ({box_r},{box_c}): dup {v} at {seen_b[v]} and ({r},{c})"
                            )
                        else:
                            seen_b[v] = (r, c)
    
    return conflicts

def get_empty_cells(grid_bbox: BBox) -> List[Tuple[int, int]]:
    bbox = find_sudoku_window()
    frame, _ = capture_window(bbox)
    x, y, w, h = grid_bbox
    grid_img = frame[y:y+h, x:x+w]

    cell_w = w / 9.0
    cell_h = h / 9.0
    empty = []

    for r in range(9):
        for c in range(9):
            cx = int(c * cell_w)
            cy = int(r * cell_h)
            cw = int(cell_w)
            ch = int(cell_h)

            x1 = int(cw * 0.12)
            x2 = cw - int(cw * 0.12)
            y1 = int(ch * 0.12)
            y2 = ch - int(ch * 0.12)
            inner = grid_img[cy+y1:cy+y2, cx+x1:cx+x2]

            if inner.size == 0:
                empty.append((r, c))
                continue

            hsv = cv2.cvtColor(inner, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(inner, cv2.COLOR_BGR2GRAY)
            dark = np.sum(gray < 100)
            colored = np.sum(hsv[:, :, 1] > 50)

            total = inner.shape[0] * inner.shape[1]
            if (dark + colored) / total < 0.04:
                empty.append((r, c))

    return empty


def read_board() -> Tuple[Optional[Board], CoordDict, Optional[BBox]]:
    bbox = find_sudoku_window()
    frame, (offset_x, offset_y) = capture_window(bbox)
    grid_bbox = detect_grid(frame)
    if grid_bbox is None:
        return None, {}, None
    gx, gy, gw, gh = grid_bbox
    board = extract_board(frame, grid_bbox)
    conflicts = validate_ocr_board(board)
    if conflicts:
        logger.error("=== OCR VALIDATION FAILED ===")
        for conflict in conflicts:
            logger.error(f"  CONFLICT: {conflict}")
        logger.error("The board read by OCR has constraint violations.")
        logger.error("This usually means the OCR misread one or more digits.")
    cell_coords = calc_cell_centers(grid_bbox, offset=(offset_x, offset_y))
    return board, cell_coords, grid_bbox
