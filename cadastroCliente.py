from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import sys

class CadastroClienteDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Novo Cliente")
        self.setFixedSize(600, 600)

        # Layout principal
        layout = QtWidgets.QVBoxLayout()

        # Logo da barbearia
        logo_pixmap = QtGui.QPixmap("Red and Black Illustrative Barber Shop Logo.png")  # Substitua pelo caminho correto do logo
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Campo de entrada para o nome
        self.nome_input = QtWidgets.QLineEdit()
        self.nome_input.setPlaceholderText("Nome Completo")
        self.nome_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)
        layout.addWidget(self.nome_input)

        # Campo de entrada para o telefone
        self.telefone_input = QtWidgets.QLineEdit()
        self.telefone_input.setPlaceholderText("Telefone")
        self.telefone_input.setInputMask("(00) 00000-0000")
        self.telefone_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)
        layout.addWidget(self.telefone_input)

        # Campo de entrada para o endereço
        self.endereco_input = QtWidgets.QLineEdit()
        self.endereco_input.setPlaceholderText("Endereço")
        self.endereco_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)
        layout.addWidget(self.endereco_input)

        # Campo de entrada para o RG
        self.rg_input = QtWidgets.QLineEdit()
        self.rg_input.setPlaceholderText("RG")
        self.rg_input.setInputMask("00.000.000-0")
        self.rg_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)
        layout.addWidget(self.rg_input)

        # Botões
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.setStyleSheet("""
            QDialogButtonBox {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        buttons.accepted.connect(self.register_client)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Configuração do layout
        self.setLayout(layout)
        self.setStyleSheet("background-color: #000000; color: #ffffff;")  # Fundo preto

    def register_client(self):
        nome = self.nome_input.text()
        telefone = self.telefone_input.text()
        endereco = self.endereco_input.text()
        rg = self.rg_input.text()

        if nome and telefone and endereco and rg:
            try:
                conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Clientes (Nome, Telefone, Endereco, RG)
                    VALUES (?, ?, ?, ?)
                """, (nome, telefone, endereco, rg))
                conn.commit()
                QtWidgets.QMessageBox.information(self, "Cadastro", "Cliente cadastrado com sucesso!")
                self.accept()
            except pyodbc.Error as e:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao cadastrar cliente: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Campos Inválidos", "Por favor, preencha todos os campos.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = CadastroClienteDialog()
    dialog.exec_()
