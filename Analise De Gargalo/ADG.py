import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar os dados
df = pd.read_csv("Gargalos.csv", encoding="ISO-8859-1", sep=";")

# Verificar colunas disponíveis
print("Colunas do DataFrame:", df.columns)

# Ajustar nomes de colunas removendo espaços extras
df.columns = df.columns.str.strip()

# Verificar se a coluna 'Data' existe antes de converter
date_col = "Data"
if date_col in df.columns:
    try:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
    except Exception as e:
        print("Erro ao converter a coluna de data:", e)

# Filtrar apenas OS geradas automaticamente, verificando se a coluna existe
desc_col = "Descrição"
if desc_col in df.columns:
    df_auto = df[df[desc_col].str.contains("OS GERADA AUTOMATICAMENTE", na=False, case=False)]
else:
    df_auto = pd.DataFrame()
    print("Coluna de descrição não encontrada!")

# Verificar se há dados filtrados antes de continuar
if not df_auto.empty:
    # Contagem de OS automáticas por tipo
    tipo_col = "Tipo"
    if tipo_col in df_auto.columns:
        tipo_counts = df_auto[tipo_col].value_counts()
        
        # Visualizar distribuição por tipo de OS
        plt.figure(figsize=(8, 5))
        sns.barplot(x=tipo_counts.index, y=tipo_counts.values, palette="viridis")
        plt.xlabel("Tipo de Ordem de Serviço")
        plt.ylabel("Quantidade")
        plt.title("Distribuição de OS Automáticas por Tipo")
        plt.xticks(rotation=45)
        plt.show()
    else:
        print("Coluna 'Tipo' não encontrada!")

    # Análise por máquina
    maquina_col = "Nome Máquina"
    if maquina_col in df_auto.columns:
        top_maquinas = df_auto[maquina_col].value_counts().head(10)
        plt.figure(figsize=(10, 5))
        sns.barplot(x=top_maquinas.values, y=top_maquinas.index, palette="magma")
        plt.xlabel("Quantidade de OS")
        plt.ylabel("Máquina")
        plt.title("Top 10 Máquinas com Mais OS Automáticas")
        plt.show()
    else:
        print("Coluna 'Nome Máquina' não encontrada!")
    
    # Salvar relatório básico
    df_auto.to_csv("Relatorio_Gargalos.csv", index=False, encoding="ISO-8859-1", sep=";")
    print("Relatório salvo: Relatorio_Gargalos.csv")
else:
    print("Nenhuma OS gerada automaticamente encontrada!")
