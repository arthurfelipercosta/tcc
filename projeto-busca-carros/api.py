# api.py
# Backend Flask para fornecer informações de preço médio de veículos (Webmotors) e quantidade de reclamações (ReclameAqui) para integração com front-end HTML/JS.
#
# Endpoints:
# - /api/info_carro: Recebe marca e modelo, retorna preço médio e reclamações.
#
# Funções auxiliares:
# - buscar_precos_webmotors: Faz scrapping de preços no Webmotors.
# - buscar_reclamacoes_reclameaqui: Faz scrapping de reclamações no ReclameAqui.
#
# Uso acadêmico/experimental.
"""
api.py
Backend Flask para fornecer informações de preço médio de veículos (Webmotors) e quantidade de reclamações (ReclameAqui) para integração com front-end HTML/JS.

Endpoints:
- /api/info_carro: Recebe marca e modelo, retorna preço médio e reclamações.

Funções auxiliares:
- buscar_precos_webmotors: Faz scrapping de preços no Webmotors.
- buscar_reclamacoes_reclameaqui: Faz scrapping de reclamações no ReclameAqui.

Uso acadêmico/experimental.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

def buscar_precos_webmotors(marca, modelo, limite=10):
    """
    Busca preços de veículos no Webmotors por marca e modelo.
    Args:
        marca (str): Marca do veículo (ex: 'honda')
        modelo (str): Modelo do veículo (ex: 'civic')
        limite (int): Número máximo de preços a coletar (default=10)
    Returns:
        tuple: (media dos preços encontrados ou None, lista de preços)
    """
    url = (
        "https://www.webmotors.com.br/api/search/car"
        "?displayPerPage=10"
        "&actualPage=1"
        "&showMenu=true"
        "&showCount=true"
        "&showBreadCrumb=true"
        "&order=1"
        f"&url=https://www.webmotors.com.br/carros/estoque/{marca.lower()}/{modelo.lower()}?marca={marca.lower()}&modelo={modelo.lower()}&autocomplete={modelo.lower()}&autocompleteTerm={marca.title()}%20{modelo.upper()}&tipoveiculo=carros&marca1={marca.upper()}&modelo1={modelo.upper()}&page=1"
        "&mediaZeroKm=true"
    )
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return 0, "Carro não encontrado"
    data = r.json()
    precos = []
    for anuncio in data.get("SearchResults", [])[:limite]:
        price = anuncio.get("Prices", {}).get("Price")
        if price:
            precos.append(float(price))
    if precos:
        media = sum(precos) / len(precos)
        return media, precos
    return 0, "Carro não encontrado"

# def buscar_reclamacoes_reclameaqui(marca,modelo):
#     """
#     Busca a quantidade de reclamações de uma empresa no ReclameAqui.
#     Args:
#         marca (str): Marca do veículo (ex: 'audi')
#         modelo (str): Modelo do veículo (ex: 'a3 sedan')
#     Returns:
#         str: Quantidade de reclamações encontradas ou 'Não encontrado'
#     """
#     url = f"https://www.reclameaqui.com.br/busca/?q={marca}%20{modelo}"
#     return url
    # headers = {'User-Agent': 'Mozilla/5.0'}
    # r = requests.get(url, headers=headers)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # # Procura por span com a classe que contém o número de reclamações (ajuste se necessário)
    # reclamacoes = soup.find('span', {'class': 'sc-1pe7b5t-1'})
    # if reclamacoes:
    #     return reclamacoes.text.strip()
    # return "Não encontrado"

@app.route('/api/info_carro', methods=['GET'])
def info_carro():
    """
    Endpoint principal da API.
    Recebe marca e modelo via query string e retorna:
    - preço médio do veículo (Webmotors)
    - lista de preços encontrados
    - quantidade de reclamações (ReclameAqui)
    Exemplo de uso:
    GET /api/info_carro?marca=honda&modelo=civic
    """
    marca = request.args.get('marca', '').lower()
    modelo = request.args.get('modelo', '').lower()
    preco_medio, precos = buscar_precos_webmotors(marca, modelo)
    # reclamacoes = buscar_reclamacoes_reclameaqui(marca, modelo)

    return jsonify({
        'preco_medio': preco_medio,
        'precos': precos,
        # 'reclamacoes': reclamacoes
    })

if __name__ == '__main__':
    # Inicia o servidor Flask em modo debug
    app.run(debug=True)