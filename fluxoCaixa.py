import sys
import pandas as pd
from sqlalchemy import create_engine
from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc

# Conexão com o banco de dados usando SQLAlchemy
connection_string = 'mssql+pyodbc://DESKTOP-S8Q93R3\\DESKTOPMARCOS/BarberShop?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(connection_string)

# Função para extrair dados do banco de dados
def fetch_payments():
    query = """
    SELECT * FROM Pagamentos
    WHERE CAST(DataPagamento AS DATE) = CAST(GETDATE() AS DATE)
    """
    data = pd.read_sql(query, engine)
    return data

class CashFlowWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fluxo de Caixa - BarberShop')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: black;")

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout()

        # Logo
        self.logo = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap('Red and Black Illustrative Barber Shop Logo.png')  # Insira o caminho para o seu logo aqui
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.logo)

        # Área de controle do caixa
        self.cash_control_area = QtWidgets.QWidget(self)
        self.cash_control_area.setStyleSheet("background-color: #222; border-radius: 4px;")
        control_layout = QtWidgets.QHBoxLayout(self.cash_control_area)
        main_layout.addWidget(self.cash_control_area)

        # Botões de controle
        self.open_cash_button = QtWidgets.QPushButton("Abrir Caixa")
        self.open_cash_button.setStyleSheet("background-color: green; color: white; padding: 10px; border-radius: 8px;")
        self.open_cash_button.clicked.connect(self.open_cash)
        control_layout.addWidget(self.open_cash_button)

        self.close_cash_button = QtWidgets.QPushButton("Fechar Caixa")
        self.close_cash_button.setStyleSheet("background-color: red; color: white; padding: 10px; border-radius: 8px;")
        self.close_cash_button.clicked.connect(self.close_cash)
        control_layout.addWidget(self.close_cash_button)

        self.reset_cash_button = QtWidgets.QPushButton("Resetar Caixa")
        self.reset_cash_button.setStyleSheet("background-color: orange; color: white; padding: 10px; border-radius: 8px;")
        self.reset_cash_button.clicked.connect(self.reset_cash)
        control_layout.addWidget(self.reset_cash_button)

        self.refresh_button = QtWidgets.QPushButton("Atualizar")
        self.refresh_button.setStyleSheet("background-color: blue; color: white; padding: 10px; border-radius: 8px;")
        self.refresh_button.clicked.connect(self.load_payment_data)
        control_layout.addWidget(self.refresh_button)

        # Área de gráficos e tabelas
        self.graph_area = QtWidgets.QWidget(self)
        self.graph_area.setStyleSheet("background-color: #333; border-radius: 4px;")
        graph_layout = QtWidgets.QVBoxLayout(self.graph_area)
        main_layout.addWidget(self.graph_area)

        # Tabela de pagamentos
        self.payment_table = QtWidgets.QTableWidget()
        self.payment_table.setStyleSheet("background-color: white; color: black;")
        graph_layout.addWidget(self.payment_table)

        # Resumo do caixa
        self.cash_summary = QtWidgets.QLabel("Resumo do Caixa")
        self.cash_summary.setStyleSheet("color: white; font-size: 18px; padding: 10px;")
        graph_layout.addWidget(self.cash_summary)

        # Carregar dados
        self.load_payment_data()

        # Central widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_payment_data(self):
        data = fetch_payments()
        self.payment_table.setRowCount(len(data))
        self.payment_table.setColumnCount(len(data.columns))
        self.payment_table.setHorizontalHeaderLabels(data.columns)

        for i, row in data.iterrows():
            for j, value in enumerate(row):
                self.payment_table.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))
        
        self.update_cash_summary(data)

    def update_cash_summary(self, data):
        total_bruto = data['ValorBruto'].sum()
        total_liquido = data['ValorLiquido'].sum()
        self.cash_summary.setText(f"Total Bruto: R$ {total_bruto:.2f} | Total Líquido: R$ {total_liquido:.2f}")

    def open_cash(self):
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Caixa (Status, DataAbertura)
                VALUES ('Aberto', GETDATE())
            """)
            conn.commit()
            conn.close()
            self.show_message("Caixa", "Caixa aberto com sucesso!", "green")
        except pyodbc.Error as e:
            self.show_message("Erro", f"Erro ao abrir o caixa: {e}", "red")

    def close_cash(self):
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Caixa
                SET Status = 'Fechado', DataFechamento = GETDATE()
                WHERE Status = 'Aberto'
            """)
            conn.commit()
            conn.close()
            self.show_message("Caixa", "Caixa fechado com sucesso!", "green")
        except pyodbc.Error as e:
            self.show_message("Erro", f"Erro ao fechar o caixa: {e}", "red")

    def reset_cash(self):
        reply = QtWidgets.QMessageBox.question(self, 'Resetar Caixa', 'Você tem certeza que deseja resetar o caixa?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Caixa")
                conn.commit()
                conn.close()
                self.show_message("Caixa", "Caixa resetado com sucesso!", "green")
            except pyodbc.Error as e:
                self.show_message("Erro", f"Erro ao resetar o caixa: {e}", "red")

    def show_message(self, title, message, color):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(f"color: white; background-color: {color};")
        msg_box.exec_()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CashFlowWindow()
    window.show()
    sys.exit(app.exec_())
