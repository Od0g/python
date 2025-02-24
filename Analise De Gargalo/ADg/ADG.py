import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ler a planilha
df = pd.read_excel('gargalos.xlsx')

# Contar O.S. por ano
os_por_ano = df['Ano de Fabricação'].value_counts().sort_index()

# Contar O.S. por máquina
os_por_maquina = df['Nome Máquina'].value_counts()

# Máquina com mais O.S.
maquina_mais_os = os_por_maquina.idxmax()
quantidade_mais_os = os_por_maquina.max()

# Gerar gráficos
plt.figure(figsize=(10, 6))
os_por_ano.plot(kind='bar')
plt.title('Número de O.S. por Ano de Fabricação')
plt.xlabel('Ano de Fabricação')
plt.ylabel('Número de O.S.')
plt.savefig('static/os_por_ano.png')  # Salvar o gráfico para usar no HTML

plt.figure(figsize=(10, 6))
os_por_maquina.plot(kind='bar')
plt.title('Número de O.S. por Máquina')
plt.xlabel('Máquina')
plt.ylabel('Número de O.S.')
plt.savefig('static/os_por_maquina.png')  # Salvar o gráfico para usar no HTML