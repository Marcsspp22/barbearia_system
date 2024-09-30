from PyQt5 import QtWidgets, QtGui, QtCore
import sys

class ShadowButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.initUI()

    def initUI(self):
        # Estilo do botão
        self.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: black;
                border: 1px solid #555555;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)

        # Adicionar efeito de sombra
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(3, 3)
        shadow.setColor(QtGui.QColor(0, 0, 0, 200))
        self.setGraphicsEffect(shadow)

        # Definir tamanho fixo para o botão
        self.setFixedSize(250, 60)

class MenuWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Configurações da janela
        self.setWindowTitle('Menu - Sistema de Barbearia')
        self.setGeometry(100, 100, 1200, 900)
        self.setStyleSheet("background-color: black;")
        self.showMaximized()  # Abrir em janela maximizada

        # Layout principal
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)  # Margens da janela
        layout.setSpacing(20)

        # Espaço para o logo
        self.logo_label = QtWidgets.QLabel(self)
        self.logo_label.setPixmap(QtGui.QPixmap('Red and Black Illustrative Barber Shop Logo.png'))
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Widget para a fileira de botões
        buttons_widget = QtWidgets.QWidget(self)
        buttons_widget.setStyleSheet("background-color: black;")
        
        # Layout da fileira de botões
        button_layout = QtWidgets.QVBoxLayout(buttons_widget)
        button_layout.setContentsMargins(20, 20, 20, 20)
        button_layout.setSpacing(20)
        button_layout.setAlignment(QtCore.Qt.AlignCenter)

        # Lista de botões
        button_names = ["Cadastrar cliente", "Agenda", "Fluxo de Caixa", "Serviços", "Relatórios"]
        self.buttons = {}

        for name in button_names:
            button = ShadowButton(name, self)
            button.clicked.connect(self.button_clicked)
            button_layout.addWidget(button)
            self.buttons[name] = button

        # Adicionar a fileira de botões ao layout principal
        layout.addWidget(buttons_widget)

        # Definir layout principal
        self.setLayout(layout)

    def button_clicked(self):
        button_text = self.sender().text()
        if button_text == "Agenda":
            self.open_agenda()
        elif button_text == "Serviços":
            self.open_servicos()
        elif button_text == "Cadastrar cliente":
            self.open_cadastra()
        elif button_text == "Relatórios":
            self.open_relatorios()
        elif button_text == "Fluxo de Caixa":
            self.open_fluxoCaixa()
            
    def open_fluxoCaixa(self):
        import fluxoCaixa
        self.CashFlowWindow = fluxoCaixa.CashFlowWindow()
        self.CashFlowWindow.show()
     
    def open_relatorios(self):
        import relatorios
        self.DashboardWindow = relatorios.DashboardWindow()
        self.DashboardWindow.show()
                
    def open_cadastra(self):
        import cadastroCliente
        self.CadastroClienteDialog = cadastroCliente.CadastroClienteDialog()
        self.CadastroClienteDialog.show()
            
    def open_servicos(self):
        import servicos
        self.ServiceRegistrationDialog = servicos.ServiceRegistrationDialog()
        self.ServiceRegistrationDialog.show()

    def open_agenda(self):
        import agenda
        self.agenda_window = agenda.AgendaWindow()
        self.agenda_window.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    menu_window = MenuWindow()
    menu_window.show()
    sys.exit(app.exec_())
