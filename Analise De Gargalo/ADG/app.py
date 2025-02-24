from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

# Carregar os dados
df = pd.read_csv("Gargalos.csv", encoding="ISO-8859-1", sep=";")
df.columns = df.columns.str.strip()
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors='coerce')

@app.route('/')
def index():
    anos = sorted(df["Data"].dt.year.dropna().unique())
    return render_template('index.html', anos=anos)

@app.route('/grafico', methods=['POST'])
def grafico():
    ano_selecionado = int(request.form['ano'])
    df_filtrado = df[df["Data"].dt.year == ano_selecionado]

    # Criar gráfico
    fig, ax = plt.subplots()
    sns.countplot(x="Tipo", data=df_filtrado, palette="viridis", ax=ax)
    plt.xticks(rotation=45)
    
    # Converter gráfico para imagem
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return render_template('grafico.html', graph_url=graph_url)

if __name__ == '__main__':
    app.run(debug=True)
