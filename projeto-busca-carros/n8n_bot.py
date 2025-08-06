# Passo a passo para rodar o projeto
# Abrir o terminal
# Rodar o comando "pip install -r requirements.txt" para instalar dependências
# Rodar o comando "n8n" (caso não o tenha instalado, rodar o comando de "npm install -g n8n" antes)
# Abrir outro terminal, navegar até a pasta do projeto
# Rodar o comando "python n8n_bot.py"
# Abrir outro terminal e rodar o comando "ngrok http 5678"
# Copiar o endereço no "Forwarding" e colar no campo "When a message comes in" na página da Twilio, em "sandbox settings"
# Entrar em https://console.twilio.com
# Copiar o ACCOUNT_SID e o AUTH_TOKEN caso tenham sido alterados
# Pegar o "Path" nos parâmetros do N8N
# Em outro terminal rodar "ngrok http 5678"

# Importação das bibliotecas necessárias
import pandas as pd  # Para manipulação de dados CSV
import os, time     # os para operações de sistema, time para delays
import requests     # Para fazer requisições HTTP
from twilio.rest import Client  # Cliente da API do Twilio
from flask import Flask, request  # Framework web Flask

# Inicialização da aplicação Flask
app = Flask(__name__)

# Variáveis de ambiente
NGROK_URL = os.getenv("NGROK_URL")                      # URL do ngrok para o N8N
WEBHOOK = os.getenv("WEBHOOK")                          # URL local do N8N
TWILIO_SID = os.getenv("TWILIO_SID")                    # Account SID do Twilio
AUTH_TOKEN = os.getenv("AUTH_TOKEN")                    # Token de autenticação do Twilio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # Diretório base do projeto

N8N_WEBHOOK_URL = f"{NGROK_URL}/webhook/{WEBHOOK}"

# Dicionário para armazenar o estado de cada usuário (número -> informações)
usuario = {}

# Função para enviar e receber dados de resposta do n8n
def chat_com_n8n(payload):
    """
    Envia dados para o webhook do N8N e retorna a resposta
    
    Parâmetros:
    - payload: dados a serem enviados para o N8N
    
    Retorna:
    - JSON da resposta se sucesso, None se erro
    """
    response = requests.post(N8N_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erro ao conversar com o N8N: ", response.text)
        return None
    
# Função que envia uma mensagem através da API do Twilio
def enviar_mensagem(destino, texto):
    """
    Enviar uma mensagem para o número de destino pela API do Twilio

    Parâmetros:
    - destino: string, número do WhatsApp no formato +5584XXXXXXXX
    - texto: string, mensagem a ser enviada
    """
    # Criação do cliente Twilio com as credenciais
    client = Client(TWILIO_SID, AUTH_TOKEN)

    # Envio da mensagem via WhatsApp
    message = client.messages.create(
        from_='whatsapp:+14155238886',  # Número da sandbox do Twilio
        body=texto,                     # Texto da mensagem
        to=f'whatsapp:{destino}'        # Número do destinatário
    )
    print(f"Mensagem enviada! SID {message.sid}")

# Função para verificar se a marca existe no banco CSV
def marcas_existentes(marca_usuario):
    """
    Verificar se a marca existe no banco CSV
    Retornar TRUE se existir, FALSE caso contrário
    """
    try:

        # Caminho para o arquivo CSV com os dados dos carros
        csv_path = os.path.join(BASE_DIR,"dados_corrigidos_sem_duplicatas.csv")

        # Leitura do CSV e extração das marcas únicas
        df = pd.read_csv(csv_path, sep=";")
        marcas = df['Marca'].str.upper().unique()

        # Verificação se a marca do usuário existe (comparação case-insensitive)
        return marca_usuario.upper() in marcas
    except Exception as e:
        print(f"Erro ao verificar marca: {e}")
        return False

def modelos_existentes(marca_usuario, modelo_usuario):
    """
    Verificar se o modelo de carro daquela marca existe no banco CSV
    Retornar TRUE se existir, FALSE caso contrário
    """
    try:
        # Caminho para o arquivo CSV com os dados dos carros
        csv_path = os.path.join(BASE_DIR, "dados_corrigidos_sem_duplicatas.csv")

        # Leitura do CSV e extração dos modelos únicos para a marca do usuário
        df = pd.read_csv(csv_path, sep=";")
        modelos = df['Modelo'].str.upper().unique()

        # Verificação se o modelo do usuário existe para a marca específica
        return modelo_usuario.upper() in modelos
    except Exception as e:
        print(f"Erro ao verificar modelo: {e}")
        return False

# Endpoints para receber mensagens do WhatsApp via N8N
@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint principal que recebe mensagens do WhatsApp via N8N
    Gerencia o fluxo de conversa com o usuário
    """
    try:
        # Verificar o tipo de requisição (form ou JSON) e extrair dados
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Extração da mensagem e número do usuário
        mensagem = data.get("mensagem")
        numero = data.get("numero")
        etapa = data.get({"etapa": "hello"})

        # Validação dos dados recebidos
        if not numero or not mensagem:
            return {"erro": "Requisição mal formatada"}, 400
        
        # Limpeza do número (remove prefixo whatsapp:)
        numero = numero.replace("whatsapp:", "")
        print(f"Mensagem recebida de {numero}: {mensagem}")

        payload = {
            "mensagem" : mensagem,
            "numero": numero,
            "etapa": etapa
        }

        # Fazer a requisição interna para validar_marca
        response = requests.post("http://127.0.0.1:5002/validar_marca")
        # Recuperar o estado do usuário ou iniciar um novo
        estado = usuario.get(numero, {"etapa": "hello"})

        # Atualização do estado do usuário no dicionário
        usuario[numero] = estado
        return payload, 200
        
    except Exception as e:
        # Tratamento de erros
        print("Erro no webhook: ", e)
        return {"erro": str(e)}, 500

@app.route("/validar_marca", methods=["POST"])
def validar_marca():
    """
    Endpoint para validar se a marca existe no banco CSV
    """

    try:
        data = request.get_json()
        marca = data.get("mensagem")
        numero = data.get("numero")
        etapa = data.get("etapa")

        print(f"DATA: {data}")

        if not numero:
            return {"erro": "Número não informado!"}, 400
        elif not marca:
            return {"erro": "Marca não informada!"}, 400
        elif marcas_existentes(marca):
            if (etapa == "hello"):
                enviar_mensagem(numero, "Qual seria a marca do primeiro carro que deseja comparar?")
            elif (etapa == "modelo1"):
                enviar_mensagem(numero, "Digite novamente a marca do primeiro carro!")

            return {
                "validade": True,
                "etapa": "modelo1",
                "mensagem": "Marca encontrada! Agora digite o modelo de carro 1."
            }, 200
        else:
            return {
                "validade": False,
                "etapa": "modelo1",
                "mensagem": "Marca não encontrada!"
            }, 200
    except Exception as e:
        print("Erro na validação da marca: ",e)
        return { "erro": str(e)}, 500

@app.route("/validar_modelo", methods=["POST"])
def validar_modelo():
    """
    Endpoint para validar se o modelo existe no banco CSV
    """
    try:
        data = request.get_json()
        marca = data.get("marca")
        modelo = data.get("mensagem")
        numero = data.get("numero")
        etapa = data.get("etapa")

        if not numero:
            return {"erro": "Número não informado!"}, 400
        elif not modelo:
            return {"erro": "Modelo não informado"}, 400
        elif modelos_existentes(marca, modelo):
            return {"validade": True}, 200
        else:
            return {"validade": False}, 200
    except Exception as e:
        print("Erro na validação do modelo: ",e)
        return { "erro": str(e)}, 500

# Execução da aplicação Flask
if __name__ == "__main__":
    app.run(port=5002, debug=True)  # Inicia o servidor na porta 5002 com debug ativado