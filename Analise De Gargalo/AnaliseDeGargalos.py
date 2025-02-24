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

meses = sorted(df_auto["Data"].dt.month.dropna().unique())
mes_selecionado = st.sidebar.multiselect("Selecione o mês", meses, default=meses)

maquinas = sorted(df_auto["Nome Máquina"].dropna().unique())
maquina_selecionada = st.sidebar.multiselect("Selecione a máquina", maquinas, default=maquinas)

# Aplicar filtros
df_auto = df_auto[df_auto["Data"].dt.year.isin(ano_selecionado)]
df_auto = df_auto[df_auto["Data"].dt.month.isin(mes_selecionado)]
df_auto = df_auto[df_auto["Nome Máquina"].isin(maquina_selecionada)]

# Análise por tipo de OS
tipo_col = "Tipo"
if tipo_col in df_auto.columns:
    st.subheader("Distribuição de OS Automáticas por Tipo")
    tipo_counts = df_auto[tipo_col].value_counts()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=tipo_counts.index, y=tipo_counts.values, palette="viridis", ax=ax)
    plt.xticks(rotation=45)
    plt.title("Quantidade de OS por Tipo")
    st.pyplot(fig)

# Análise por máquina
maquina_col = "Nome Máquina"
if maquina_col in df_auto.columns:
    st.subheader("Top 10 Máquinas com Mais OS Automáticas")
    top_maquinas = df_auto[maquina_col].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(y=top_maquinas.index, x=top_maquinas.values, palette="magma", ax=ax)
    plt.title("Máquinas com mais OS Automáticas")
    st.pyplot(fig)

# Criar colunas de período
df_auto["Ano"] = df_auto[date_col].dt.year
df_auto["Mês"] = df_auto[date_col].dt.month
df_auto["Semana"] = df_auto[date_col].dt.isocalendar().week
df_auto["Dia"] = df_auto[date_col].dt.day

# Gráficos por período
st.subheader("OS Automáticas por Ano")
fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x="Ano", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

st.subheader("OS Automáticas por Mês")
fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x="Mês", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

st.subheader("OS Automáticas por Semana")
fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x="Semana", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

st.subheader("OS Automáticas por Dia")
fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x="Dia", data=df_auto, palette="coolwarm", ax=ax)
st.pyplot(fig)

# Exibir tabela filtrada
st.subheader("Dados Filtrados")
st.dataframe(df_auto)

# Salvar relatório e permitir download
csv = df_auto.to_csv(index=False, encoding="ISO-8859-1", sep=";")
st.download_button(label="Baixar Relatório CSV", data=csv, file_name="Relatorio_Gargalos.csv", mime="text/csv")
