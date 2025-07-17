"""
api.py
Backend Flask para fornecer informações de preço médio de veículos (Webmotors) e quantidade de reclamações (ReclameAqui) para integração com front-end HTML/JS.

Endpoints:
- /api/info_carro: Recebe marca e modelo, retorna preço médio e reclamações.

Funções auxiliares:
- buscar_precos_webmotors: Faz scraping de preços no Webmotors.
- buscar_reclamacoes_reclameaqui: Faz scraping de reclamações no ReclameAqui.

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
    url = f"https://www.webmotors.com.br/carros/estoque/{marca}/{modelo}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    precos = []
    # Procura por elementos <strong> que contenham o preço (ajuste o seletor se necessário)
    for preco in soup.select('p._body-bold-large_qtpsh_78'):
        valor = preco.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
        print(valor)
        try:
            precos.append(float(valor))
        except:
            pass
        if len(precos) >= limite:
            break
    if precos:
        media = sum(precos) / len(precos)
        return media, precos
    return None, []

def buscar_reclamacoes_reclameaqui(empresa_slug):
    """
    Busca a quantidade de reclamações de uma empresa no ReclameAqui.
    Args:
        empresa_slug (str): Slug da empresa na URL do ReclameAqui (ex: 'honda-do-brasil')
    Returns:
        str: Quantidade de reclamações encontradas ou 'Não encontrado'
    """
    url = f"https://www.reclameaqui.com.br/empresa/{empresa_slug}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Procura por span com a classe que contém o número de reclamações (ajuste se necessário)
    reclamacoes = soup.find('span', {'class': 'sc-1pe7b5t-1'})
    if reclamacoes:
        return reclamacoes.text.strip()
    return "Não encontrado"

@app.route('/api/info_carro', methods=['GET'])
def info_carro():
    """
    Endpoint principal da API.
    Recebe marca, modelo e empresa_slug via query string e retorna:
    - preço médio do veículo (Webmotors)
    - lista de preços encontrados
    - quantidade de reclamações (ReclameAqui)
    Exemplo de uso:
    GET /api/info_carro?marca=honda&modelo=civic&empresa_slug=honda-do-brasil
    """
    marca = request.args.get('marca', '').lower()
    modelo = request.args.get('modelo', '').lower()
    empresa_slug = request.args.get('empresa_slug', '').lower()
    preco_medio, precos = buscar_precos_webmotors(marca, modelo)
    reclamacoes = buscar_reclamacoes_reclameaqui(empresa_slug)
    return jsonify({
        'preco_medio': preco_medio,
        'precos': precos,
        'reclamacoes': reclamacoes
    })

if __name__ == '__main__':
    # Inicia o servidor Flask em modo debug
    app.run(debug=True)