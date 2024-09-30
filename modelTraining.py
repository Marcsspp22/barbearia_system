import pandas as pd
from sqlalchemy import create_engine
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import time
from scipy.stats import randint

# Conexão com o banco de dados usando SQLAlchemy
connection_string = 'mssql+pyodbc://DESKTOP-S8Q93R3\\DESKTOPMARCOS/BarberShop?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(connection_string)

# Executar a consulta para extrair os dados de agendamentos
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

# Feature Engineering
data['Mes'] = data['Data'].dt.month
data['Ano'] = data['Data'].dt.year
data['Dia'] = data['Data'].dt.day

# Seleção de características e alvo
X = data[['Cliente', 'DiaSemana', 'Hora', 'Servico', 'Mes', 'Ano', 'Dia', 'NumAgendamentos', 'NumCancelamentos']]
y = data['Status']

# Codificação das variáveis categóricas
X = pd.get_dummies(X, columns=['Cliente', 'Servico'], drop_first=True)

# Balanceamento das classes usando SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

# Divisão dos dados em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)

# Parâmetros para RandomizedSearchCV
param_dist = {
    'n_estimators': randint(100, 500),
    'max_features': ['sqrt', 'log2'],
    'max_depth': [10, 30, 50, None],
    'min_samples_split': randint(2, 11),
    'min_samples_leaf': randint(1, 5),
    'bootstrap': [True, False]
}

start_time = time.time()
rf = RandomForestClassifier(random_state=42)
random_search = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=50, cv=3, n_jobs=-1, verbose=2, random_state=42)
random_search.fit(X_train, y_train)
end_time = time.time()

print(f"Tempo total de execução: {end_time - start_time} segundos")

# Treinamento do modelo com os melhores hiperparâmetros
best_rf = random_search.best_estimator_
best_rf.fit(X_train, y_train)

# Avaliação do modelo no conjunto de teste
y_pred = best_rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Acurácia do modelo: {accuracy * 100:.2f}%')

# Salvando o modelo treinado
with open('cancelation_model.pkl', 'wb') as f:
    pickle.dump(best_rf, f)
