from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import pyodbc
import menu  # Importar o módulo menu

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Configurações da janela
        self.setWindowTitle('Sistema de Barbearia - Login')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black;")

        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        layout = QtWidgets.QVBoxLayout()

        self.logo_label = QtWidgets.QLabel(self)
        self.logo_label.setPixmap(QtGui.QPixmap('Red and Black Illustrative Barber Shop Logo.png'))
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        central_widget = QtWidgets.QWidget(self)
        central_widget.setFixedSize(400, 350)
        central_widget.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
        """)

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        central_widget.setGraphicsEffect(shadow)

        login_layout = QtWidgets.QVBoxLayout(central_widget)
        login_layout.setContentsMargins(30, 30, 30, 30)

        self.user_input = QtWidgets.QLineEdit(self)
        self.user_input.setPlaceholderText('Usuário')
        self.user_input.setStyleSheet("""
            padding: 10px;
            border: 1px solid gray;
            border-radius: 10px;
            font-size: 16px;
        """)
        login_layout.addWidget(self.user_input)


        login_layout.addSpacing(20)

        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText('Senha')
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setStyleSheet("""
            padding: 10px;
            border: 1px solid gray;
            border-radius: 10px;
            font-size: 16px;
        """)
        login_layout.addWidget(self.password_input)

        self.remember_me = QtWidgets.QCheckBox("Lembrar-me", self)
        self.remember_me.setStyleSheet("font-size: 14px;")

        remember_layout = QtWidgets.QHBoxLayout()
        remember_layout.addWidget(self.remember_me)
        login_layout.addLayout(remember_layout)

        # Espaçamento
        login_layout.addSpacing(20)

        # Botão de login
        self.login_button = QtWidgets.QPushButton('Login', self)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.login_button.clicked.connect(self.check_login)
        login_layout.addWidget(self.login_button)

        # Adicionar caixa de login ao layout principal
        layout.addWidget(central_widget, alignment=QtCore.Qt.AlignCenter)

        # Definir layout principal
        self.setLayout(layout)

        # Inicializar janela de menu como persistente
        self.menu_window = None

    def check_login(self):
        username = self.user_input.text()
        password = self.password_input.text()

        conn = None
        try:
            # Conectar ao banco de dados
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()

            # Verificar as credenciais
            cursor.execute("SELECT * FROM Usuarios WHERE NomeUsuario = ? AND Senha = ?", (username, password))
            user = cursor.fetchone()

            if user:
                self.show_message('Login', 'Login bem-sucedido!', QtWidgets.QMessageBox.Information)
                self.open_menu()  
            else:
                self.show_message('Login', 'Nome de usuário ou senha incorretos.', QtWidgets.QMessageBox.Warning)

        except pyodbc.Error as e:
            self.show_message('Erro', f'Erro ao conectar ao banco de dados: {e}', QtWidgets.QMessageBox.Critical)
        finally:
            if conn:
                conn.close()

    def show_message(self, title, message, icon):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: black;
                color: black;
                font-size: 14px;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                color: white;
                background-color: #4CAF50;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        msg_box.exec_()

    def open_menu(self):
        if self.menu_window is None:
            self.menu_window = menu.MenuWindow()  # Criar uma instância da janela de menu
        self.menu_window.show()  # Mostrar a janela de menu
        self.close()  # Fechar a janela de login

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
