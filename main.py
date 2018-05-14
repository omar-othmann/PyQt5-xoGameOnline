# XO-Online Game wroted by: Omar Othman
# 2018/11/05 - 02:11 PM



from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWebSockets, QtNetwork
from PyQt5.uic import loadUiType
import threading
import os
import sys
import time
from socketIO_client import SocketIO, LoggingNamespace

scriptDir = os.path.dirname(os.path.realpath(__file__))
FROM_MAIN,_ = loadUiType(os.path.join(os.path.dirname(__file__),"main.ui"))

class Switch(object):
    value = None

    def __new__(cls, value):
        cls.value = value
        return True


def case(*args):
    return any((arg == Switch.value for arg in args))


class Json:
    def __init__(self):
        self.json = None

    def set_json(self, json):
        self.json = json

    def get(self, key):
        if self.json is None:
            print("Error while you edit code!")
            return None
        if key in self.json:
            return self.json[key]
        return None

    
class Main(QMainWindow, FROM_MAIN):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.default_show()
        self.client = QtWebSockets.QWebSocket("",QtWebSockets.QWebSocketProtocol.Version13,None)
        self.client.error.connect(self.on_error)
        self.client.open(QUrl("ws://127.0.0.1:80"))
        self.client.connected.connect(self.on_connect)
        self.client.disconnected.connect(self.on_disconnect)
        self.client.textMessageReceived.connect(self.on_message)
        self.button_search.clicked.connect(self.on_search_click)
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'icon.png'))
        self.setWindowTitle("XO Online game")
        self.isPlaying = False
        self.b_1 = False
        self.b_2 = False
        self.b_3 = False
        self.b_4 = False
        self.b_5 = False
        self.b_6 = False
        self.b_7 = False
        self.b_8 = False
        self.b_9 = False
        self.i_am = False
        self.button_1.clicked.connect(self.click_1)
        self.button_2.clicked.connect(self.click_2)
        self.button_3.clicked.connect(self.click_3)
        self.button_4.clicked.connect(self.click_4)
        self.button_5.clicked.connect(self.click_5)
        self.button_6.clicked.connect(self.click_6)
        self.button_7.clicked.connect(self.click_7)
        self.button_8.clicked.connect(self.click_8)
        self.button_9.clicked.connect(self.click_9)
    def on_error(self, code):
        self.label_status_text.setText("خطأ: "+str(code))
        
    def on_message(self, msg):
        try: packet = eval(msg)
        except: return
        json = Json()
        json.set_json(packet)
        space = json.get("space")
        if space == "get key":
            key = json.get("key")
            self.label_id_player.setText(key)
        if space == "play":
            status = json.get("status")
            if status is None:
                play = json.get("play")
                wid = json.get("with")
                are = json.get("are")
                self.label_player_name.setText(wid)
                QMessageBox.information(self, "بدء اللعب", "تم بدء اللعبة مع: "+str(wid))
                self.isPlaying = True
                self.i_am = play
                if play:
                    self.label_play_now.setText("انت")
                else:
                    self.label_play_now.setText("المنافس")
                form = "<html><body><center><h4>{}</h4></center></body></html>".format(are)
                self.label_you_are.setText(form)
            elif status == "re":
                play = json.get("play")
                you = json.get("you")
                key = str(json.get("key"))
                if play:
                    self.label_play_now.setText("المنافس")
                    self.i_am = False
                else:
                    self.label_play_now.setText("انت")
                    self.i_am = True
                i_m = str(self.label_you_are.text()).split("<h4>")[1].split("</h4>")[0]
                font = QFont()
                font.setPointSize(20)
                if you:
                    form = i_m
                else:
                    i_m = "X" if i_m == "O" else "O"
                    form = i_m
                while Switch(key):
                    if case("1"):
                        self.button_1.setText(form)
                        self.button_1.setFont(font)
                        self.b_1 = True
                        break
                    if case("2"):
                        self.button_2.setText(form)
                        self.button_2.setFont(font)
                        self.b_2 = True
                        break
                    if case("3"):
                        self.button_3.setText(form)
                        self.button_3.setFont(font)
                        self.b_3 = True
                        break
                    if case("4"):
                        self.button_4.setText(form)
                        self.button_4.setFont(font)
                        self.b_4 = True
                        break
                    if case("5"):
                        self.button_5.setText(form)
                        self.button_5.setFont(font)
                        self.b_5 = True
                        break
                    if case("6"):
                        self.button_6.setText(form)
                        self.button_6.setFont(font)
                        self.b_6 = True
                        break
                    if case("7"):
                        self.button_7.setText(form)
                        self.button_7.setFont(font)
                        self.b_7 = True
                        break
                    if case("8"):
                        self.button_8.setText(form)
                        self.button_8.setFont(font)
                        self.b_8 = True
                        break
                    if case("9"):
                        self.button_9.setText(form)
                        self.button_9.setFont(font)
                        self.b_9 = True
                        break
                    break
            elif status == "win-you":
                QMessageBox.information(self, "مبروك", "لقد ربحت!")
                self.backup_to_default()
            elif status == "lost-you":
                QMessageBox.information(self, "للأسف", "لقد خسرت")
                self.backup_to_default()
            elif status == "vs":
                QMessageBox.information(self, "تعادل", "لم يربح احد منكم لان النتيجة تعادل!")
                self.backup_to_default()
        if space == "invite":
            status = json.get("status")
            if status == "playing":
                QMessageBox.information(self, "المعذرة", "صديقك لديه لعبى اخرى. يرجى اعادة محاولة لاحقا")
            # if status == "success":
                # QMessageBox.information(self, "تم", "تم ارسال طلب الدعوة بنجاح. يرجى الانتظار حتى يتم استقبال اللعبة")
            if status == "offline":
                QMessageBox.information(self, "للأسف", "ان صديقك الذي ادخلت رقمه. غير متصل او الرقم خاطئ")
            # if status == "no":
                # QMessageBox.information(self, "للأسف", "لم يوافق صديقك للعب معك")
                # self.backup_to_default()
                
        """if space == "accept":
            _id = json.get("with")
            msg = QMessageBox(QMessageBox.Question, "دعوة للعب", "دعاك {} للعب معه. هل تقبل؟".format(_id), QMessageBox.Yes | QMessageBox.No )
            rep = msg.exec_()
            if rep == QMessageBox.Yes:
                self.client.sendTextMessage(str({"space": "accept", "id": _id, "status": "yes"}))
            else:
                self.client.sendTextMessage(str({"space": "accept", "id": _id, "status": "no"}))"""
    def backup_to_default(self):
        self.label_you_are.setText("لم يتم تحديد بعد")
        self.button_1.setText("1")
        self.button_2.setText("2")
        self.button_3.setText("3")
        self.button_4.setText("4")
        self.button_5.setText("5")
        self.button_6.setText("6")
        self.button_7.setText("7")
        self.button_8.setText("8")
        self.button_9.setText("9")
        self.label_player_name.setText("لم يتم البدء بعد")
        self.label_play_now.setText("غير معروف بعد")
        self.isPlaying = False
        self.i_am = False
        self.b_1 = False
        self.b_2 = False
        self.b_3 = False
        self.b_4 = False
        self.b_5 = False
        self.b_6 = False
        self.b_7 = False
        self.b_8 = False
        self.b_9 = False
    def on_connect(self):
        self.label_status_text.setText("متصل")
        self.client.sendTextMessage(str({"space": "get key"}))
    def on_disconnect(self):
        self.label_status_text.setText("قطع الاتصال")
        

    def on_reconnect(self):
        self.label_status_text.setText("اعادة الاتصال")

    def default_show(self):
        self.player_id_edit.setPlaceholderText("رقم التعريف الخاص بصديقك")
        self.label_you_are.setText("لم يتم تحديد بعد")
        self.label_status_text.setText("جاري الاتصال")
        self.label_id_player.setText("N/A")
        self.label_8.setOpenExternalLinks(True)
        self.label_play_now.setText("غير معروف بعد")

    def on_search_click(self):
        if self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لديك للعبة بالفعل")
            return
        code = self.player_id_edit.text()
        if code:
            data = {"space": "search", "key": code}
            self.client.sendTextMessage(str(data))
        else:
            data = {"space": "search random"}
            self.client.sendTextMessage(str(data))
        self.label_player_name.setText("جاري البحث..")

    def click_1(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_1:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "1"}
            self.client.sendTextMessage(str(data))

    def click_2(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_2:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "2"}
            self.client.sendTextMessage(str(data))
    def click_3(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_3:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "3"}
            self.client.sendTextMessage(str(data))

    def click_4(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_4:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "4"}
            self.client.sendTextMessage(str(data))

    def click_5(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_5:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "5"}
            self.client.sendTextMessage(str(data))

    def click_6(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_6:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "6"}
            self.client.sendTextMessage(str(data))

    def click_7(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_7:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "7"}
            self.client.sendTextMessage(str(data))

    def click_8(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_8:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "8"}
            self.client.sendTextMessage(str(data))

    def click_9(self):
        if not self.isPlaying:
            QMessageBox.information(self, "غير مسموح", "لم يتم بدء اللعبة بعد. قم بالضغط على زر بحث عن لاعب للبحث العشوائي او ضع رقم صديقك ثم اضغط على بحث عن لاعب")
        elif not self.i_am:
            QMessageBox.information(self, "غير مسموح", "الدور لمنافسك وليس لك")
        elif self.b_9:
            QMessageBox.information(self, "مستخدم", "تم استخدام هذا الزر")
        else:
            data = {"space": "data", "set": "9"}
            self.client.sendTextMessage(str(data))
        

def main():
    app=QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
