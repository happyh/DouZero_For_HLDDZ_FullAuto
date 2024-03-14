import GameHelper as gh
from GameHelper import GameHelper
import cv2
import numpy as np

import win32gui

def callback(hwnd, extra):
    text = win32gui.GetWindowText(hwnd)
    clsname = win32gui.GetClassName(hwnd)
    print('窗口句柄:%s; 窗口标题：%s; 窗口类名: %s' % (hwnd, text, clsname))

#win32gui.EnumWindows(callback, None)

GameHelper = GameHelper()

img = cv2.imread("test_pic/5.png")
#img, _ = GameHelper.Screenshot(classname="D3JJ7GAME_GENT1001_2000")
img = cv2.cvtColor(np.asarray(img), cv2.COLOR_BGR2RGB)
img = gh.DrawRectWithText(img, (740, 637, 170, 50), "test")

gh.ShowImg(img)
