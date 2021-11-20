from PyQt5.QtCore import QCoreApplication, QObject, QThread, pyqtSignal, QProcess
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QActionGroup
from PyQt5.QtGui import QIcon
import sys
import json
from pynput import keyboard
import pyautogui
import configparser
import requests

json_data = '{"agents":["Astra","Breach","Brimstone","Chamber","Cypher","Jett","KAY\/O","Killjoy","Omen","Phoenix","Raze","Reyna","Sage","Skye","Sova","Viper","Yoru"],"coordinates":[[625,929],[709,929],[793,929],[877,929],[961,929],[1045,929],[1129,929],[1213,929],[1297,929],[625,1013],[709,1013],[793,1013],[877,1013],[961,1013],[1045,1013],[1129,1013],[1213,1013]],"button":[960,808]}'

def load_data():
    config = configparser.ConfigParser()
    config.read("config.ini")
    config = config["Settings"]

    if config["PullData"] == "no":
        data = json.loads(json_data)
    else:
        data = requests.get("https://raw.githubusercontent.com/JannisMcMak/valorant-instalock/main/data.json").json()
    
    return data, config


global data, config
data, config = load_data()

app = QApplication(sys.argv)


class Instalocker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True
        
        self.agents = self.load_agent_list()
        self.choice = config["DefaultAgent"]

    def on_press(self, key):
        try:
            if str(key).split(".")[1] == config["Hotkey"].lower():
                self.lock_in()
                if config["AutoClose"] == "yes":
                    self.finished.emit()
                    self.stop()

        except:
            return


    def listen(self):            
        with keyboard.Listener(on_press=self.on_press) as listener:
            print("Listening...")
            listener.join()

        print("Finished listening...")

    def load_agent_list(self):
        agents = data["agents"]
        for agent in agents:
            if agent in config["DisabledAgents"].split(", "):
                agents.remove(agent)   
        return agents

    def lock_in(self):
        coords = data["coordinates"][self.agents.index(self.choice)]

        pyautogui.moveTo(coords[0], coords[1])
        pyautogui.click()
        pyautogui.click()
        QThread.msleep(int(float(config["Delay"]) * 100))
        pyautogui.moveTo(data["button"][0], data["button"][1])
        pyautogui.click()
        pyautogui.click()


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
            
            action.setEnabled(agent not in config["DisabledAgents"].split(", "))
            menu2.addAction(action)
            agent_group.addAction(action)

        agent_group.setExclusive(True)
        agent_group.triggered.connect(self.onChoice)
        
        menu.addAction('Reload').triggered.connect(self.reload)
        menu.addAction('Exit').triggered.connect(self.stop)

        self.setContextMenu(menu)


        self.thread = QThread()
        self.worker = Instalocker()
        self.stop_signal.connect(self.worker.stop)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.listen)
        self.worker.finished.connect(self.stop)

    
    def onChoice(self, action):
        self.worker.choice = action.text()

    def reload(self, action):
        QCoreApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def stop(self, action):
        self.thread.quit()
        self.worker.stop()
        self.worker.deleteLater()
        self.thread.deleteLater()
        app.quit()


def main():
    w = App()

    w.thread.start()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    

