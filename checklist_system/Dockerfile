# Usa uma imagem base oficial do Python
FROM python:3.12-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação
COPY . .

# Expõe a porta que a aplicação vai rodar
EXPOSE 5000

# Comando para iniciar o servidor de produção Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]