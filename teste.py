import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from pyspark.sql import SparkSession

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barbearia Insights")

        # Layout principal
        layout = QVBoxLayout()
        self.label = QLabel("Insights de Agendamento")
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_insights(self, insights_text):
        self.label.setText(insights_text)

def process_data():
    spark = SparkSession.builder.appName("BarbeariaAnalytics").getOrCreate()

    # Exemplo de dados de agendamento
    data = [
        ("2024-08-01", "10:00", "Corte de Cabelo"),
        ("2024-08-01", "11:00", "Barba"),
        ("2024-08-02", "10:00", "Corte de Cabelo"),
    ]

    columns = ["data", "horario", "servico"]
    agendamentos_df = spark.createDataFrame(data, columns)

    # Analisar os horários mais populares
    insights_df = agendamentos_df.groupBy("horario").count().orderBy("count", ascending=False)
    insights = insights_df.collect()

    spark.stop()
    return insights

def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    # Processar dados com PySpark
    insights = process_data()
    insights_text = "\n".join([f"Horário: {row['horario']}, Contagem: {row['count']}" for row in insights])

    # Atualizar a interface com os insights
    window.update_insights(insights_text)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
