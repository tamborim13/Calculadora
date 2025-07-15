import sys
from main_window import MainWindow, Display,Info,Style, Button, ButtonGrid
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from variable import ARQUIVO_ICON

if __name__ == '__main__':
    # Cria a aplicação
    app = QApplication(sys.argv)
    window = MainWindow()
    Style.setupTheme(app)
    


    # Define o ícone
    icon = QIcon(str(ARQUIVO_ICON))
    window.setWindowIcon(icon)
    app.setWindowIcon(icon)

    # Info
    info = Info('sua conta')
    window.addWidgetToVLayout(info)

    # Display
    display = Display()
    window.addWidgetToVLayout(display)

    #GRID
    buttonsGrid = ButtonGrid(display, info, window)
    window.vLayout.addLayout(buttonsGrid)
    
    
    # Executa tudo
    window.adjustFixedSize()
    window.show()
    app.exec()