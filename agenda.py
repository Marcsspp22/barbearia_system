import pandas as pd
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import pickle
import time
from scipy.stats import randint
from decimal import Decimal
from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import sys

# Carregar o modelo treinado
with open('cancelation_model.pkl', 'rb') as f:
    cancelation_model = pickle.load(f)

# Conexão com o banco de dados usando SQLAlchemy
connection_string = 'mssql+pyodbc://DESKTOP-S8Q93R3\\DESKTOPMARCOS/BarberShop?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(connection_string)

# Executar a consulta para extrair os dados
query = """
SELECT A.Cliente, A.Data, A.Hora, A.Servico, A.Status,
       (SELECT COUNT(*) FROM Agendamentos AS A1 WHERE A1.Cliente = A.Cliente AND A1.Data < A.Data) AS NumAgendamentos,
       (SELECT COUNT(*) FROM Agendamentos AS A2 WHERE A2.Cliente = A.Cliente AND A2.Data < A.Data AND A2.Status = 'Cancelado') AS NumCancelamentos
FROM Agendamentos AS A
"""
data = pd.read_sql(query, engine)

# Pré-processamento dos dados
data['Data'] = pd.to_datetime(data['Data'])
data['DiaSemana'] = data['Data'].dt.dayofweek
data['Hora'] = data['Hora'].astype(str).str.slice(0, 2).astype(int)
data['Status'] = data['Status'].map({'Agendado': 0, 'Cancelado': 1})

# Remover linhas com valores NaN em 'Status'
data = data.dropna(subset=['Status'])

# Feature Engineering
data['Mes'] = data['Data'].dt.month
data['Ano'] = data['Data'].dt.year
data['Dia'] = data['Data'].dt.day

# Seleção de características e alvo
X = data[['Cliente', 'DiaSemana', 'Hora', 'Servico', 'Mes', 'Ano', 'Dia', 'NumAgendamentos', 'NumCancelamentos']]
y = data['Status']

# Remover linhas com valores NaN em X ou y
X = X.dropna()
y = y[X.index]

# Codificação das variáveis categóricas
X = pd.get_dummies(X, columns=['Cliente', 'Servico'], drop_first=True)

# Balanceamento das classes usando SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

# Divisão dos dados em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)

# Função para prever a chance de cancelamento
def predict_cancelation(client, day_of_week, hour, service, month, year, day, X_columns):
    # Prepare the input data in the same way as during training
    input_data = pd.DataFrame({
        'Cliente': [client],
        'DiaSemana': [day_of_week],
        'Hora': [hour],
        'Servico': [service],
        'Mes': [month],
        'Ano': [year],
        'Dia': [day],
        'NumAgendamentos': [data[(data['Cliente'] == client) & (data['Data'] < f"{year}-{month}-{day}")].shape[0]],
        'NumCancelamentos': [data[(data['Cliente'] == client) & (data['Data'] < f"{year}-{month}-{day}") & (data['Status'] == 1)].shape[0]]
    })
    input_data = pd.get_dummies(input_data, columns=['Cliente', 'Servico'], drop_first=True)

    # Align the input_data columns with the training data columns
    input_data = input_data.reindex(columns=X_columns, fill_value=0)

    # Predict the probability of cancellation
    prob_cancelation = cancelation_model.predict_proba(input_data)[:, 1][0]
    return prob_cancelation


class ClientRegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Novo Cliente")
        self.setFixedSize(300, 250)

        layout = QtWidgets.QFormLayout()

        # Campos para cadastrar cliente
        self.name_input = QtWidgets.QLineEdit()
        self.phone_input = QtWidgets.QLineEdit()
        self.address_input = QtWidgets.QLineEdit()
        self.rg_input = QtWidgets.QLineEdit()

        layout.addRow("Nome Completo:", self.name_input)
        layout.addRow("Telefone:", self.phone_input)
        layout.addRow("Endereço:", self.address_input)
        layout.addRow("RG:", self.rg_input)

        # Botões
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.setStyleSheet("""
            QDialogButtonBox {
                border: none;
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

        self.setLayout(layout)

    def register_client(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        rg = self.rg_input.text()

        if name and phone and address and rg:
            try:
                conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Clientes (Nome, Telefone, Endereco, RG)
                    VALUES (?, ?, ?, ?)
                """, (name, phone, address, rg))
                conn.commit()
                conn.close()
                QtWidgets.QMessageBox.information(self, "Cadastro", "Cliente cadastrado com sucesso!")
                self.accept()
            except pyodbc.Error as e:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao cadastrar cliente: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Campos Inválidos", "Por favor, preencha todos os campos.")

class PaymentDialog(QtWidgets.QDialog):
    def __init__(self, appointment_details, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processar Pagamento")
        self.setFixedSize(300, 250)
        self.appointment_details = appointment_details

        layout = QtWidgets.QFormLayout()

        self.service_label = QtWidgets.QLabel(f"Serviço: {appointment_details['service']}")
        self.client_label = QtWidgets.QLabel(f"Cliente: {appointment_details['client']}")
        self.price_label = QtWidgets.QLabel(f"Preço: {appointment_details['price']}")

        self.payment_method = QtWidgets.QComboBox()
        self.payment_method.addItems(["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])

        layout.addRow(self.service_label)
        layout.addRow(self.client_label)
        layout.addRow(self.price_label)
        layout.addRow("Forma de Pagamento:", self.payment_method)

        self.confirm_button = QtWidgets.QPushButton("Confirmar")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #218838;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.confirm_button.clicked.connect(self.process_payment)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def process_payment(self):
        price = self.appointment_details['price']
        method = self.payment_method.currentText()

        if method == "Pix" or method == "Dinheiro":
            net_amount = price
        elif method == "Cartão de Crédito":
            net_amount = price * Decimal('0.975')
        elif method == "Cartão de Débito":
            net_amount = price * Decimal('0.985')

        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Pagamentos (Cliente, Profissional, Servico, FormaPagamento, ValorBruto, ValorLiquido)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.appointment_details['client'],
                self.appointment_details['professional'],
                self.appointment_details['service'],
                method,
                price,
                net_amount
            ))

            # Atualizar o status do agendamento para "Finalizado"
            cursor.execute("""
                UPDATE Agendamentos
                SET Status = 'Finalizado'
                WHERE Id = ?
            """, (self.appointment_details['id'],))

            conn.commit()
            conn.close()
            QtWidgets.QMessageBox.information(self, "Pagamento", "Pagamento processado com sucesso!")
            self.accept()
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao processar pagamento: {e}")


class AppointmentInfoDialog(QtWidgets.QDialog):
    def __init__(self, date_time, appointment_details, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalhes do Agendamento")
        self.setFixedSize(300, 200)
        self.appointment_details = appointment_details
        self.parent_window = parent

        layout = QtWidgets.QVBoxLayout()

        self.date_time_label = QtWidgets.QLabel(f"Data e Hora: {date_time}")
        self.date_time_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.client_label = QtWidgets.QLabel(f"Cliente: {appointment_details['client']}")
        self.service_label = QtWidgets.QLabel(f"Serviço: {appointment_details['service']}")

        layout.addWidget(self.date_time_label)
        layout.addWidget(self.client_label)
        layout.addWidget(self.service_label)

        self.cancel_button = QtWidgets.QPushButton("Desmarcar Cliente")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #c82333;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_appointment)
        layout.addWidget(self.cancel_button)

        self.payment_button = QtWidgets.QPushButton("Fechar Ticket")
        self.payment_button.setStyleSheet("""
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
        self.payment_button.clicked.connect(self.open_payment_dialog)
        layout.addWidget(self.payment_button)

        self.setLayout(layout)

    def cancel_appointment(self):
        reason, ok = QtWidgets.QInputDialog.getText(self, "Motivo do Cancelamento", "Informe o motivo do cancelamento:")
        if not ok or not reason:
            QtWidgets.QMessageBox.warning(self, "Motivo Não Informado", "O motivo do cancelamento deve ser preenchido.")
            return

        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()

            # Atualizar o status do agendamento
            cursor.execute("""
                UPDATE Agendamentos
                SET Status = 'Cancelado', MotivoCancelamento = ?
                WHERE Id = ?
            """, (reason, self.appointment_details['id']))

            conn.commit()
            QtWidgets.QMessageBox.information(self, "Cancelamento", "Agendamento desmarcado com sucesso!")
            
            # Atualizar a agenda principal
            self.parent_window.get_appointments_from_db(self.parent_window.professional_selector.currentText(), self.date_time_label.text().split()[2])
            self.parent_window.show_schedule()
            self.accept()

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao desmarcar agendamento: {e}")
        finally:
            if conn:
                conn.close()

    def open_payment_dialog(self):
        # Pegar o preço do serviço no banco de dados
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
        cursor = conn.cursor()
        cursor.execute("SELECT Preco FROM Servicos WHERE Nome = ?", (self.appointment_details['service'],))
        price = cursor.fetchone()[0]
        conn.close()

        self.appointment_details['price'] = Decimal(price)
        self.appointment_details['professional'] = self.parent_window.professional_selector.currentText()  # Adicionando profissional
        dialog = PaymentDialog(self.appointment_details, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.accept()


class ScheduleDialog(QtWidgets.QDialog):
    def __init__(self, date_time, appointment_details, appointment_id, professional, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agendar Serviço")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.appointment_id = appointment_id
        self.parent_window = parent
        self.professional = professional

        layout = QtWidgets.QVBoxLayout()

        self.date_time_label = QtWidgets.QLabel(f"Data e Hora: {date_time}")
        self.date_time_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.client_search_input = QtWidgets.QLineEdit()
        self.client_search_input.setPlaceholderText("Pesquisar Cliente (opcional)")
        self.client_search_input.setStyleSheet("""
             QLineEdit {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.client_search_input.textChanged.connect(self.update_client_list)

        self.client_list = QtWidgets.QComboBox()
        self.client_list.setStyleSheet("""
            QComboBox {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
        """)
        self.client_list.currentIndexChanged.connect(self.client_selected)

        self.service_list = QtWidgets.QComboBox()
        self.service_list.setPlaceholderText("Serviço")
        self.service_list.setStyleSheet("""
            QComboBox {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
        """)
        self.load_services()

        layout.addWidget(self.date_time_label)
        layout.addWidget(self.client_search_input)
        layout.addWidget(self.client_list)
        layout.addWidget(self.service_list)

        self.register_client_button = QtWidgets.QPushButton("Cadastrar Novo Cliente")
        self.register_client_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
            QPushButton:pressed {
                background-color: #218838;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.register_client_button.clicked.connect(self.register_new_client)
        layout.addWidget(self.register_client_button)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.setStyleSheet("""
            QDialogButtonBox {
                border: none;
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
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        self.update_client_list()

    def load_services(self):
        conn = None
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            query = "SELECT Nome FROM Servicos"
            cursor.execute(query)
            
            self.service_list.clear()  # Limpa os itens existentes na combobox
            
            # Adiciona os serviços da base de dados
            services = cursor.fetchall()
            for row in services:
                self.service_list.addItem(row.Nome)

            # Define o índice do primeiro serviço se houver serviços disponíveis
            if services:
                self.service_list.setCurrentIndex(1)  # Define o índice do primeiro serviço

        except pyodbc.Error as e:
            print(f"Erro ao buscar serviços: {e}")
        finally:
            if conn:
                conn.close()

    def update_client_list(self):
        search_text = self.client_search_input.text()
        self.client_list.clear()
        self.client_list.addItem("Selecione um Cliente")

        conn = None
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            query = """
                SELECT Nome FROM Clientes
                WHERE Nome LIKE ?
            """
            cursor.execute(query, ('%' + search_text + '%',))
            for row in cursor.fetchall():
                self.client_list.addItem(row.Nome)
        except pyodbc.Error as e:
            print(f"Erro ao buscar clientes: {e}")
        finally:
            if conn:
                conn.close()

    def client_selected(self):
        pass

    def register_new_client(self):
        reg_dialog = ClientRegistrationDialog(self)
        if reg_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.update_client_list()
            self.client_list.setCurrentIndex(0)

class AgendaWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agenda de Serviços")
        self.setFixedSize(800, 600)

        self.layout = QtWidgets.QVBoxLayout()   

        self.professional_selector = QtWidgets.QComboBox()
        self.professional_selector.setStyleSheet("""
            QComboBox {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
        """)
        self.load_professionals()  
        self.layout.addWidget(self.professional_selector)

        

        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 10px;
                padding: 10px;
                font-family: Arial, sans-serif;
            }
            QCalendarWidget QAbstractItemView {
                selection-background-color: #007bff;
                selection-color: white;
                border-radius: 8px;
            }
            QCalendarWidget QWidget {
                font-size: 14px;
            }
        """)
        self.layout.addWidget(self.calendar)

        self.schedule_layout = QtWidgets.QGridLayout()
        self.schedule_container = QtWidgets.QWidget()
        self.schedule_container.setLayout(self.schedule_layout)
        self.layout.addWidget(self.schedule_container)

        self.setLayout(self.layout)

        self.selected_date = None
        self.current_dialog = None
        self.appointments = {}
        self.schedule_visible = True

        self.calendar.clicked.connect(self.date_selected)
        self.professional_selector.currentIndexChanged.connect(self.professional_selected)
        
       
        
    def get_appointment_id_from_db(self, professional, date_time):
        conn = None
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            query = """
                SELECT Id FROM Agendamentos
                WHERE Profissional = ? AND Data = ? AND Hora = ? 
            """
            cursor.execute(query, (professional, date_time.split(' ')[0], date_time.split(' ')[1]))
            row = cursor.fetchone()
            return row.Id if row else None
        except pyodbc.Error as e:
            print(f"Erro ao buscar ID do agendamento: {e}")
        finally:
            if conn:
                conn.close()
        return None


    def load_professionals(self):
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            cursor.execute("SELECT Nome FROM Profissionais")
            for row in cursor.fetchall():
                self.professional_selector.addItem(row.Nome)
            conn.close()
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao buscar profissionais: {e}")

    def date_selected(self, date):
        if self.selected_date == date:
            self.toggle_schedule_visibility()
        else:
            self.selected_date = date
            self.show_schedule()

    def toggle_schedule_visibility(self):
        if self.schedule_visible:
            self.clear_schedule()
        else:
            self.show_schedule()
        self.schedule_visible = not self.schedule_visible

    def show_schedule(self):
        if not self.selected_date:
            return

        self.clear_schedule()
        date_str = self.selected_date.toString("yyyy-MM-dd")
        professional = self.professional_selector.currentText()

        self.get_appointments_from_db(professional, date_str)

        times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        for i, time in enumerate(times):
            date_time = f'{date_str} {time}'
            appointment_details = self.appointments.get(date_time, None)
            
            if appointment_details:
                client = appointment_details['client']
                service = appointment_details['service']
                day_of_week = self.selected_date.dayOfWeek() - 1  # Convert to 0-6 format
                hour = int(time.split(':')[0])
                month = self.selected_date.month()
                year = self.selected_date.year()
                day = self.selected_date.day()

                # Prever a chance de cancelamento
                prob_cancelation = predict_cancelation(client, day_of_week, hour, service, month, year, day, X.columns)

                # Definir a cor do botão baseado na previsão
                if prob_cancelation < 0.44:
                    color = 'green'
                elif prob_cancelation < 0.55:
                    color = 'yellow'
                else:
                    color = 'red'

                button_text = f"{time} - {client}"
                button = QtWidgets.QPushButton(button_text)
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border: 1px solid #007bff;
                        border-radius: 8px;
                        padding: 10px;
                        color: #333;
                    }}
                    QPushButton:pressed {{
                        background-color: #f0f0f0;
                    }}
                    QPushButton:hover {{
                        background-color: #e9ecef;
                    }}
                """)
            else:
                button_text = f"{time} - Livre"
                button = QtWidgets.QPushButton(button_text)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 1px solid #007bff;
                        border-radius: 8px;
                        padding: 10px;
                        color: #333;
                    }
                    QPushButton:pressed {
                        background-color: #f0f0f0;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                    }
                """)
            
            button.clicked.connect(lambda _, t=date_time: self.time_selected(t))
            self.schedule_layout.addWidget(button, i // 3, i % 3)

        self.update_calendar_highlights()

    def update_calendar_highlights(self):
        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QColor('lightyellow'))
        for date_time in self.appointments.keys():
            date = QtCore.QDate.fromString(date_time.split(' ')[0], "yyyy-MM-dd")
            self.calendar.setDateTextFormat(date, format)

        marker_format = QtGui.QTextCharFormat()
        marker_format.setForeground(QtGui.QColor('red'))
        marker_format.setFontWeight(QtGui.QFont.Bold)
        for date_time in self.appointments.keys():
            date = QtCore.QDate.fromString(date_time.split(' ')[0], "yyyy-MM-dd")
            self.calendar.setDateTextFormat(date, marker_format)

    def professional_selected(self):
        self.clear_schedule()
        self.show_schedule()

    def month_selected(self):
        month = self.month_selector.currentIndex() + 1
        self.calendar.setCurrentPage(self.calendar.yearShown(), month)

    def time_selected(self, date_time):
        professional = self.professional_selector.currentText()
        appointment_details = self.appointments.get(date_time, None)
        appointment_id = self.get_appointment_id_from_db(professional, date_time)
        if appointment_details:
            dialog = AppointmentInfoDialog(date_time, appointment_details, self)
        else:
            dialog = ScheduleDialog(date_time, appointment_details, appointment_id, professional, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if isinstance(dialog, ScheduleDialog):
                new_client = dialog.client_list.currentText()
                new_service = dialog.service_list.currentText()
                if new_client:
                    appointment = {
                        'client': new_client,
                        'service': new_service
                    }
                    self.appointments[date_time] = appointment
                else:
                    self.appointments.pop(date_time, None)
                self.save_appointment_to_db(professional, date_time.split(' ')[0], date_time.split(' ')[1], self.appointments.get(date_time, {}))
        self.show_schedule()

    def clear_schedule(self):
        for i in reversed(range(self.schedule_layout.count())):
            widget = self.schedule_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def get_appointments_from_db(self, professional, date_str):
        conn = None
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            query = """
                SELECT Id, Hora, Cliente, Servico, Data
                FROM Agendamentos
                WHERE Profissional = ? AND Data = ? AND Status = 'Agendado'
            """
            cursor.execute(query, (professional, date_str))
            self.appointments.clear()
            for row in cursor.fetchall():
                time = row.Hora.strftime("%H:%M")
                self.appointments[f'{date_str} {time}'] = {
                    'id': row.Id,
                    'client': row.Cliente,
                    'service': row.Servico
                }
        except pyodbc.Error as e:
            print(f"Erro ao buscar agendamentos: {e}")
        finally:
            if conn:
                conn.close()

    def save_appointment_to_db(self, professional, date, time, appointment):
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            
            if appointment:
                client = appointment.get('client')
                service = appointment.get('service')
                
                # Check if there's already an appointment for the same professional, date, and time
                cursor.execute("""
                    SELECT Id FROM Agendamentos
                    WHERE Profissional = ? AND Data = ? AND Hora = ?
                """, (professional, date, time))
                existing_appointment = cursor.fetchone()
                
                if existing_appointment:
                    # Update the existing appointment
                    cursor.execute("""
                        UPDATE Agendamentos
                        SET Cliente = ?, Servico = ?, Status = 'Agendado'
                        WHERE Id = ?
                    """, (client, service, existing_appointment.Id))
                else:
                    # Insert a new appointment
                    cursor.execute("""
                        INSERT INTO Agendamentos (Profissional, Data, Hora, Cliente, Servico, Status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (professional, date, time, client, service, 'Agendado'))
            else:
                cursor.execute("""
                    DELETE FROM Agendamentos
                    WHERE Profissional = ? AND Data = ? AND Hora = ?
                """, (professional, date, time))
            
            conn.commit()
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao salvar agendamento: {e}")
        finally:
            if conn:
                conn.close()

    def delete_appointment_from_db(self, professional, date_str, time_str):
        appointment_id = self.get_appointment_id_from_db(professional, date_str, time_str)
        if not appointment_id:
            print("Agendamento não encontrado.")
            return

        conn = None
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
            cursor = conn.cursor()
            query = """
                DELETE FROM Agendamentos
                WHERE Id = ?
            """
            cursor.execute(query, (appointment_id,))
            conn.commit()
            print("Agendamento excluído com sucesso!")
        except pyodbc.Error as e:
            print(f"Erro ao excluir agendamento: {e}")
        finally:
            if conn:
                conn.close()

    def register_new_client(self):
        reg_dialog = ClientRegistrationDialog(self)
        if reg_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.update_client_list()
            self.client_list.setCurrentIndex(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AgendaWindow()
    window.show()
    sys.exit(app.exec_())
