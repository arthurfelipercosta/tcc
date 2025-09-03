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
import unicodedata

app = Flask(__name__)
CORS(app)

def slugify(valor: str) -> str:
    """
    Converte texto para slug: sem acentos, minúsculo e com hífens.
    Ex.: 'A3 Sedan' -> 'a3-sedan', 'HR/V' -> 'hr-v'
    """
    if not valor:
        return ""
    # Remove acentos
    valor_norm = unicodedata.normalize('NFKD', valor)
    valor_sem_acentos = ''.join(ch for ch in valor_norm if not unicodedata.combining(ch))
    # Minúsculas
    valor_sem_acentos = valor_sem_acentos.lower()
    # Substitui separadores comuns por '-'
    valor_sem_acentos = re.sub(r"[\s/_.]+", "-", valor_sem_acentos)
    # Remove caracteres que não são letras, números ou '-'
    valor_sem_acentos = re.sub(r"[^a-z0-9-]", "", valor_sem_acentos)
    # Remove hifens duplicados
    valor_sem_acentos = re.sub(r"-+", "-", valor_sem_acentos).strip('-')
    return valor_sem_acentos

def buscar_precos_fipe(marca, modelo):
    """
    Busca preço na FIPE usando a API pública (parallelum.com.br).
    Retorna preço do ano mais recente disponível.
    """
    try:
        session = requests.Session()
        base = "https://parallelum.com.br/fipe/api/v1/carros"

        # Mapeamento de nomes para melhor compatibilidade com FIPE
        modelo_map = {
            'f-150': 'f150',
            'f150': 'f-150',
            'a3 sportback': 'a3',
            'a4 sedan': 'a4',
            'a5 sportback': 'a5',
            'corolla cross': 'corolla',
            'corolla hb': 'corolla',
            'hilux diesel 4x4': 'hilux',
            'sw4 diesel 4x4': 'sw4',
            'nova ranger 4x4': 'ranger',
            'nova ranger 4x2': 'ranger',
            'ranger raptor': 'ranger',
            'novo mustang': 'mustang',
            'l200 triton': 'l200',
            'l200 triton sport': 'l200',
            'defender 130': 'defender',
            'defender 110': 'defender',
            'range rover sport': 'range rover',
            'amg gla 354m': 'gla',
            'amg a45s 4matic': 'a45',
            'amg g63 4m': 'g63',
            'g580 eq': 'g580',
            'q3 sportback': 'q3',
            'q5 sportback': 'q5',
            'q5 tfsi e': 'q5',
            'q7': 'q7',
            'q8 sportback': 'q8',
            'q8 e-tron sportback 55': 'q8 e-tron',
            'q8 e-tron 55': 'q8 e-tron',
            'e-tron gt': 'e-tron',
            'rs e-tron gt': 'e-tron',
            'sq8 e-tron sportback': 'q8 e-tron',
            'i4': 'i4',
            'i7': 'i7',
            'ix': 'ix',
            'i5': 'i5',
            'ix3': 'ix3',
            'ix xdrive 40': 'ix',
            'ix xdrive 50': 'ix',
            'ix m60': 'ix',
            'i5 m60xdrive': 'i5',
            '420i': '420i',
            '530e': '530e',
            '330e': '330e',
            '320i': '320i',
            '118i': '118i',
            'm3': 'm3',
            'm2': 'm2',
            'c40': 'c40',
            'ec40': 'ec40',
            'id.4': 'id4',
            't-cross': 't-cross',
            't-cross': 't-cross',
            'nivus': 'nivus',
            'saveiro': 'saveiro',
            'amarok': 'amarok',
            's10': 's10',
            'silverado': 'silverado',
            'montana': 'montana',
            'camaro': 'camaro',
            'spin': 'spin',
            'toro': 'toro',
            'titano': 'titano',
            'strada': 'strada',
            'fastback': 'fastback',
            'pulse': 'pulse',
            'argo': 'argo',
            'mobi': 'mobi',
            '500e': '500e',
            'ducato': 'ducato',
            'scudo': 'scudo',
            'e-scudo': 'scudo',
            'fiorino': 'fiorino',
            'transit': 'transit',
            'maverick': 'maverick',
            'hr': 'hr',
            'hb20': 'hb20',
            'creta': 'creta',
            'kicks': 'kicks',
            'sentra': 'sentra',
            'leaf': 'leaf',
            'frontier': 'frontier',
            'townstar': 'townstar',
            'kangoo': 'kangoo',
            'e-kangoo': 'kangoo',
            'master': 'master',
            'kwid': 'kwid',
            'e-kwid': 'kwid',
            'oroch': 'oroch',
            'sandero': 'sandero',
            'kardian': 'kardian',
            '2008': '2008',
            'e-208': '208',
            '208': '208',
            'expert': 'expert',
            'e-expert': 'expert',
            'partner': 'partner',
            'boxer': 'boxer',
            'jumper': 'jumper',
            'jumpy': 'jumpy',
            'e-jumpy': 'jumpy',
            'renegade': 'renegade',
            'compass': 'compass',
            'commander': 'commander',
            'gladiator': 'gladiator',
            'pajero sport': 'pajero',
            'l200': 'l200',
            'sportage': 'sportage',
            'carnival': 'carnival',
            'bongo': 'bongo',
            'nx 350h': 'nx',
            'levante': 'levante',
            'rampage': 'rampage',
            '1500': '1500',
            'classic': 'classic',
            'dolphin': 'dolphin',
            'dolphin mini': 'dolphin',
            'han': 'han',
            'tan': 'tan',
            'seal': 'seal',
            'king': 'king',
            'song plus': 'song',
            'songplus': 'song',
            'yuan plus': 'yuan',
            'tiggo 8': 'tiggo',
            'tiggo 7': 'tiggo',
            'icar eq1': 'icar',
            'e-js1': 'js1',
            'et3': 'et3',
            'ejv5.5': 'ejv',
            'haval h6': 'haval',
            'seres 3': 'seres',
            'cooper': 'cooper',
            'jcw': 'jcw',
            'civic': 'civic',
            'cr-v hybrid': 'cr-v',
            'type-r': 'civic',
            'carnival': 'carnival',
            'bongo k2500 4x4 sc': 'bongo',
            'bongo k2500 4x4': 'bongo',
            '315cdi street': '315',
            '315cdi': '315'
        }

        # 1) Busca marcas
        r = session.get(f"{base}/marcas", timeout=10)
        if r.status_code != 200:
            return 0, "FIPE indisponível"
        
        marcas = r.json()
        marca_alvo = marca.lower().strip()
        
        # Busca marca (tenta match exato primeiro, depois parcial)
        marca_item = None
        for m in marcas:
            nome_marca = m.get('nome', '').lower().strip()
            if nome_marca == marca_alvo or marca_alvo in nome_marca:
                marca_item = m
                break
        
        if not marca_item:
            return 0, f"Marca '{marca}' não encontrada na FIPE"

        # 2) Busca modelos da marca
        r = session.get(f"{base}/marcas/{marca_item['codigo']}/modelos", timeout=10)
        if r.status_code != 200:
            return 0, "FIPE indisponível"
        
        modelos = r.json().get('modelos', [])
        modelo_original = modelo.lower().strip()
        modelo_alvo = modelo_map.get(modelo_original, modelo_original)
        
        # Busca modelo (tenta match exato primeiro, depois parcial)
        modelo_item = None
        for m in modelos:
            nome_modelo = m.get('nome', '').lower().strip()
            if (nome_modelo == modelo_alvo or modelo_alvo in nome_modelo or 
                nome_modelo == modelo_original or modelo_original in nome_modelo):
                modelo_item = m
                break
        
        if not modelo_item:
            return 0, f"Modelo '{modelo}' não encontrado na FIPE"

        # 3) Busca anos do modelo
        r = session.get(f"{base}/marcas/{marca_item['codigo']}/modelos/{modelo_item['codigo']}/anos", timeout=10)
        if r.status_code != 200:
            return 0, "FIPE indisponível"
        
        anos = r.json()
        if not anos:
            return 0, "Sem anos disponíveis na FIPE"
        
        # Pega o ano mais recente (último da lista)
        ano_codigo = anos[-1]['codigo']

        # 4) Busca preço do ano mais recente
        r = session.get(f"{base}/marcas/{marca_item['codigo']}/modelos/{modelo_item['codigo']}/anos/{ano_codigo}", timeout=10)
        if r.status_code != 200:
            return 0, "FIPE indisponível"
        
        dados = r.json()
        valor = dados.get('Valor')
        if not valor:
            return 0, "Preço não disponível na FIPE"
        
        # Converte valor para float
        valor_str = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try:
            preco = float(valor_str)
            print(f"FIPE: {marca} {modelo} = R$ {preco:,.2f}")
            return preco, [preco]
        except ValueError:
            return 0, "Erro ao converter preço FIPE"
            
    except Exception as e:
        print(f"Erro FIPE para {marca}/{modelo}: {e}")
        return 0, "Erro na consulta FIPE"

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
    marca_slug = slugify(marca)
    modelo_slug = slugify(modelo)
    url = (
        "https://www.webmotors.com.br/api/search/car"
        "?displayPerPage=10"
        "&actualPage=1"
        "&showMenu=true"
        "&showCount=true"
        "&showBreadCrumb=true"
        "&order=1"
        f"&url=https://www.webmotors.com.br/carros/estoque/{marca_slug}/{modelo_slug}?marca={marca_slug}&modelo={modelo_slug}&autocomplete={modelo_slug}&autocompleteTerm={marca.title()}%20{modelo.title()}&tipoveiculo=carros&marca1={marca.upper()}&modelo1={modelo.upper()}&page=1"
        "&mediaZeroKm=true"
    )
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Referer': 'https://www.webmotors.com.br/',
        'Origin': 'https://www.webmotors.com.br'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"Webmotors respondeu {r.status_code} para {marca}/{modelo}")
            return 0, "Carro não encontrado"
    except requests.exceptions.ConnectionError as e:
        print(f"Erro de conexão para {marca}/{modelo}: {e}")
        return 0, "Erro de conexão"
    except requests.exceptions.Timeout as e:
        print(f"Timeout para {marca}/{modelo}: {e}")
        return 0, "Timeout"
    except Exception as e:
        print(f"Erro inesperado para {marca}/{modelo}: {e}")
        return 0, "Erro inesperado"
    try:
        data = r.json()
    except Exception as e:
        print("Falha ao parsear JSON da Webmotors:", e)
        return 0, "Carro não encontrado"

    # Tenta diferentes formas de onde podem estar os resultados
    candidatos_listas = [
        data.get("SearchResults"),
        data.get("searchResults"),
        data.get("SearchResult"),
        data.get("Vehicles"),
        data.get("Result"),
    ]
    resultados = None
    for lista in candidatos_listas:
        if isinstance(lista, list) and len(lista) > 0:
            resultados = lista
            break
    if resultados is None:
        print("Formato inesperado na resposta da Webmotors. Chaves no topo:", list(data.keys())[:10])
        return 0, "Carro não encontrado"

    precos = []
    for anuncio in resultados[:limite]:
        price = None
        if isinstance(anuncio, dict):
            price = (
                anuncio.get("Prices", {}).get("Price")
                or anuncio.get("Prices", {}).get("salePrice")
                or anuncio.get("Price")
            )
        if price is not None:
            try:
                precos.append(float(price))
            except Exception:
                # Às vezes vem string com separadores
                try:
                    precos.append(float(re.sub(r"[^0-9.,]", "", str(price)).replace('.', '').replace(',', '.')))
                except Exception:
                    pass
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
    - preço médio do veículo (FIPE primeiro, Webmotors como fallback)
    - lista de preços encontrados
    - quantidade de reclamações (ReclameAqui)
    Exemplo de uso:
    GET /api/info_carro?marca=honda&modelo=civic
    """
    marca = request.args.get('marca', '').strip()
    modelo = request.args.get('modelo', '').strip()
    
    # Tenta FIPE primeiro (mais confiável)
    print(f"Tentando FIPE para {marca}/{modelo}...")
    preco_medio, precos = buscar_precos_fipe(marca, modelo)
    fonte = "FIPE"
    
    # Se FIPE falhar, tenta Webmotors como fallback
    if preco_medio == 0:
        print(f"FIPE falhou para {marca}/{modelo}, tentando Webmotors...")
        preco_medio, precos = buscar_precos_webmotors(marca, modelo)
        fonte = "Webmotors"
    else:
        print(f"FIPE encontrou preço: R$ {preco_medio:,.2f}")
    
    # reclamacoes = buscar_reclamacoes_reclameaqui(marca, modelo)

    return jsonify({
        'preco_medio': preco_medio,
        'precos': precos,
        'fonte': fonte,
        # 'reclamacoes': reclamacoes
    })

if __name__ == '__main__':
    # Inicia o servidor Flask em modo debug
    app.run(debug=True)