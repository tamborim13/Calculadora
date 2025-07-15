import math
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QKeyEvent
from variable import BIG_FONT_SIZE, MINIMUM_WIDTH, TEXT_MARGIN, SMALL_FONT_SIZE, MEDIUM_FONT_SIZE
import qdarkstyle
from variable import (DARKER_PRIMARY_COLOR, DARKEST_PRIMARY_COLOR,
                       PRIMARY_COLOR)
from utils import isEmpty, isNumOrDot, isValidNumber, converToNumber
from typing import TYPE_CHECKING


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        # Configurando o layout básico
        self.cw = QWidget()
        self.vLayout = QVBoxLayout()
        self.cw.setLayout(self.vLayout)
        self.setCentralWidget(self.cw)

        # Título da janela
        self.setWindowTitle('Calculadora')

    def adjustFixedSize(self):
        # Última coisa a ser feita
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())

    def addWidgetToVLayout(self, widget: QWidget):
        self.vLayout.addWidget(widget)

    def makeMsgBox(self):
        return QMessageBox(self)
        


class Display(QLineEdit):
    eqPressed = Signal()
    delPressed = Signal()
    clearPressed = Signal()

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.configStyle()

    
    def configStyle (self):
        margins = [TEXT_MARGIN for _ in  range(4)]
        self.setStyleSheet(f'font-size:{BIG_FONT_SIZE}px;')
        self.setMinimumHeight(BIG_FONT_SIZE * 2)
        self.setMinimumWidth(MINIMUM_WIDTH)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setTextMargins(*margins)

    def keyPressEvent(self, event: QKeyEvent)-> None:
        text = event.text().strip()
        key = event.key()
        KEYS = Qt.Key

        isEnter = key in [KEYS.Key_Enter, KEYS.Key_Return]
        isDelete = key in [KEYS.Key_Backspace, KEYS.Key_Delete]
        isEsc = key in [KEYS.Key_Escape]

        if isEnter:
            self.eqPressed.emit()
            return event.ignore()

        if isDelete:
            self.delPressed.emit()
            return event.ignore()

        if isEsc:
            self.clearPressed.emit()
            return event.ignore()

        # Não passar daqui se não tiver texto
        if isEmpty(text):
            return event.ignore()

        print('Texto', text)


class Info(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.configStylee()

    def configStylee(self):
        self.setStyleSheet(f'font-size: {SMALL_FONT_SIZE}px;')
        self.setAlignment(Qt.AlignmentFlag.AlignRight)


class Style:
    @staticmethod
    def setupTheme(app):
        base_style = qdarkstyle.load_stylesheet_pyside6()
        
        # QSS adicional
        extra_qss = f"""
            QPushButton[cssClass="specialButton"] {{
                color: #fff;
                background: {PRIMARY_COLOR};
            }}
            QPushButton[cssClass="specialButton"]:hover {{
                color: #fff;
                background: {DARKER_PRIMARY_COLOR};
            }}
            QPushButton[cssClass="specialButton"]:pressed {{
                color: #fff;
                background: {DARKEST_PRIMARY_COLOR};
            }}
        """

        # Aplica o estilo base + extra
        app.setStyleSheet(base_style + extra_qss)

class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()
            
    def configStyle(self):
        font = self.font()
        font.setPixelSize(MEDIUM_FONT_SIZE)  
        font.setBold(True)                   
        self.setFont(font)                   

        self.setMinimumSize(60, 60)
        

class ButtonGrid (QGridLayout):
    def __init__(self, display:'Display', info:'Info', window:'MainWindow',
                  *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._gridMask = [
            ['C', '◀', '^', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['N',  '0', '.', '='],
        ]

        self.display = display
        self.info = info
        self.window = window
        self._equation = ''
        self._equationValueInitial = ''
        self._left = None
        self._right = None
        self._op = None

        self.equation = self._equationValueInitial
        self._makeGrid()

    @property
    def equation(self):
        return self._equation
    
    @equation.setter
    def equation(self, value):
        self._equation = value
        self.info.setText(value)


    def _makeGrid(self):
        self.display.eqPressed.connect(self._eq)
        self.display.delPressed.connect(self.display.backspace)  # ← aqui corrigido
        self.display.clearPressed.connect(self._clear)


        for i, rol in enumerate(self._gridMask):
            for j, buttonText in enumerate(rol):
                button = Button(buttonText)

                if not isNumOrDot(buttonText) and not isEmpty(buttonText):
                    button.setProperty('cssClass', 'specialButton')
                    self._makeConfigButton(button)

                self.addWidget(button, i, j)
                slot = self._makeSlot(self._insertTextButton, button)
                self._connectButton(button, slot)

    def _connectButton(self, button, slot):
        button.clicked.connect(slot)

    def _makeConfigButton(self, button):
        text = button.text()

        if text == 'C':
            self._connectButton(button, self._clear)

        if text == '◀':
            self._connectButton(button, self.display.backspace)

        if text == 'N':
            self._connectButton(button, self._inverteNegativo)

        if text in '+-/*^':
            self._connectButton(
                button,
                 self._makeSlot(self._operationClicked, button)
                )
            
        if text == '=':
            self._connectButton(button, self._eq)


    def _makeSlot(self, func, *args, **kwargs):
        @Slot(bool)
        def realSlot(_):
            func(*args, **kwargs)
        return realSlot
    
    @Slot()
    def _inverteNegativo(self):
        displayText = self.display.text()

        if not isValidNumber(displayText):
            return
        
        number = converToNumber(displayText) * -1

        self.display.setText(str(number))

    def _insertTextButton(self, button):
        buttonText = button.text()
        newDisplayValue = self.display.text() + buttonText

        if not isValidNumber(newDisplayValue):
            return

        self.display.insert(buttonText)
        self.display.setFocus()

    def _clear(self):
        self._left = None
        self._right = None
        self._op = None
        self.equation = self._equationValueInitial
        self.display.clear()

    def _operationClicked(self,button):
        buttonText = button.text() # +-*/
        displayText = self.display.text() #devera ser o numero _left
        self.display.clear() # limpa o display

        if not isValidNumber(displayText) and self._left is None:
            self.showError('Digite um número válido')
            return

        if self._left is None:
            self._left = converToNumber(displayText)

        self._op = buttonText
        self.equation = f'{self._left} {self._op} ??'

    @Slot()
    def _eq(self):
        displayText = self.display.text()

        if not isValidNumber(displayText) or self._left is None:
            self.showError('Conta Incompleta!')
            return
        
        self._right = converToNumber(displayText)
        self.equation = f'{self._left} {self._op} {self._right}'
        result = 'error'

        try:
            if '^' in self.equation and isinstance(self._left, int | float):
                result = math.pow(self._left, self._right)
            else:
                result = eval(self.equation)
        except ZeroDivisionError:
            self.showError('Divisão por zero')
        except OverflowError:
            self.showError('Essa conta não pode ser realizada')

        self.display.clear()
        self.info.setText(f'{self.equation} = {result}')
        self._left = result
        self._right = None
        self.display.setFocus()

        if result == 'error':
            self._left = None

    def showError(self, text: str):
        msgBox = self.window.makeMsgBox()
        msgBox.setWindowTitle('Erro')
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Icon.Critical)
        msgBox.exec()
        self.display.setFocus()

