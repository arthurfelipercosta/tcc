# Importação das bibliotecas necessárias
import pandas as pd  # Para manipulação de dados CSV
import os, time     # os para operações de sistema, time para delays
import requests     # Para fazer requisições HTTP
from twilio.rest import Client  # Cliente da API do Twilio
from flask import Flask, request, jsonify  # Framework web Flask

# Inicialização da aplicação Flask
app = Flask(__name__)

# Variáveis de ambiente
NGROK_URL = os.getenv("NGROK_URL")                      # URL do ngrok para o N8N
WEBHOOK = os.getenv("WEBHOOK")                          # URL local do N8N
ACCOUNT_SID = os.getenv("ACCOUNT_SID")                   # Account SID do Twilio
AUTH_TOKEN = os.getenv("AUTH_TOKEN")                    # Token de autenticação do Twilio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # Diretório base do projeto

N8N_WEBHOOK_URL = f"{NGROK_URL}/webhook-test/{WEBHOOK}"

usuario_etapas = {}

@app.route('/atualizar_estado', methods=['POST'])
def atualizar_estado():
    try:
        data = request.get_json()
        numero = data.get('numero')
        etapa = data.get('etapa')

        if numero:
            print(f"Numero enviado: {numero}")
            return jsonify({'status': 'ok'}), 200
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        return False


if __name__ == '__main__':
    app.run(port=5002, debug=True)