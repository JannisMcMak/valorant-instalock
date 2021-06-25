from PyQt5.QtCore import QCoreApplication, QObject, QThread, pyqtSignal, QProcess
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QActionGroup
from PyQt5.QtGui import QIcon
import sys
import json
import keyboard
import pyautogui
import configparser
import os

json_data = '{"agents":["Astra","Breach","Brimstone","Cypher","Jett","KAY\/O","Killjoy","Omen","Phoenix","Raze","Reyna","Sage","Skye","Sova","Viper","Yoru"],"coordinates":[[667,929],[755,929],[826,929],[921,929],[1006,929],[1086,929],[1167,929],[1245,292],[661,1013],[751,1013],[835,1013],[919,1013],[1002,1013],[1089,1013],[1173,1013],[1249,1013]],"button":[960,808]}'

def load_data():
    data = json.loads(json_data)

    config = configparser.ConfigParser()
    config.read("config.ini")
    config = config["Settings"]
    
    return data, config


global data, config
data, config = load_data()


class Instalocker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True
        
        self.choice = config["DefaultAgent"]

    def listen(self):
        agents = data["agents"]
        for agent in agents:
            if agent in config["DisabledAgents"].split(","):
                agents.remove(agent)

        while self.continue_run:
            try:
                if keyboard.is_pressed(config["Hotkey"]):
                    print(self.choice)
                    coords = data["coordinates"][agents.index(self.choice)]

                    QThread.msleep(int(float(config["DefaultDelay"]) * 100))
                    pyautogui.moveTo(coords[0], coords[1])
                    QThread.msleep(int(float(config["DefaultDelay"]) * 100))
                    pyautogui.click()
                    QThread.msleep(int(float(config["DefaultDelay"]) * 100))
                    pyautogui.moveTo(data["button"][0], data["button"][1])
                    QThread.msleep(int(float(config["DefaultDelay"]) * 100))
                    pyautogui.click()

                    if config["AutoClose"] == "yes":
                        break
            except:
                    continue

        self.finished.emit()

    def stop(self):
        self.continue_run = False


class App(QSystemTrayIcon):
    stop_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(App, self).__init__(QIcon("logo/logo.png"), parent)


        self.setToolTip("Instalocker")
        self.show()


        menu = QMenu()
        menu2 = menu.addMenu("Choose agent")

        agent_group = QActionGroup(menu2)
        
        for agent in data["agents"]:
            action = QAction(agent, menu, checkable=True, checked=agent==config["DefaultAgent"])
            
            action.setEnabled(agent not in config["DisabledAgents"].split(","))
            menu2.addAction(action)
            agent_group.addAction(action)

        agent_group.setExclusive(True)
        agent_group.triggered.connect(self.onChoice)
        
        menu.addAction('Reload').triggered.connect(self.reload)
        menu.addAction('Exit').triggered.connect(app.quit)

        self.setContextMenu(menu)


        self.thread = QThread()
        self.worker = Instalocker()
        self.stop_signal.connect(self.worker.stop)
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)

        self.thread.started.connect(self.worker.listen)
        self.thread.finished.connect(self.worker.stop)

        self.worker.finished.connect(app.quit)

    
    def onChoice(self, action):
        self.worker.choice = action.text()

    def reload(self, action):
        QCoreApplication.quit()
        status = QProcess.startDetached(sys.executable, sys.argv)
        print(status)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = App()

    w.thread.start()


    sys.exit(app.exec_())
