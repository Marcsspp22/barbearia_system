from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import sys


class ServiceRegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Novo Serviço")
        self.setFixedSize(600, 600)

        # Layout principal
        layout = QtWidgets.QVBoxLayout()

        # Logo da barbearia
        logo_pixmap = QtGui.QPixmap("Red and Black Illustrative Barber Shop Logo.png")  # Substitua pelo caminho correto do logo
        logo_label = QtWidgets.QLabel()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Campo de entrada para o nome do serviço
        self.service_name_input = QtWidgets.QLineEdit()
        self.service_name_input.setPlaceholderText("Nome do Serviço")
        self.service_name_input.setStyleSheet("""
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
        layout.addWidget(self.service_name_input)

        # Campo de entrada para o preço
        self.price_input = QtWidgets.QLineEdit()
        self.price_input.setPlaceholderText("Preço")
        self.price_input.setStyleSheet("""
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
        layout.addWidget(self.price_input)

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
        buttons.accepted.connect(self.register_service)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Configuração do layout
        self.setLayout(layout)
        self.setStyleSheet("background-color: #000000; color: #ffffff;")  # Fundo preto

    def register_service(self):
        service_name = self.service_name_input.text()
        price = self.price_input.text()

        if service_name and price:
            try:
                conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Servicos (Nome, Preco)
                    VALUES (?, ?)
                """, (service_name, price))
                conn.commit()
                QtWidgets.QMessageBox.information(self, "Cadastro", "Serviço cadastrado com sucesso!")
                self.accept()
            except pyodbc.Error as e:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao cadastrar serviço: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Campos Inválidos", "Por favor, preencha todos os campos.")
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = ServiceRegistrationDialog()
    dialog.exec_()
