import pyodbc
from faker import Faker

# Conexão com o banco de dados
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S8Q93R3\\DESKTOPMARCOS;DATABASE=BarberShop;Trusted_Connection=yes;')
cursor = conn.cursor()

# Gerador de dados fictícios
fake = Faker('pt_BR')

# Script de inserção
insert_query = """
    INSERT INTO Clientes (Nome, Telefone, Endereco, RG)
    VALUES (?, ?, ?, ?)
"""

# Inserir 100 clientes masculinos
for _ in range(100):
    nome = fake.first_name_male() + ' ' + fake.last_name()
    telefone = fake.phone_number()
    endereco = fake.address()
    rg = fake.random_number(digits=9)

    cursor.execute(insert_query, (nome, telefone, endereco, rg))

# Confirmar transação
conn.commit()

# Fechar conexão
conn.close()

print("100 clientes masculinos inseridos com sucesso.")
