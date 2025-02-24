from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    # Passo 1: Ler os dados
    df = pd.read_excel('gargalos.xlsx')

    # Passo 2: Processar os dados
    os_por_ano = df['Ano de Fabricação'].value_counts().sort_index()
    os_por_maquina = df['Nome Máquina'].value_counts()
    maquina_mais_os = os_por_maquina.idxmax()
    quantidade_mais_os = os_por_maquina.max()

    # Passo 3: Gerar gráficos (salvar em static/)
    plt.figure(figsize=(10, 6))
    os_por_ano.plot(kind='bar')
    plt.title('Número de O.S. por Ano de Fabricação')
    plt.xlabel('Ano de Fabricação')
    plt.ylabel('Número de O.S.')
    plt.savefig('static/os_por_ano.png')
    plt.close()  # Fechar a figura para liberar memória

    plt.figure(figsize=(10, 6))
    os_por_maquina.plot(kind='bar')
    plt.title('Número de O.S. por Máquina')
    plt.xlabel('Máquina')
    plt.ylabel('Número de O.S.')
    plt.savefig('static/os_por_maquina.png')
    plt.close()

    # Passo 4: Passar dados para o template
    return render_template('index.html',
                           os_por_ano=os_por_ano.to_dict(),
                           os_por_maquina=os_por_maquina.to_dict(),
                           maquina_mais_os=maquina_mais_os,
                           quantidade_mais_os=quantidade_mais_os)

if __name__ == '__main__':
    app.run(debug=True)