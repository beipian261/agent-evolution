import time
import pyautogui
import logging
from typing import Tuple, Optional
import platform

if platform.system() == 'Windows':
    import win32gui
    import win32con

pyautogui.FAILSAFE = False
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimulatorController:
    def __init__(self, config_manager):
        self.config = config_manager
        self.window_handle = None
        self.window_rect = None

    def find_simulator_window(self) -> Optional[int]:
        if platform.system() != 'Windows':
            logger.warning("仅支持Windows系统")
            return None

        window_title = self.config.get('simulator.window_title', 'MuMuPlayer')

        def callback(hwnd, extra):
            if window_title in win32gui.GetWindowText(hwnd):
                extra.append(hwnd)

        windows = []
        win32gui.EnumWindows(callback, windows)
        if windows:
            self.window_handle = windows[0]
            self.get_window_rect()
            logger.info(f"找到模拟器窗口: {win32gui.GetWindowText(self.window_handle)}")
            return self.window_handle
        logger.warning("未找到模拟器窗口")
        return None

    def get_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        if not self.window_handle:
            return None
        rect = win32gui.GetWindowRect(self.window_handle)
        self.window_rect = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
        return self.window_rect

    def bring_to_front(self) -> bool:
        if not self.window_handle:
            if not self.find_simulator_window():
                return False
        try:
            win32gui.SetForegroundWindow(self.window_handle)
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"激活窗口失败: {e}")
            return False

    def click(self, x: int, y: int, relative: bool = True) -> None:
        if relative and self.window_rect:
            x = self.window_rect[0] + x
            y = self.window_rect[1] + y
        pyautogui.click(x, y)
        logger.info(f"点击坐标: ({x}, {y})")

    def type_text(self, text: str, interval: float = 0.1) -> None:
        pyautogui.typewrite(text, interval=interval)
        logger.info(f"输入文本: {text}")

    def press_key(self, key: str) -> None:
        pyautogui.press(key)
        logger.info(f"按键: {key}")

    def scroll(self, clicks: int) -> None:
        pyautogui.scroll(clicks)
        logger.info(f"滚动: {clicks}")

    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> 'Image':
        if region and self.window_rect:
            region = (
                self.window_rect[0] + region[0],
                self.window_rect[1] + region[1],
                region[2],
                region[3]
            )
        return pyautogui.screenshot(region=region)

    def find_image(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                logger.info(f"找到图像: {image_path} 在 {center}")
                return (center.x, center.y)
        except Exception as e:
            logger.error(f"查找图像失败: {e}")
        return None

    def click_image(self, image_path: str, confidence: float = 0.8) -> bool:
        location = self.find_image(image_path, confidence)
        if location:
            self.click(location[0], location[1], relative=False)
            return True
        return False
