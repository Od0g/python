import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Configurar layout do Streamlit
st.set_page_config(layout="wide")

# Carregar os dados
df = pd.read_csv("Gargalos.csv", encoding="ISO-8859-1", sep=";")

# Ajustar nomes de colunas removendo espaços extras
df.columns = df.columns.str.strip()

# Converter coluna de data
date_col = "Data"
if date_col in df.columns:
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')

# Filtrar OS geradas automaticamente
desc_col = "Descrição"
df_auto = df[df[desc_col].str.contains("OS GERADA AUTOMATICAMENTE", na=False, case=False)]

# Criar filtros no Streamlit
st.sidebar.header("Filtros")
anos = sorted(df_auto["Data"].dt.year.dropna().unique())
ano_selecionado = st.sidebar.multiselect("Selecione o ano", anos, default=anos)

df_auto = df_auto[df_auto["Data"].dt.year.isin(ano_selecionado)]

# Análise por tipo de OS
tipo_col = "Tipo"
if tipo_col in df_auto.columns:
    st.subheader("Distribuição de OS Automáticas por Tipo")
    tipo_counts = df_auto[tipo_col].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=tipo_counts.index, y=tipo_counts.values, palette="viridis", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Análise por máquina
maquina_col = "Nome Máquina"
if maquina_col in df_auto.columns:
    st.subheader("Top 10 Máquinas com Mais OS Automáticas")
    top_maquinas = df_auto[maquina_col].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(y=top_maquinas.index, x=top_maquinas.values, palette="magma", ax=ax)
    st.pyplot(fig)

# Criar colunas de período
df_auto["Ano"] = df_auto[date_col].dt.year
df_auto["Mês"] = df_auto[date_col].dt.month
df_auto["Semana"] = df_auto[date_col].dt.isocalendar().week
df_auto["Dia"] = df_auto[date_col].dt.day

# Gráficos por período
st.subheader("OS Automáticas por Ano")
fig, ax = plt.subplots()
sns.countplot(x="Ano", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

st.subheader("OS Automáticas por Mês")
fig, ax = plt.subplots()
sns.countplot(x="Mês", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

st.subheader("OS Automáticas por Semana")
fig, ax = plt.subplots()
sns.countplot(x="Semana", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

st.subheader("OS Automáticas por Dia")
fig, ax = plt.subplots()
sns.countplot(x="Dia", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

# Exibir tabela filtrada
st.subheader("Dados Filtrados")
st.dataframe(df_auto)

# Salvar relatório
df_auto.to_csv("Relatorio_Gargalos.csv", index=False, encoding="ISO-8859-1", sep=";")
st.success("Relatório salvo como Relatorio_Gargalos.csv")
