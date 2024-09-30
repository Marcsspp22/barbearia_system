from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import sys

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
        self.client_search_input.setPlaceholderText("Pesquisar Cliente")
        self.client_search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.client_search_input.textChanged.connect(self.update_client_list)

        self.client_list = QtWidgets.QComboBox()
        self.client_list.setStyleSheet("""
            QComboBox {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
        """)
        self.client_list.addItem("Selecione um Cliente")
        self.client_list.addItem("Cadastrar Novo Cliente")
        self.client_list.currentIndexChanged.connect(self.client_selected)

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

        if appointment_details:
            self.client_list.setCurrentText(appointment_details.get('client', ''))
            self.service_list.setCurrentText(appointment_details.get('service', ''))
            self.client_list.setEnabled(False)

        layout.addWidget(self.date_time_label)
        layout.addWidget(self.client_search_input)
        layout.addWidget(self.client_list)
        layout.addWidget(self.register_client_button)
        layout.addWidget(self.service_list)

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
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if appointment_details:
            self.cancel_client_button = QtWidgets.QPushButton("Desmarcar Cliente")
            self.cancel_client_button.setStyleSheet("""
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
            self.cancel_client_button.clicked.connect(self.cancel_client)
            layout.addWidget(self.cancel_client_button)

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
        self.client_list.addItem("Cadastrar Novo Cliente")

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
        if self.client_list.currentText() == "Cadastrar Novo Cliente":
            self.register_new_client()
        else:
            # Corrigido: Atualizar o campo de texto com o cliente selecionado
            pass

    def register_new_client(self):
        reg_dialog = ClientRegistrationDialog(self)
        if reg_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.update_client_list()
            self.client_list.setCurrentIndex(0)
            
    def cancel_client(self):
        if not self.appointment_id:
            QtWidgets.QMessageBox.warning(self, "Erro", "Nenhum agendamento selecionado.")
            return

        client_name = self.client_list.currentText()
        if not client_name:
            QtWidgets.QMessageBox.warning(self, "Cliente Não Selecionado", "Por favor, selecione um cliente para desmarcar.")
            return

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
            """, (reason, self.appointment_id))

            # Puxar as informações do agendamento para o cancelamento
            cursor.execute("""
                SELECT Data, Hora, Profissional, Cliente, Servico
                FROM Agendamentos
                WHERE Id = ?
            """, (self.appointment_id,))
            appointment = cursor.fetchone()

            if appointment:
                # Inserir na tabela Cancelamentos
                cursor.execute("""
                    INSERT INTO Cancelamentos (Id, Data, Hora, Profissional, Cliente, Servico, Motivo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.appointment_id, appointment.Data, appointment.Hora, appointment.Profissional, appointment.Cliente, appointment.Servico, reason))

            conn.commit()
            QtWidgets.QMessageBox.information(self, "Cancelamento", "Agendamento desmarcado com sucesso!")
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao desmarcar agendamento: {e}")
        finally:
            if conn:
                conn.close()




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
        self.load_professionals()  # Carregar profissionais
        self.layout.addWidget(self.professional_selector)

        self.month_selector = QtWidgets.QComboBox()
        self.month_selector.addItems([
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ])
        self.month_selector.currentIndexChanged.connect(self.month_selected)
        self.month_selector.setStyleSheet("""
            QComboBox {
                border: 1px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
        """)
        self.layout.addWidget(self.month_selector)

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
        self.month_selector.currentIndexChanged.connect(self.month_selected)
        
        
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
            button_text = f"{time} - {appointment_details['client'] if appointment_details else 'Livre'}"
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
        dialog = ScheduleDialog(date_time, appointment_details, appointment_id, professional)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AgendaWindow()
    window.show()
    sys.exit(app.exec_())