import random, sys, os, logging
from pickle import load, dump
from PyQt5 import QtGui, uic, QtMultimedia
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox

__author__ = 'Mihir Shrestha'

class TicTacToe(QMainWindow):
    """A game of craps."""

    def __init__(self, parent = None):
        """Build a game with two dice."""

        super().__init__()
        uic.loadUi("tictactoe.ui", self)

        self.buttons = [self.button1, self.button2, self.button3, self.button4, self.button5, self.button6,
                        self.button7, self.button8, self.button9]
        self.used = []

        try:
            with open("tictactoe.pkl", 'rb') as pickledData:
                self.pickledSelfData = load(pickledData)
                self.user, self.computer, self.wins, self.losses, self.draws, self.goFirst, self.result, self.btnStatus, self.logging = self.pickledSelfData
                index = 0
                for button in self.buttons:
                    button.setText(self.btnStatus[index][1])
                    button.setEnabled(self.btnStatus[index][0])
                    if button.isEnabled():
                        self.used.append(button)
                    index += 1
                self.updateUI()
                if self.logging:
                    logging.info("Successfuly retrieved save game and applied it")

        except FileNotFoundError:
            self.logging = True
            self.user = 'X'
            self.result = "Welcome to Tic Tac Toe!"
            self.computer = 'O'
            self.wins = 0
            self.losses = 0
            self.draws = 0
            self.goFirst = True
            if self.logging:
                logging.info("Could not retrieve data from save game")

        self.values = (self.user, self.computer)
        self.corners = [self.button1, self.button3, self.button7, self.button9]
        self.edges = [self.button8, self.button4, self.button6, self.button2]
        self.notes = {
            "win": QtMultimedia.QSound("win.wav"),
            "lose": QtMultimedia.QSound("lose.wav"),
            "circle": QtMultimedia.QSound("circle.wav"),
            "cross": QtMultimedia.QSound("cross.wav")
        }

        self.actionSettings.triggered.connect(self.showSettings)

        self.button1.clicked.connect(lambda: self.play(self.button1, self.user))
        self.button2.clicked.connect(lambda: self.play(self.button2, self.user))
        self.button3.clicked.connect(lambda: self.play(self.button3, self.user))
        self.button4.clicked.connect(lambda: self.play(self.button4, self.user))
        self.button5.clicked.connect(lambda: self.play(self.button5, self.user))
        self.button6.clicked.connect(lambda: self.play(self.button6, self.user))
        self.button7.clicked.connect(lambda: self.play(self.button7, self.user))
        self.button8.clicked.connect(lambda: self.play(self.button8, self.user))
        self.button9.clicked.connect(lambda: self.play(self.button9, self.user))
        self.newGameButton.clicked.connect(self.restartGame)

        if self.logging:
            logging.info("Initialized all buttons and verified that they exist.")

    def closeEvent(self, event):
        if self.logging:
            logging.info("Reached close event method. User is trying to end game")
        quit_msg = "Are you sure you want to exit Tic Tac Toe?\nAll changes will be saved automatically."
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        self.btnStatus = []

        for button in self.buttons:
            self.btnStatus.append((button.isEnabled(), button.text()))

        if self.logging:
            logging.info("Saving button status")

        self.pickleinfo = [self.user, self.computer, self.wins, self.losses, self.draws, self.goFirst, self.result, self.btnStatus, self.logging]

        if reply == QMessageBox.Yes:
            if self.logging:
                logging.info("User ended game")
            event.accept()
            with open("tictactoe.pkl", 'wb') as ticPickle:
                dump(self.pickleinfo, ticPickle)
            exit()
        else:
            if self.logging:
                logging.info("User didn't end game")
            event.ignore()

    def changePlayer(self, arg):
        self.user = arg
        if arg == 'O':
            if self.logging:
                logging.info("User changed player to O")
            self.computer = "X"
            settings.oRadio.setChecked(True)
        else:
            if self.logging:
                logging.info("User changed player to X")
            self.computer = "O"
            settings.xRadio.setChecked(True)

    def goesFirst(self, arg):
        if self.logging:
            logging.info("Reached go first method")
        self.goFirst = arg
        if self.logging:
            logging.info("User wants to go first: {}".format(self.goFirst))

    def showSettings(self):
        if self.logging:
            logging.info("User chose to show settings")
        settings.show()

    def play(self, arg, value):
        if self.user == 'O':
            self.notes["circle"].play()
        else:
            self.notes["cross"].play()

        self.makeMove(arg, value)
        if self.logging:
            logging.info("User put {} to {}".format(value, arg))
        status = self.checkWinner()
        if status:
            if self.logging:
                logging.info("User won!")
            self.strikeOut(status)
            self.notes["win"].play()
            self.result = "You win!"
            self.wins += 1
            self.endGame()
            self.updateUI()
            return

        self.computerLogic()
        if self.logging:
            logging.info("Computer is making its move right now")
        status = self.checkWinner()

        if status:
            if self.logging:
                logging.info("Computer won!")
            self.strikeOut(status)
            self.notes["lose"].play()
            self.result = "You lose!"
            self.losses += 1
            self.endGame()
            self.updateUI()
            return

        if self.checkBoard():
            if self.logging:
                logging.info("Nobody won!")
            self.result = "You draw!"
            self.draws += 1
            self.updateUI()
            self.endGame()
            return

    def restartGame(self):
        for button in self.buttons:
            button.setEnabled(True)
            button.setText("")
            temp = button.font()
            temp.setStrikeOut(False)
            temp.setBold(False)
            button.setFont(temp)
        self.used = []
        self.result = "Another round of Tic Tac Toe!"
        if self.goFirst != True:
            self.computerLogic()
        if self.logging:
            logging.info("User chose to restar game")
        self.updateUI()

    def updateUI(self):
        if self.logging:
            logging.info("Updated UI")
        self.lossesLabel.setText(str(self.losses))
        self.winsLabel.setText(str(self.wins))
        self.drawsLabel.setText(str(self.draws))
        self.resultsLabel.setText(self.result)

    def checkBoard(self):
        if self.logging:
            logging.info("Checking if buttons are enabled")
        for button in self.buttons:
            if button.isEnabled():
                return False
        return True

    def strikeOut(self, args):
        if self.logging:
            logging.info("Striking out winning values")
        for arg in args:
            temp = arg.font()
            temp.setStrikeOut(True)
            temp.setBold(True)
            arg.setFont(temp)

    def makeMove(self, arg, value, boolean=True, append=True):
        if self.logging:
            logging.info("Inside make move function")
        arg.setText(value)
        if boolean:
            arg.setEnabled(False)
        if append:
            self.used.append(arg)

    def deleteMove(self, arg):
        if self.logging:
            logging.info("Inside delete move function")
        arg.setText("")
        arg.setEnabled(True)
        if arg in self.used:
            self.used.remove(arg)

    def endGame(self):
        if self.logging:
            logging.info("Inside end settings")
        for button in self.buttons:
            button.setEnabled(False)

    def computerLogic(self):
        # First check if computer can be a winner
        if self.logging:
            logging.info("Checking if computer can be a winner")
        for button in self.buttons:
            if button.isEnabled():
                self.makeMove(button, self.computer)
                if self.checkWinner():
                    return
                else:
                    self.deleteMove(button)

        # Second check if player can be a winner
        if self.logging:
            logging.info("Checking if player can be a winner")
        for button in self.buttons:
            if button.isEnabled():
                self.makeMove(button, self.user)
                if self.checkWinner():
                    self.makeMove(button, self.computer)
                    return
                self.deleteMove(button)

        # Go to center if player uses corner in first try
        if self.logging:
            logging.info("Going to center if player takes corner in first try")
        if len(self.used) == 1 and self.used[0] in self.corners:
            self.makeMove(self.button5, self.computer)
            return

        # Take the corner if available
        if self.logging:
            logging.info("Taking the corner if available")
        random.shuffle(self.corners)
        for corner in self.corners:
            if corner.isEnabled():
                self.makeMove(corner, self.computer)
                return

        # Take the middle position if available
        if self.logging:
            logging.info("Taking the middle position if available")
        if self.button5.isEnabled():
            self.makeMove(self.button5, self.computer)
            return

        # Random
        if self.logging:
            logging.info("Picking a random box")
        random.shuffle(self.buttons)
        for button in self.buttons:
            if button.isEnabled():
                self.makeMove(button, self.computer)
                return

    def checkWinner(self):
        if self.logging:
            logging.info("Checking if there is a winner")
        if self.button1.text() == self.button2.text() == self.button3.text() and self.button1.text() in self.values:
            return self.button1, self.button2, self.button3

        elif self.button4.text() == self.button5.text() == self.button6.text() and self.button4.text() in self.values:
            return self.button4, self.button5, self.button6

        elif self.button7.text() == self.button8.text() == self.button9.text() and self.button7.text() in self.values:
            return self.button7, self.button8, self.button9

        elif self.button1.text() == self.button4.text() == self.button7.text() and self.button1.text() in self.values:
            return self.button1, self.button4, self.button7

        elif self.button2.text() == self.button5.text() == self.button8.text() and self.button2.text() in self.values:
            return self.button2, self.button5, self.button8

        elif self.button3.text() == self.button6.text() == self.button9.text() and self.button3.text() in self.values:
            return self.button3, self.button6, self.button9

        elif self.button1.text() == self.button5.text() == self.button9.text() and self.button1.text() in self.values:
            return self.button1, self.button5, self.button9

        elif self.button7.text() == self.button5.text() == self.button3.text() and self.button7.text() in self.values:
            return self.button7, self.button5, self.button3
        return False

    # def checkFull(self):
    #     logging.info("Checking if board is full")
    #     for button in self.buttons:
    #         if button.text() == "":
    #             return False
    #     return True

class Settings(QDialog):
    def __init__(self, parent = None):
        """Build a game with two dice."""
        if game.logging:
            logging.info("Initialized settings UI")

        super().__init__()
        uic.loadUi("settings.ui", self)
        self.goFirstCheck.setChecked(True)
        if game.user == "X":
            self.xRadio.setChecked(True)
        else:
            self.oRadio.setChecked(True)

        if game.logging:
            self.loggingCheck.setChecked(True)
        else:
            self.loggingCheck.setChecked(False)

        if game.goFirst:
            self.goFirstCheck.setChecked(True)
        else:
            self.goFirstCheck.setChecked(False)

        self.buttonBox.accepted.connect(self.saveSettings)
        self.buttonBox.rejected.connect(self.cancelSettings)
        self.deleteSaveBtn.clicked.connect(self.deleteSave)
        self.clearLog.clicked.connect(self.deleteLog)
        self.openLog.clicked.connect(self.openLogFile)

    def openLogFile(self):
        # os.startfile('tictactoe.log')
        logText = LogText()
        with open("tictactoe.log", 'r') as readLog:
            log = readLog.read()
            logText.logTextStuff.setPlainText(log)
        logText.show()
        logText.exec_()

    def deleteLog(self):
        if "tictactoe.log" in os.listdir():
            open("tictactoe.log", 'w').close()
            game.result = "LOG CLEARED!"
        else:
            game.result = "NO LOG FOUND!!!!"
        game.updateUI()

    def cancelSettings(self):
        if game.logging:
            logging.info("Cancelled Settings")
        if game.user == "X":
            self.xRadio.setChecked(True)
        else:
            self.oRadio.setChecked(True)

        if game.goFirst:
            self.goFirstCheck.setChecked(True)
        else:
            self.goFirstCheck.setChecked(False)

        if game.logging == True:
            self.loggingCheck.setChecked(True)
        else:
            self.loggingCheck.setChecked(False)


    def saveSettings(self):
        if self.oRadio.isChecked():
            game.changePlayer('O')
        elif self.xRadio.isChecked():
            game.changePlayer('X')

        self.goFirst()

        if self.loggingCheck.isChecked():
            game.logging = True
        else:
            game.logging = False
        game.restartGame()
        if game.logging:
            logging.info("Saved settings")

    def goFirst(self):
        if self.goFirstCheck.isChecked():
            game.goesFirst(True)
        else:
            game.goesFirst(False)
        if game.logging:
            logging.info("Saved settings to go first or not")

    def deleteSave(self):
        if "tictactoe.pkl" in os.listdir():
            os.remove("tictactoe.pkl")
            game.result = "Save deleted! Restart game to see changes!"
            game.wins = 0
            game.losses = 0
            game.draws = 0
            if game.logging:
                logging.info("Deleted saved!")
        else:
            game.result = "Save not found!"
            if game.logging:
                logging.info("Save not found")
        game.updateUI()

class LogText(QDialog):
    def __init__(self, parent = None):
        if game.logging:
            logging.info("Initialized Logging Text File")

        super().__init__()
        uic.loadUi("logFileText.ui", self)


if __name__== "__main__":
    app = QApplication(sys.argv)
    logger = logging.basicConfig(filename='tictactoe.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s Ln %(lineno)d: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    game = TicTacToe()
    settings = Settings()
    game.show()
    sys.exit(app.exec_())