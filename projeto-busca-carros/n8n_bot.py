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
Backend Flask para consulta de informações de veículos com integração a:
- Webmotors (preços) via chamada pública
- Catálogo local (CSV) para validação de marca/modelo e listagem de versões

Principais endpoints (GET):
- /api/validar_marca?marca=FIAT
    Confere se a marca existe no CSV.
- /api/validar_modelo?marca=FIAT&modelo=MOBI
    Confere se o modelo existe no CSV (independente da marca informada).
- /api/versoes?marca=FIAT&modelo=MOBI
    Lista versões únicas do CSV para a combinação marca+modelo.
- /api/validar_versao?marca=FIAT&modelo=MOBI&numero=1
    Valida se o número informado corresponde a uma versão da lista retornada em /api/versoes.
- /api/info_carro?marca=honda&modelo=civic
    Busca preços na Webmotors e retorna média e amostras.

Observação: código para uso acadêmico/experimental.
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
    """Carregar o CSV uma vez na memória.

    - Usa o caminho definido em CSV_PATH (env ou default)
    - Detecta automaticamente o separador ("," ou ";")
    - Preenche a lista global `_catalogo_rows`
    """
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
    """Listar versões únicas do CSV para marca+modelo (case-insensitive).

    Params:
        marca: Nome da marca (ex.: "FIAT")
        modelo: Nome do modelo (ex.: "MOBI")
        max_items: Limite máximo de versões a retornar (default: 25)

    Returns:
        list[str]: Versões únicas em ordem de primeira ocorrência no CSV
    """
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

def _parse_number(value):
    """Converter valores do CSV para float, lidando com vírgula decimal e 'ND'."""
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() == 'ND' or s == '-':
        return None
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None

def _buscar_linha_catalogo(marca: str, modelo: str, versao: str):
    """Encontrar primeira linha do CSV que case exatamente marca+modelo+versão (case-insensitive)."""
    _carregar_catalogo()
    m = (marca or '').strip().lower()
    mod = (modelo or '').strip().lower()
    ver = (versao or '').strip().lower()
    for row in _catalogo_rows:
        marca_row = (row.get('Marca') or row.get('marca') or '').strip().lower()
        modelo_row = (row.get('Modelo') or row.get('modelo') or '').strip().lower()
        versao_row = (row.get('Versão') or row.get('versão') or '').strip().lower()
        if m == marca_row and mod == modelo_row and ver == versao_row:
            return row
    return None

def pesquisar_preco(marca, modelo):
    """
    Função para testar busca de preços na FIPE via parallelum.
    
    Args:
        marca (str): Marca do veículo (ex.: "FIAT")
        modelo (str): Modelo do veículo (ex.: "MOBI")
    
    Returns:
        dict: Resultado da pesquisa com preços e informações
    """
    try:
        session = requests.Session()
        base = "https://parallelum.com.br/fipe/api/v1/carros"
        
        print(f"🔍 Pesquisando: {marca.upper()} {modelo.upper()}")
        
        # 1. Buscar marcas
        print("📋 Buscando marcas...")
        marcas = session.get(f"{base}/marcas").json()
        marca_id = None
        marca_nome = None
        
        for m in marcas:
            if marca.lower() in m['nome'].lower() or m['nome'].lower() in marca.lower():
                marca_id = m['codigo']
                marca_nome = m['nome']
                print(f"✅ Marca encontrada: {marca_nome} (ID: {marca_id})")
                break
        
        if not marca_id:
            return {
                'sucesso': False,
                'erro': f"Marca '{marca}' não encontrada na FIPE",
                'marcas_disponiveis': [m['nome'] for m in marcas[:10]]  # Primeiras 10 para referência
            }
        
        # 2. Buscar modelos da marca
        print(f"🚗 Buscando modelos da marca {marca_nome}...")
        modelos = session.get(f"{base}/marcas/{marca_id}/modelos").json()
        modelo_id = None
        modelo_nome = None
        
        for m in modelos['modelos']:
            if modelo.lower() in m['nome'].lower() or m['nome'].lower() in modelo.lower():
                modelo_id = m['codigo']
                modelo_nome = m['nome']
                print(f"✅ Modelo encontrado: {modelo_nome} (ID: {modelo_id})")
                break
        
        if not modelo_id:
            return {
                'sucesso': False,
                'erro': f"Modelo '{modelo}' não encontrado para marca '{marca_nome}'",
                'modelos_disponiveis': [m['nome'] for m in modelos['modelos'][:10]]
            }
        
        # 3. Buscar anos do modelo
        print(f"📅 Buscando anos do modelo {modelo_nome}...")
        anos = session.get(f"{base}/marcas/{marca_id}/modelos/{modelo_id}/anos").json()
        
        if not anos:
            return {
                'sucesso': False,
                'erro': f"Nenhum ano encontrado para {marca_nome} {modelo_nome}"
            }
        
        print(f"📅 Anos disponíveis: {[ano['nome'] for ano in anos]}")
        
        # 4. Pegar o ano mais recente
        # Função para extrair o ano do código (ex: "2020-5" -> 2020)
        def extrair_ano(codigo):
            try:
                # Se o código tem formato "2020-5", pega só a parte do ano
                if '-' in str(codigo):
                    return int(str(codigo).split('-')[0])
                return int(codigo)
            except (ValueError, TypeError):
                return 0  # Retorna 0 para códigos inválidos
        
        ano_mais_recente = max(anos, key=lambda x: extrair_ano(x['codigo']))
        ano_codigo = ano_mais_recente['codigo']
        ano_nome = ano_mais_recente['nome']
        
        print(f"🎯 Usando ano mais recente: {ano_nome}")
        
        # 5. Buscar preço do ano mais recente
        print(f"💰 Buscando preço para {marca_nome} {modelo_nome} {ano_nome}...")
        preco_data = session.get(f"{base}/marcas/{marca_id}/modelos/{modelo_id}/anos/{ano_codigo}").json()
        
        if 'Valor' in preco_data:
            # Converter valor de string para float
            valor_str = preco_data['Valor'].replace('R$ ', '').replace('.', '').replace(',', '.')
            valor = float(valor_str)
            
            resultado = {
                'sucesso': True,
                'marca': marca_nome,
                'modelo': modelo_nome,
                'ano': ano_nome,
                'preco': valor,
                'preco_formatado': preco_data['Valor'],
                'codigo_fipe': preco_data.get('CodigoFipe', ''),
                'referencia': preco_data.get('MesReferencia', ''),
                'todos_anos': [ano['nome'] for ano in anos]
            }
            
            print(f"✅ Preço encontrado: {preco_data['Valor']}")
            return resultado
        else:
            return {
                'sucesso': False,
                'erro': f"Preço não encontrado para {marca_nome} {modelo_nome} {ano_nome}",
                'dados_recebidos': preco_data
            }
        
    except Exception as e:
        print(f"❌ Erro na pesquisa: {e}")
        return {
            'sucesso': False,
            'erro': f"Erro na consulta: {str(e)}"
        }

# ========= FIPE =========
def buscar_precos_fipe(marca, modelo):
    """
    Busca preço na FIPE usando a API pública (parallelum.com.br).
    Retorna preço do ano mais recente disponível.
    """
    try:
        session = requests.Session()
        base = "https://parallelum.com.br/fipe/api/v1/carros"
        
        # Buscar marcas
        marcas = session.get(f"{base}/marcas").json()
        marca_id = None
        for m in marcas:
            if marca.lower() in m['nome'].lower() or m['nome'].lower() in marca.lower():
                marca_id = m['codigo']
                break
        
        if not marca_id:
            return 0, "Marca não encontrada na FIPE"
        
        # Buscar modelos da marca
        modelos = session.get(f"{base}/marcas/{marca_id}/modelos").json()
        modelo_id = None
        for m in modelos['modelos']:
            if modelo.lower() in m['nome'].lower() or m['nome'].lower() in modelo.lower():
                modelo_id = m['codigo']
                break
        
        if not modelo_id:
            return 0, "Modelo não encontrado na FIPE"
        
        # Buscar anos do modelo
        anos = session.get(f"{base}/marcas/{marca_id}/modelos/{modelo_id}/anos").json()
        if not anos:
            return 0, "Anos não encontrados na FIPE"
        
        # Pegar o ano mais recente
        # Função para extrair o ano do código (ex: "2020-5" -> 2020)
        def extrair_ano(codigo):
            try:
                # Se o código tem formato "2020-5", pega só a parte do ano
                if '-' in str(codigo):
                    return int(str(codigo).split('-')[0])
                return int(codigo)
            except (ValueError, TypeError):
                return 0  # Retorna 0 para códigos inválidos
        
        ano_mais_recente = max(anos, key=lambda x: extrair_ano(x['codigo']))
        ano_codigo = ano_mais_recente['codigo']
        
        # Buscar preço do ano mais recente
        preco_data = session.get(f"{base}/marcas/{marca_id}/modelos/{modelo_id}/anos/{ano_codigo}").json()
        
        if 'Valor' in preco_data:
            # Converter valor de string para float
            valor_str = preco_data['Valor'].replace('R$ ', '').replace('.', '').replace(',', '.')
            valor = float(valor_str)
            return valor, [valor]  # Retorna como lista para compatibilidade
        
        return 0, "Preço não encontrado na FIPE"
        
    except Exception as e:
        print(f"Erro FIPE: {e}")
        return 0, "Erro na consulta FIPE"

# ========= Webmotors =========
def buscar_precos_webmotors(marca, modelo, limite=10):
    """Consulta a API pública do Webmotors para obter preços.

    Args:
        marca (str): Marca do veículo (ex.: "honda")
        modelo (str): Modelo do veículo (ex.: "civic")
        limite (int): Máximo de preços a coletar (default: 10)

    Returns:
        tuple[float, list[float] | str]:
            (media, precos) quando sucesso; (0, "Carro não encontrado") quando vazio/erro.
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
    """Valida se uma marca existe no CSV (case-insensitive).

    Query:
        - marca: nome da marca (ex.: FIAT)

    Response JSON:
        - valid (bool): True se encontrada
        - marca (str): Entrada normalizada para UPPERCASE
        - error (str, opcional): quando entrada ausente
    """
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
    """Valida se um modelo existe no CSV (case-insensitive).

    Query:
        - modelo: nome do modelo (ex.: MOBI)
        - marca: nome da marca (opcional, usado apenas para eco/depuração)

    Response JSON:
        - valid (bool): True se encontrado
        - modelo_input (str): valor recebido
        - modelo_upper (str): normalizado para UPPERCASE
        - marca_upper (str): marca em UPPERCASE (eco)
        - encontrado (bool): igual a valid
    """
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

@app.route('/api/validar_versao', methods=['GET'])
def validar_versao():
    """Valida se o número informado corresponde a uma versão de marca+modelo.

    Query:
        - marca: nome da marca (ex.: FIAT)
        - modelo: nome do modelo (ex.: MOBI)
        - numero: índice 1-based escolhido pelo usuário (ex.: 1, 2, ...)

    Response JSON (válido):
        - valid (bool) = True
        - marca (str)
        - modelo (str)
        - numero (int): o número recebido
        - versao (str): versão selecionada
        - total (int): total de versões disponíveis
        - versoes (list[str]): lista de versões (para referência)

    Response JSON (inválido):
        - valid (bool) = False
        - error (str): motivo (inválido/fora do intervalo)
        - demais campos para contexto

    Exemplo:
        /api/validar_versao?marca=FIAT&modelo=MOBI&numero=1
    """
    marca = request.args.get('marca', '')
    modelo = request.args.get('modelo', '')
    numero_raw = request.args.get('versao', '')

    # Listar versões possíveis
    versoes = _listar_versoes(marca, modelo)
    total = len(versoes)

    # Validar número
    try:
        numero = int(str(numero_raw).strip())
    except (TypeError, ValueError):
        return jsonify({
            'valid': False,
            'error': 'numero inválido',
            'marca': marca,
            'modelo': modelo,
            'numero': numero_raw,
            'versao': None,
            'total': total,
            'versoes': versoes,
        })

    # Converter para índice 0-based
    idx = numero - 1
    if idx < 0 or idx >= total:
        return jsonify({
            'valid': False,
            'error': 'numero fora do intervalo',
            'marca': marca,
            'modelo': modelo,
            'numero': numero,
            'versao': None,
            'total': total,
            'versoes': versoes,
        })

    versao_escolhida = versoes[idx]
    return jsonify({
        'valid': True,
        'marca': marca,
        'modelo': modelo,
        'numero': numero,
        'versao': versao_escolhida,
        'total': total,
        'versoes': versoes,
    })

@app.route('/api/comparativo', methods=['GET'])
def comparativo():
    """Gera um comparativo entre dois carros e retorna mensagens sequenciais.

    Query:
        - marca1, modelo1, versao1 (numero 1-based da lista /api/versoes)
        - marca2, modelo2, versao2 (numero 2-based)

    Retorna JSON:
        - messages (list[str]): mensagens em ordem para enviar no n8n
        - placar (dict): { carro1: int, carro2: int, empate: int }
        - detalhes (dict): métricas usadas na comparação
    """
    p = request.args

    marca1 = p.get('marca1', '')
    modelo1 = p.get('modelo1', '')
    numero_raw1 = p.get('versao1', '')
    marca2 = p.get('marca2', '')
    modelo2 = p.get('modelo2', '')
    numero_raw2 = p.get('versao2', '')

    # Resolver versões pelo índice
    versoes1 = _listar_versoes(marca1, modelo1)
    versoes2 = _listar_versoes(marca2, modelo2)

    try:
        idx1 = int(str(numero_raw1).strip()) - 1
        idx2 = int(str(numero_raw2).strip()) - 1
    except (TypeError, ValueError):
        return jsonify({'error': 'versao1/versao2 inválidas', 'valid': False}), 400

    if idx1 < 0 or idx1 >= len(versoes1) or idx2 < 0 or idx2 >= len(versoes2):
        return jsonify({'error': 'versao fora do intervalo', 'valid': False}), 400

    versao1 = versoes1[idx1]
    versao2 = versoes2[idx2]

    # Preços FIPE primeiro, Webmotors como fallback
    def buscar_preco_com_fallback(marca, modelo):
        # Tenta FIPE primeiro
        media, precos = buscar_precos_fipe(marca, modelo)
        fonte = "FIPE"
        
        # Se FIPE falhar, tenta Webmotors
        if media == 0:
            media, precos = buscar_precos_webmotors(marca.lower(), modelo.lower())
            fonte = "Webmotors"
        
        return media, precos, fonte
    
    media1, precos1, fonte1 = buscar_preco_com_fallback(marca1, modelo1)
    media2, precos2, fonte2 = buscar_preco_com_fallback(marca2, modelo2)

    amostras1 = len(precos1) if isinstance(precos1, list) else 0
    amostras2 = len(precos2) if isinstance(precos2, list) else 0

    # Poluentes e GEE do CSV
    row1 = _buscar_linha_catalogo(marca1, modelo1, versao1)
    row2 = _buscar_linha_catalogo(marca2, modelo2, versao2)

    def extrair_metricas(row):
        if not row:
            return {}
        return {
            'nmog_nox': _parse_number(row.get('Poluentes(NMOG+NOx [mg/km])')),
            'co': _parse_number(row.get('Poluentes(CO [mg/km])')),
            'cho': _parse_number(row.get('Poluentes(CHO [mg/km])')),
            'gee_etanol': _parse_number(row.get('Gás Efeito Estufa (Etanol [CO2 fóssil] [g/km])')),
            'gee_gas': _parse_number(row.get('Gás Efeito Estufa (Gasolina ou Diesel [CO2 fóssil] [g/km])')),
            'consumo_gas_cidade': _parse_number(row.get('Km - (Gasolina ou Diesel[Cidade][km/l])')),
            'consumo_gas_estrada': _parse_number(row.get('Km - (Gasolina ou Diesel[Estrada][km/l])')),
        }

    m1 = extrair_metricas(row1)
    m2 = extrair_metricas(row2)

    # Placar e mensagens
    placar = {'carro1': 0, 'carro2': 0, 'empate': 0}
    messages = []

    titulo = f"Comparativo:\nCarro 1: {marca1.upper()} {modelo1.upper()} - {versao1}\nCarro 2: {marca2.upper()} {modelo2.upper()} - {versao2}"
    messages.append(titulo)

    # Preço médio
    if media1 and media2 and isinstance(media1, (int, float)) and isinstance(media2, (int, float)):
        messages.append(f"Preço médio ({fonte1}/{fonte2}):\n1) R$ {media1:,.0f} ({amostras1} amostras)\n2) R$ {media2:,.0f} ({amostras2} amostras)")
        if media1 == media2:
            placar['empate'] += 1
            messages.append('Preço: Empate')
        else:
            vencedor_preco = 'carro1' if media1 < media2 else 'carro2'
            placar[vencedor_preco] += 1
            mais_barato = 'Carro 1' if vencedor_preco == 'carro1' else 'Carro 2'
            messages.append(f'Preço: {mais_barato} leva o ponto')
    else:
        messages.append('Preço médio: dados insuficientes')

    # Poluentes: quanto menor, melhor
    def comparar_campo(label, v1, v2):
        if v1 is None or v2 is None:
            messages.append(f"{label}: dados insuficientes")
            return
        if v1 == v2:
            placar['empate'] += 1
            messages.append(f"{label}: Empate ({v1})")
        else:
            vencedor = 'carro1' if v1 < v2 else 'carro2'
            placar[vencedor] += 1
            melhor = 'Carro 1' if vencedor == 'carro1' else 'Carro 2'
            messages.append(f"{label}: {melhor} melhor ({v1} vs {v2})")

    comparar_campo('NMOG+NOx [mg/km]', m1.get('nmog_nox'), m2.get('nmog_nox'))
    comparar_campo('CO [mg/km]', m1.get('co'), m2.get('co'))
    comparar_campo('CHO [mg/km]', m1.get('cho'), m2.get('cho'))
    comparar_campo('GEE (Etanol) [g/km]', m1.get('gee_etanol'), m2.get('gee_etanol'))
    comparar_campo('GEE (Gas/Diesel) [g/km]', m1.get('gee_gas'), m2.get('gee_gas'))

    # Consumo: quanto MAIOR km/l, melhor
    def comparar_consumo(label, v1, v2):
        if v1 is None or v2 is None:
            messages.append(f"{label}: dados insuficientes")
            return
        if v1 == v2:
            placar['empate'] += 1
            messages.append(f"{label}: Empate ({v1} km/l)")
        else:
            vencedor = 'carro1' if v1 > v2 else 'carro2'
            placar[vencedor] += 1
            melhor = 'Carro 1' if vencedor == 'carro1' else 'Carro 2'
            messages.append(f"{label}: {melhor} melhor ({v1} vs {v2} km/l)")

    comparar_consumo('Consumo Gasolina - Cidade', m1.get('consumo_gas_cidade'), m2.get('consumo_gas_cidade'))
    comparar_consumo('Consumo Gasolina - Estrada', m1.get('consumo_gas_estrada'), m2.get('consumo_gas_estrada'))

    # Resumo do placar
    resumo = f"Placar parcial -> Carro 1: {placar['carro1']} | Carro 2: {placar['carro2']} | Empates: {placar['empate']}"
    messages.append(resumo)

    return jsonify({
        'valid': True,
        'messages': messages,
        'placar': placar,
        'detalhes': {
            'carro1': {
                'marca': marca1, 'modelo': modelo1, 'versao': versao1,
                'preco_medio': media1, 'amostras': amostras1, 'fonte_preco': fonte1,
                **m1,
            },
            'carro2': {
                'marca': marca2, 'modelo': modelo2, 'versao': versao2,
                'preco_medio': media2, 'amostras': amostras2, 'fonte_preco': fonte2,
                **m2,
            }
        }
    })

@app.route('/api/info_carro', methods=['GET'])
def info_carro():
    """Retorna preço usando FIPE primeiro (fallback Webmotors) para marca+modelo.

    Query:
        - marca: ex.: honda
        - modelo: ex.: civic

    Response JSON:
        - preco_medio (float): preço FIPE (ano mais recente) ou média Webmotors
        - precos (list[float] | str): lista com um valor (FIPE) ou amostras (Webmotors) ou mensagem
        - fonte (str): "FIPE" ou "Webmotors"

    Exemplo:
    GET /api/info_carro?marca=honda&modelo=civic
    """
    marca = request.args.get('marca', '').strip()
    modelo = request.args.get('modelo', '').strip()

    # Tenta FIPE primeiro
    preco_medio, precos = buscar_precos_fipe(marca, modelo)
    fonte = 'FIPE'

    # Fallback: Webmotors
    if preco_medio == 0:
        preco_medio, precos = buscar_precos_webmotors(marca.lower(), modelo.lower())
        fonte = 'Webmotors'

    return jsonify({
        'preco_medio': preco_medio,
        'precos': precos,
        'fonte': fonte,
    })

@app.route('/api/versoes', methods=['GET'])
def versoes():
    """Lista versões únicas do CSV para a combinação marca+modelo.

    Query:
        - marca
        - modelo

    Response JSON:
        - marca (str)
        - modelo (str)
        - versoes (list[str])
    """
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
    """Compara dois carros pela média de preços (Webmotors).

    Query:
        - marca1, modelo1, versao1 (opcional)
        - marca2, modelo2, versao2 (opcional)

    Response JSON:
        - carro1: { marca, modelo, versao, preco_medio, amostras }
        - carro2: { marca, modelo, versao, preco_medio, amostras }
        - diferenca (float): media1 - media2
        - mais_barato (str): "carro1", "carro2" ou "empate"
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

    # Preços FIPE primeiro, Webmotors como fallback
    def buscar_preco_com_fallback(marca, modelo):
        # Tenta FIPE primeiro
        media, precos = buscar_precos_fipe(marca, modelo)
        fonte = "FIPE"
        
        # Se FIPE falhar, tenta Webmotors
        if media == 0:
            media, precos = buscar_precos_webmotors(marca.lower(), modelo.lower())
            fonte = "Webmotors"
        
        return media, precos, fonte
    
    media1, precos1, fonte1 = buscar_preco_com_fallback(c1['marca'], c1['modelo'])
    media2, precos2, fonte2 = buscar_preco_com_fallback(c2['marca'], c2['modelo'])

    amostras1 = len(precos1) if isinstance(precos1, list) else 0
    amostras2 = len(precos2) if isinstance(precos2, list) else 0

    diff = media1 - media2
    if media1 == media2:
        mais_barato = 'empate'
    else:
        mais_barato = 'carro1' if media1 < media2 else 'carro2'

    return jsonify({
        'carro1': {**c1, 'preco_medio': media1, 'amostras': amostras1, 'fonte': fonte1},
        'carro2': {**c2, 'preco_medio': media2, 'amostras': amostras2, 'fonte': fonte2},
        'diferenca': diff,
        'mais_barato': mais_barato
    })

# ========= TESTE TEMPORÁRIO =========
@app.route('/teste_preco', methods=['GET'])
def teste_preco():
    """Endpoint temporário para testar a função pesquisar_preco no browser."""
    marca = request.args.get('marca', 'FIAT')
    modelo = request.args.get('modelo', 'MOBI')
    
    resultado = pesquisar_preco(marca, modelo)
    return jsonify(resultado)

if __name__ == '__main__':
    # Inicia o servidor Flask em modo debug
    app.run(host='0.0.0.0', port=5000, debug=True)