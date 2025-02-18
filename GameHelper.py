# -*- coding: utf-8 -*-
# Created by: Vincentzyx
import ctypes

import win32gui
import win32ui
import win32api
import win32con
from ctypes import windll
from PIL import Image
import cv2
import pyautogui
import pygame
import matplotlib.pyplot as plt
import numpy as np
import os
import time
from win32con import WM_LBUTTONDOWN, MK_LBUTTON, WM_LBUTTONUP, WM_MOUSEMOVE, WM_ACTIVATE, WA_ACTIVE

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QTime, QEventLoop
from skimage.metrics import structural_similarity as ssim

Pics = {}


def compare_images(image1, image2):
    img2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
    # 转换为灰度图
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 使用结构相似性指数（SSIM）比较相似度
    ssim_index, _ = ssim(gray1, gray2, full=True)
    return ssim_index


def ShowImg(image):
    plt.imshow(image)
    plt.show()


def DrawRectWithText(image, rect, text):
    img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    x, y, w, h = rect
    img2 = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    img2 = cv2.putText(img2, text, (x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    return Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))


def CompareCard(card):
    order = {"3": 0, "4": 1, "5": 2, "6": 3, "7": 4, "8": 5, "9": 6, "T": 7, "J": 8, "Q": 9, "K": 10, "A": 11, "2": 12,
             "X": 13, "D": 14}
    return order[card]


def CompareCardInfo(card):
    order = {"3": 0, "4": 1, "5": 2, "6": 3, "7": 4, "8": 5, "9": 6, "T": 7, "J": 8, "Q": 9, "K": 10, "A": 11, "2": 12,
             "X": 13, "D": 14}
    return order[card[0]]


def CompareCards(cards1, cards2):
    if len(cards1) != len(cards2):
        return False
    cards1.sort(key=CompareCard)
    cards2.sort(key=CompareCard)
    for i in range(0, len(cards1)):
        if cards1[i] != cards2[i]:
            return False
    return True


def GetListDifference(l1, l2):
    temp1 = []
    temp1.extend(l1)
    temp2 = []
    temp2.extend(l2)
    for i in l2:
        if i in temp1:
            temp1.remove(i)
    for i in l1:
        if i in temp2:
            temp2.remove(i)
    return temp1, temp2


def FindImage(fromImage, template, threshold=0.9):
    w, h, _ = template.shape
    fromImage = cv2.cvtColor(np.asarray(fromImage), cv2.COLOR_RGB2BGR)
    res = cv2.matchTemplate(fromImage, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = []
    for pt in zip(*loc[::-1]):
        points.append(pt)
    return points


def LocateOnImage(image, template, region=None, confidence=0.8):
    if region is not None:
        x, y, w, h = region
        imgShape = image.shape
        image = image[y:y + h, x:x + w, :]
    print("")
    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, maxLoc = cv2.minMaxLoc(res)
    if (res >= confidence).any():
        return region[0] + maxLoc[0], region[1] + maxLoc[1]
    else:
        return None


def LocateAllOnImage(image, template, region=None, confidence=0.8):
    if region is not None:
        x, y, w, h = region
        image = image[y:y + h, x:x + w]
    w, h = image.shape[1], image.shape[0]

    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= confidence)
    points = []
    for pt in zip(*loc[::-1]):
        points.append((pt[0], pt[1], w, h))
    return points


class GameHelper:
    def __init__(self):
        self.ScreenZoomRate = None
        self.counter = QTime()
        self.Pics = {}
        self.PicsCV = {}
        st = time.time()
        self.Handle = win32gui.FindWindow("UnityWndClass", None)
        self.Interrupt = False
        self.screen_width = 1284
        self.screen_height = 796
        #self.RealRate = (1440, 810)
        self.RealRate = (self.screen_width, self.screen_height)
        self.GetZoomRate()

        pic_path="./jj_pic"
        for file in os.listdir(pic_path):
            info = file.split(".")
            if info[1] == "png":
                tmpImage = Image.open(pic_path+"/" + file)
                imgCv = cv2.imread(pic_path+"/" + file)
                self.Pics.update({info[0]: tmpImage})
                self.PicsCV.update({info[0]: imgCv})

    def sleep(self, ms):
        self.counter.restart()
        while self.counter.elapsed() < ms:
            QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 50)

    def Screenshot(self, region=None,classname=None):  # -> (im, (left, top))
        try_count = 3
        success = False
        while try_count > 0 and not success:
            try:
                try_count -= 1
                classname = "D3JJ7GAME_GENT1001_2000"
                if classname == None:
                    self.Handle = win32gui.FindWindow("UnityWndClass", None)
                else:
                    self.Handle = win32gui.FindWindow(classname, None)
                win32gui.SetActiveWindow(self.Handle)
                hwnd = self.Handle
                left, top, right, bot = win32gui.GetWindowRect(hwnd)
                #print("原始大小：",left,top,right,bot)

                # 调整窗口大小
                win32gui.MoveWindow(hwnd, left, top, self.screen_width, self.screen_height, True)

                left, top, right, bot = win32gui.GetWindowRect(hwnd)
                #print("调整后大小：", left, top, right, bot, )

                self.RealRate = (self.screen_width, self.screen_height)
                width = int(self.screen_width)
                height = int(self.screen_height)
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                im = Image.frombuffer(
                    "RGB",
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1)
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                im = im.resize((width, height))
                if region is not None:
                    im = im.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))
                if result:
                    success = True
                    return im, (left, top)
            except Exception as e:
                print("截图时出现错误:", repr(e))
                self.sleep(200)
        return None, (0, 0)

    def GetZoomRate(self):
        self.ScreenZoomRate = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

    def LocateOnScreen(self, templateName, region, confidence=0.8, img=None):
        if img is not None:
            image = img
        else:
            image, _ = self.Screenshot()
        imgcv = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        return LocateOnImage(imgcv, self.PicsCV[templateName], region=region, confidence=confidence)

    def ClickOnImage(self, templateName, region=None, confidence=0.8, img=None):
        if img is not None:
            image = img
        else:
            image, _ = self.Screenshot()
        imgcv = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        result = LocateOnImage(imgcv, self.PicsCV[templateName], region=region, confidence=confidence)

        if result is not None:
            self.LeftClick(result)
            print("click @",result,",region=",region)

    def LeftClick(self, pos):
        x, y = pos
        x = (x / self.screen_width) * self.RealRate[0]
        y = (y / self.screen_height) * self.RealRate[1]
        x = int(x)
        y = int(y)

        left, top, _, _ = win32gui.GetWindowRect(self.Handle)
        m, n = int(left + x), int(top + y)
        client_pos = (x, y)

        win32api.SetCursorPos((m, n))
        # print(client_pos)

        tmp = win32api.MAKELONG(client_pos[0], client_pos[1])
        '''tmp2 = win32api.MAKELONG(m, n)

        win32gui.PostMessage(self.Handle, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        win32gui.SendMessage(self.Handle, win32con.WM_NCHITTEST, tmp2)

        htclient = win32gui.DefWindowProc(self.Handle, win32con.WM_NCHITTEST, 0, tmp)
        print(htclient)
        win32gui.SendMessage(self.Handle, win32con.WM_SETCURSOR, self.Handle,
                             ((htclient & 0xFFFF) | ((win32con.WM_MOUSEMOVE & 0xFFFF) << 16)))

        win32gui.SendMessage(self.Handle, win32con.WM_MOUSEMOVE, 0, tmp)'''

        win32gui.PostMessage(self.Handle, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        win32gui.SendMessage(self.Handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, tmp)
        win32gui.SendMessage(self.Handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, tmp)
        self.sleep(200)
        win32api.SetCursorPos((int(left + 1000), int(top + 550)))

    def LeftClick2(self, pos):
        x, y = pos
        x = (x / self.screen_width) * self.RealRate[0]
        y = (y / self.screen_height) * self.RealRate[1]
        x = int(x)
        y = int(y)

        left, top, _, _ = win32gui.GetWindowRect(self.Handle)
        m, n = int(left + x), int(top + y)
        client_pos = (x, y)

        win32api.SetCursorPos((m, n))
        # print(client_pos)

        tmp = win32api.MAKELONG(client_pos[0], client_pos[1])
        win32gui.PostMessage(self.Handle, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        # win32gui.PostMessage(self.Handle, win32con.WM_SETCURSOR, self.Handle, tmp)
        # win32gui.SendMessage(self.Handle, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, tmp)

        win32gui.SendMessage(self.Handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, tmp)
        win32gui.SendMessage(self.Handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, tmp)

    def MoveTo(self, pos):
        x, y = pos
        x = (x / self.screen_width) * self.RealRate[0]
        y = (y / self.screen_height) * self.RealRate[1]
        x = int(x)
        y = int(y)
        self.Handle = win32gui.FindWindow("UnityWndClass", None)
        left, top, _, _ = win32gui.GetWindowRect(self.Handle)
        x, y = int(left + x), int(top + y)

        pyautogui.moveTo(x, y)

    def play_sound(self, sound_file):
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
