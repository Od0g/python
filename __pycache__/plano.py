import pandas as pd

# Criar o arquivo Excel com múltiplas abas
file_path = "Gestao_Manutencao_Indicadores.xlsx"
with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
    # Aba 1: Controle de Ordens de Serviço
    controle_os = pd.DataFrame({
        "ID da OS": [],
        "Requisitante": [],
        "Setor": [],
        "Descrição do Problema": [],
        "Prioridade": [],
        "Material Necessário": [],
        "Técnico Responsável": [],
        "Status": [],
        "Data de Abertura": [],
        "Data de Conclusão": [],
    })
    controle_os.to_excel(writer, sheet_name="Controle_OS", index=False)
    
    # Aba 2: Resumo e Indicadores
    resumo_indicadores = pd.DataFrame({
        "Indicador": ["Total de Ordens", "Ordens Concluídas", "Ordens Pendentes",
                      "Tempo Médio para Conclusão (dias)", "Ordens por Prioridade (Alta/Média/Baixa)"],
        "Valor": [None, None, None, None, None],
    })
    resumo_indicadores.to_excel(writer, sheet_name="Resumo_Indicadores", index=False)

    # Aba 3: Dados para Gráficos
    dados_graficos = pd.DataFrame({
        "Prioridade": ["Alta", "Média", "Baixa"],
        "Quantidade": [None, None, None],
    })
    dados_graficos.to_excel(writer, sheet_name="Dados_Graficos", index=False)

    # Configurar o dashboard (Resumo_Indicadores)
    workbook = writer.book
    worksheet = writer.sheets["Resumo_Indicadores"]
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'categories': ['Dados_Graficos', 1, 0, 3, 0],
        'values':     ['Dados_Graficos', 1, 1, 3, 1],
        'name':       'Ordens por Prioridade',
    })
    chart.set_title({'name': 'Distribuição de Ordens por Prioridade'})
    worksheet.insert_chart('E5', chart)

print(f"Arquivo Excel criado com sucesso: {file_path}")
