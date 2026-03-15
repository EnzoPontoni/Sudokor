from setuptools import setup, find_packages

setup(
    name="sudoku-bot",
    version="1.0.0",
    description="Bot Autônomo para o Microsoft Sudoku",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.8.0",
        "pytesseract>=0.3.10",
        "Pillow>=10.0.0",
        "pyautogui>=0.9.54",
        "pygetwindow>=0.0.9",
        "mss>=9.0.1",
        "numpy>=1.24.0"
    ],
    python_requires=">=3.10",
)
