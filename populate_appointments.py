import pyodbc
import random
from datetime import datetime, timedelta

# Conexão com o banco de dados
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
cursor = conn.cursor()

# Profissionais disponíveis
profissionais = ["João Silva", "Kleber Machado"]

# Valores Bruto e Líquido disponíveis
valores_bruto = ["50.00", "80.00", "40.00"]
valores_liquido = ["50.00", "48.75", "78.80", "39.00", "80.00"]

# Serviços disponíveis
servicos = ["Cabelo", "Barba", "Cabelo e Barba"]

# Formas de pagamento disponíveis
formas_pagamento = ["Pix", "Cartão de Crédito", "Cartão de Débito"]

# Clientes disponíveis
clientes = [
    "Vitor Nascimento", "Fernando Montenegro", "Thales Ramos", "João Miguel Guerra", "Dom Ramos", "Augusto Pinto",
    "Benjamin Marques", "Liam Fonseca", "Isaque Peixoto", "Kaique Gonçalves", "Gael Henrique Porto", "Vitor Brito",
    "Daniel Mendes", "Diego Sampaio", "Raul Macedo", "Brayan Camargo", "Vitor Hugo Peixoto", "Apollo Pimenta",
    "João Gabriel da Paz", "Igor Alves", "Guilherme da Conceição", "Vitor Hugo Souza", "Arthur Gabriel Sousa",
    "Lucas Vieira", "Nathan Alves", "João Guilherme Vasconcelos", "Carlos Eduardo Fonseca", "Isaque da Costa",
    "Vicente Sá", "Brayan Andrade", "Matheus Guerra", "Guilherme Campos", "Luigi Câmara", "João Gabriel Santos",
    "Thiago Cavalcanti", "Leonardo Cavalcanti", "Pedro Henrique Rocha", "Anthony Gabriel Câmara", "Nicolas Ferreira",
    "Enrico Pinto", "Gael Viana", "João Marques", "Davi das Neves", "Luiz Fernando Pires", "Enrico Marques",
    "Luiz Henrique Machado", "Raul Moura", "Igor Guerra", "Henry Gabriel Costela", "Bento Ribeiro", "Eduardo Vasconcelos",
    "Léo Gonçalves", "Noah Sousa", "Matteo da Mata", "Marcelo Jesus", "José Pedro Pinto", "Pedro Miguel Aragão",
    "Diego Gonçalves", "José Miguel Siqueira", "Yuri da Costa", "Carlos Eduardo Silva", "Luiz Felipe Freitas",
    "Vitor Macedo", "Marcos Vinicius Costela", "Murilo Melo", "Felipe Castro", "Dom Nunes", "Théo Rezende",
    "Matteo Aparecida", "Bryan Melo", "Marcos Vinicius Câmara", "Erick Cavalcanti", "Davi Miguel Vasconcelos",
    "Diogo Pimenta", "Cauê Campos", "Kaique Câmara", "João Pedro Porto", "Caio Cavalcante", "Luiz Henrique Leão",
    "José Miguel Guerra", "Davi da Rocha", "Arthur da Paz", "Yan Pereira", "Eduardo Moreira", "Pedro Henrique Pastor",
    "Thales Porto", "João Miguel Porto", "Liam Cardoso", "Daniel Freitas", "Calebe Teixeira", "Bento Moura",
    "Anthony Abreu", "Bento Jesus", "Apollo Vieira", "Henry Gabriel Teixeira", "Luiz Gustavo Cardoso", "Yuri Ramos",
    "José Pedro Mendonça", "Emanuel Fogaça", "Mateus da Paz"
]

# Script de inserção
insert_query = """
    INSERT INTO Pagamentos (Cliente, Profissional, Servico, FormaPagamento, ValorBruto, ValorLiquido, DataPagamento)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

# Função para gerar uma data aleatória entre 01/01/2022 e 31/07/2024
def random_date():
    start = datetime(2022, 1, 1)
    end = datetime(2024, 7, 31)
    return start + (end - start) * random.random()

# Inserir 5000 agendamentos
for _ in range(5000):
    cliente = random.choice(clientes)
    profissional = random.choice(profissionais)
    servico = random.choice(servicos)
    forma_pagamento = random.choice(formas_pagamento)
    valor_bruto = random.choice(valores_bruto)
    valor_liquido = random.choice(valores_liquido)
    data = random_date()

    cursor.execute(insert_query, (cliente, profissional, servico, forma_pagamento, valor_bruto, valor_liquido, data))

# Confirmar transação
conn.commit()

# Fechar conexão
conn.close()

print("5000 pagamentos inseridos com sucesso.")
