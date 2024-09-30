import sys
import pandas as pd
from sqlalchemy import create_engine
from PyQt5 import QtWidgets, QtGui, QtCore
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Conexão com o banco de dados usando SQLAlchemy
connection_string = 'mssql+pyodbc://DESKTOP-S8Q93R3\\DESKTOPMARCOS/BarberShop?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(connection_string)

# Função para extrair dados do banco de dados
def fetch_data():
    query = """
    SELECT * FROM Agendamentos
    """
    data = pd.read_sql(query, engine)
    return data

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='black')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('black')
        super(MplCanvas, self).__init__(self.fig)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()

class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dashboard - BarberShop')
        self.setGeometry(100, 100, 1200, 1200)
        self.setStyleSheet("background-color: black;")

        # Layout principal
        main_layout = QtWidgets.QVBoxLayout()

        # Logo
        self.logo = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap('Red and Black Illustrative Barber Shop Logo.png')  # Insira o caminho para o seu logo aqui
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.logo)

        # Área de gráficos
        self.graph_area = QtWidgets.QWidget(self)
        self.graph_area.setStyleSheet("background-color: #222; border-radius: 4px;")
        graph_layout = QtWidgets.QGridLayout(self.graph_area)
        main_layout.addWidget(self.graph_area)

        # Carregar dados
        self.data = fetch_data()

        # Gráfico 1: Taxa de cancelamento por profissional
        self.cancel_rate_chart = MplCanvas(self, width=4, height=3, dpi=100)
        self.plot_cancel_rate()
        graph_layout.addWidget(self.cancel_rate_chart, 0, 0)

        # Gráfico 2: Dias da semana com maiores movimentos
        self.weekday_chart = MplCanvas(self, width=3, height=3, dpi=100)
        self.plot_weekday_movements()
        graph_layout.addWidget(self.weekday_chart, 0, 1)

        # Gráfico 3: Número total de atendimentos por ano
        self.total_appointments_chart = MplCanvas(self, width=3, height=3, dpi=100)
        self.plot_total_appointments_by_year()
        graph_layout.addWidget(self.total_appointments_chart, 1, 0)

        # Gráfico 4: Serviço mais realizado
        self.service_chart = MplCanvas(self, width=3, height=3, dpi=100)
        self.plot_service_distribution()
        graph_layout.addWidget(self.service_chart, 1, 1)

        # Central widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def plot_cancel_rate(self):
        self.cancel_rate_chart.axes.clear()
        cancel_rate = self.data[self.data['Status'] == 'Cancelado'].groupby('Profissional').size() / self.data.groupby('Profissional').size()
        cancel_rate = cancel_rate.sort_values()
        sns.barplot(x=cancel_rate.values, y=cancel_rate.index, hue=cancel_rate.index, dodge=False, palette='Reds', ax=self.cancel_rate_chart.axes, legend=False)
        self.cancel_rate_chart.axes.set_title('Taxa de Cancelamento por Profissional', color='white')
        self.cancel_rate_chart.axes.set_xlabel('Taxa de Cancelamento', color='white')
        self.cancel_rate_chart.axes.set_ylabel('Profissional', color='white')
        self.cancel_rate_chart.axes.tick_params(colors='white')
        self.cancel_rate_chart.fig.tight_layout()
        self.cancel_rate_chart.draw()

    def plot_weekday_movements(self):
        self.weekday_chart.axes.clear()
        self.data['DiaSemana'] = pd.to_datetime(self.data['Data']).dt.dayofweek
        weekday_movements = self.data.groupby('DiaSemana').size().sort_index()
        sns.barplot(x=weekday_movements.index, y=weekday_movements.values, hue=weekday_movements.index, dodge=False, palette='Blues', ax=self.weekday_chart.axes, legend=False)
        self.weekday_chart.axes.set_title('Movimentos por Dia da Semana', color='white')
        self.weekday_chart.axes.set_xlabel('Dia da Semana', color='white')
        self.weekday_chart.axes.set_ylabel('Número de Movimentos', color='white')
        self.weekday_chart.axes.set_xticks(range(7))
        self.weekday_chart.axes.set_xticklabels(['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'], color='white')
        self.weekday_chart.axes.tick_params(colors='white')
        self.weekday_chart.fig.tight_layout()
        self.weekday_chart.draw()

    def plot_total_appointments_by_year(self):
        self.total_appointments_chart.axes.clear()
        self.data['Ano'] = pd.to_datetime(self.data['Data']).dt.year
        total_appointments_by_year = self.data.groupby('Ano').size()
        sns.barplot(x=total_appointments_by_year.index, y=total_appointments_by_year.values, palette='Greens', ax=self.total_appointments_chart.axes)
        self.total_appointments_chart.axes.set_title('Número Total de Atendimentos por Ano', color='white')
        self.total_appointments_chart.axes.set_xlabel('Ano', color='white')
        self.total_appointments_chart.axes.set_ylabel('Número de Atendimentos', color='white')
        self.total_appointments_chart.axes.tick_params(colors='white')
        self.total_appointments_chart.fig.tight_layout()
        self.total_appointments_chart.draw()

    def plot_service_distribution(self):
        self.service_chart.axes.clear()
        service_distribution = self.data.groupby('Servico').size()
        wedges, texts, autotexts = self.service_chart.axes.pie(service_distribution, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Paired'))
        for text in texts + autotexts:
            text.set_color('white')
        self.service_chart.axes.set_title('Distribuição de Serviços', color='white')
        self.service_chart.axes.legend(service_distribution.index, loc='upper right', bbox_to_anchor=(1.3, 1))
        self.service_chart.fig.tight_layout()
        self.service_chart.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())
