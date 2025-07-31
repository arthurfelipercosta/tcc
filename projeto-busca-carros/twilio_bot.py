# twilio.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Credenciais do Twilio
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_WHATSAPP = 'whatsapp:+14155238886' # número do sandbox

# Dicionário para guardar o estado da conversa por número
user_states = {}
user_answers={}

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    print(f"Mensagem recebida de {from_number}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    state = user_states.get(from_number)

    # Se for a primeira mensagem, pergunta a marca do carro 1
    if state is None:
        msg.body("Bem-vindoQual a marca do carro 1?")
        user_states[from_number] = 'asked_car_brand'
    elif state == 'asked_car_brand':
        user_answers[from_number] = {'marca': incoming_msg}
        print(f"Marca recebida: {incoming_msg}")
        msg.body("Qual o modelo do carro 1?")
        user_states[from_number] = 'asked_car_model'
    elif state == 'asked_car_model':
        user_answers[from_number]['modelo'] = incoming_msg
        print(f"Modelo recebido: {incoming_msg}")
        msg.body(f"Marca: {user_answers[from_number]['marca']}, Modelo: {incoming_msg}")
        # Aqui você pode resetar ou continuar o fluxo
        user_states[from_number] = None

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)