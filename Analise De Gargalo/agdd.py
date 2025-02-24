# Importar bibliotecas
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Carregar os dados
df = pd.read_excel('/workspaces/python/gargalos.xlsx', engine='openpyxl')

# Verificar primeiras linhas
df.head()

# Converter coluna de Data para formato datetime
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')

# Calcular idade da OS em dias
hoje = datetime.now()
df['Idade_OS_Dias'] = (hoje - df['Data']).dt.days

# Filtrar OS com mais de 365 dias
os_antigas = df[df['Idade_OS_Dias'] > 365]
print(f"Total de OS com mais de 1 ano: {len(os_antigas)}")

# Contagem por máquina
maquinas_problematicas = os_antigas['Máquina'].value_counts().reset_index()
maquinas_problematicas.columns = ['Máquina', 'Total de OS Antigas']

# Gráfico de barras
plt.figure(figsize=(12, 6))
plt.bar(maquinas_problematicas['Máquina'], maquinas_problematicas['Total de OS Antigas'], color='#ff9999')
plt.title('Top Máquinas com OS Antigas (Mais de 1 Ano)')
plt.xticks(rotation=45)
plt.ylabel('Quantidade de OS')
plt.show()

# Gráfico 1: Proporção de OS Antigas vs Recentes
plt.figure(figsize=(8, 6))
df['Status_OS'] = ['Antiga (>1 ano)' if dias > 365 else 'Recente' for dias in df['Idade_OS_Dias']]
df['Status_OS'].value_counts().plot.pie(autopct='%1.1f%%', colors=['#ff9999','#66b3ff'])
plt.title('Proporção de OS Antigas vs Recentes')
plt.show()

# Gráfico 2: Distribuição de OS por Máquina (Top 10)
plt.figure(figsize=(12, 6))
df['Máquina'].value_counts().head(10).plot(kind='bar', color='#88c999')
plt.title('Top 10 Máquinas com Mais OS (Todas)')
plt.xlabel('Máquina')
plt.ylabel('Total de OS')
plt.xticks(rotation=45)
plt.show()

# Tabela resumo
resumo = df.groupby('Máquina').agg(
    Total_OS=('O.S.', 'count'),
    OS_Antigas=('Idade_OS_Dias', lambda x: (x > 365).sum())
).reset_index()

# Ordenar por OS antigas
resumo = resumo.sort_values('OS_Antigas', ascending=False)
print("\nResumo por Máquina:")
display(resumo.head(10)) # type: ignore

# Gráfico 3: OS Antigas por Fabricante
plt.figure(figsize=(10, 6))
os_antigas['Fabricante'].value_counts().head(5).plot(kind='barh', color='#d4a5c7')
plt.title('Top 5 Fabricantes com Mais OS Antigas')
plt.xlabel('Total de OS')
plt.show()

# Gráfico 4: Idade das Máquinas vs OS Antigas (se houver dados de ano de fabricação)
if 'Ano de Fabricação' in df.columns:
    plt.figure(figsize=(10, 6))
    plt.scatter(df['Ano de Fabricação'], df['Idade_OS_Dias'], alpha=0.5, color='#ff6961')
    plt.title('Relação entre Ano de Fabricação e Idade da OS')
    plt.xlabel('Ano de Fabricação')
    plt.ylabel('Idade da OS (Dias)')
    plt.show()