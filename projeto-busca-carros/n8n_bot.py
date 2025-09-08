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
import re, os, csv

app = Flask(__name__)
CORS(app)

# ========= CONFIG CSV =========

CSV_PATH = os.environ.get('CSV_PATH', 'dados_corrigidos_sem_duplicatas.csv')

_catalogo_rows = []
_catalogo_loaded = False

def _carregar_catalogo():
    """Carregar o CSV uma vez na memória."""
    global _catalogo_rows, _catalogo_loaded
    if _catalogo_loaded:
        return
    sep = ';'

    try:
        with open(CSV_PATH, 'r', encoding='utf-8', newline='') as f:
            sample = f.read(2048)
            f.seek(0)
            # Tentar auto-detectar o separador
            sep = ';' if sample.count(';') >= sample.count(',') else ','
            reader = csv.DictReader(f, delimiter=sep)
            _catalogo_rows = [row for row in reader]
            _catalogo_loaded = True
    except FileNotFoundError:
        _catalogo_rows = []
        _catalogo_loaded = True

def _listar_versoes(marca: str, modelo: str, max_items: int=25):
    """Listar versões únicas do CSV para marca+modelo (case-insensitive)"""
    _carregar_catalogo()
    m = (marca or '').strip().lower()
    mod = (modelo or '').strip().lower()
    seen = set()
    versoes = []

    for row in _catalogo_rows:
        marca_row = (row.get('Marca') or row.get('marca') or '').strip().lower()
        modelo_row = (row.get('Modelo') or row.get('modelo') or '').strip().lower()
        versao_row = (row.get('Versão') or row.get('versão') or '').strip()

        if m == marca_row and mod == modelo_row and versao_row:
            key = versao_row.lower()
            if key not in seen:
                seen.add(key)
                versoes.append(versao_row)
                if len(versoes) >= max_items:
                    break
    return versoes

# ========= Webmotors =========
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

# ========= ENDPOINTS =========
@app.route('/api/validar_marca', methods=['GET'])
def validar_marca():
    """Valida se uma marca existe no CSV (case-insensitive)"""
    marca=request.args.get('marca','').strip()
    if not marca:
        return jsonify({'valid': False, 'error': 'Marca não informada!'})
    
    _carregar_catalogo()
    m_upper = marca.upper()     # Converter para uppercase

    # Buscar se a marca existe
    marca_existe = any(
        ((row.get('Marca') or '').strip().upper() == m_upper)
        for row in _catalogo_rows
    )

    return jsonify({'valid': marca_existe, 'marca': m_upper})

@app.route('/api/validar_modelo', methods=['GET'])
def validar_modelo():
    """Valida se um modelo existe no CSV (case-insensitive)"""
    modelo=request.args.get('modelo','').strip()
    marca=request.args.get('marca','').strip()
    if not modelo:
        return jsonify({'valid': False, 'error': 'modelo não informado!'})
    
    _carregar_catalogo()
    modelo_upper = modelo.upper()     # Converter para uppercase
    marca_upper = marca.upper()     # Converter para uppercase

    # Buscar se a marca existe
    modelo_encontrado = False
    for row in _catalogo_rows:
        modelo_row = (row.get('Modelo') or '').strip()
        if modelo_upper == modelo_row.upper():
            modelo_encontrado = True
            break

    return jsonify({
        'valid': modelo_encontrado,
        'modelo_input': modelo,
        'modelo_upper': modelo_upper,
        'marca_upper': marca_upper,
        'encontrado': modelo_encontrado
    })

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

@app.route('/api/versoes', methods=['GET'])
def versoes():
    """marca+modelo -> lista de versões únicas do CSV"""
    marca = request.args.get('marca', '')
    modelo = request.args.get('modelo', '')
    versoes = _listar_versoes(marca, modelo)
    return jsonify({
        'marca': marca,
        'modelo': modelo,
        'versoes': versoes,
    })

@app.route('/api/comparar', methods=['GET'])
def comparar():
    """
    marca1, modelo1, versao1, marca2, modelo2, versao2 -> comparação
    Preço médio usa o mesmo critério do /api/info_carro (marca+modelo)
    """
    p = request.args

    c1 = {
        'marca': p.get('marca1', '').lower(),
        'modelo': p.get('modelo1', '').lower(),
        'versao': p.get('versao1', '') or None,
    }

    c2 = {
        'marca': p.get('marca2', '').lower(),
        'modelo': p.get('modelo2', '').lower(),
        'versao': p.get('versao2', '') or None,
    }

    media1, precos1 = buscar_precos_webmotors(c1['marca'], c1['modelo'])
    media2, precos2 = buscar_precos_webmotors(c2['marca'], c2['modelo'])

    amostras1 = len(precos1) if isinstance(precos1, list) else 0
    amostras2 = len(precos2) if isinstance(precos2, list) else 0

    diff = media1 - media2
    if media1 == media2:
        mais_barato = 'empate'
    else:
        mais_barato = 'carro1' if media1 < media2 else 'carro2'

    return jsonify({
        'carro1': {**c1, 'preco_medio': media1, 'amostras': amostras1},
        'carro2': {**c2, 'preco_medio': media2, 'amostras': amostras2},
        'diferenca': diff,
        'mais_barato': mais_barato
    })

if __name__ == '__main__':
    # Inicia o servidor Flask em modo debug
    app.run(host='0.0.0.0', port=5000, debug=True)