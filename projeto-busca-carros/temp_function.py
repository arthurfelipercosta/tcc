def top10_fipe_por_marca(marca: str, ordem: str='asc', limite: int=10):
    """
    Top 10 carros de uma marca ordenados por preço FIPE.
    
    Esta função busca todos os modelos de uma marca específica no CSV local,
    consulta os preços na API FIPE para cada modelo e retorna o top N
    ordenados por preço (mais baratos ou mais caros).
    
    Args:
        marca (str): Marca do veículo (ex: "FIAT")
        ordem (str): 'asc' para mais baratos primeiro, 'desc' para mais caros
        limite (int): Número de carros a retornar (default: 10)
    
    Returns:
        dict: {
            'sucesso': bool,
            'marca': str,
            'ordem': str,
            'total_encontrados': int,
            'total_modelos_disponiveis': int,
            'items': [{'marca': str, 'modelo': str, 'preco': float, 'fonte': str}]
        }
    """
    _carregar_catalogo()
    if not _catalogo_rows:
        return {'sucesso': False, 'erro': 'CSV vazio'}

    # Filtrar carros da marca especificada
    marca_alvo = (marca or '').strip().lower()
    carros_marca = []
    
    for row in _catalogo_rows:
        marca_row = (row.get('Marca') or row.get('marca') or '').strip().lower()
        if marca_row == marca_alvo:
            modelo = (row.get('Modelo') or row.get('modelo') or '').strip()
            if modelo:
                carros_marca.append(modelo)
    
    # Remover duplicatas mantendo ordem
    modelos_unicos = []
    seen = set()
    for modelo in carros_marca:
        if modelo.lower() not in seen:
            seen.add(modelo.lower())
            modelos_unicos.append(modelo)
    
    if not modelos_unicos:
        return {'sucesso': False, 'erro': f'Nenhum modelo encontrado para a marca {marca}'}
    
    # Buscar preços na FIPE para cada modelo
    precos_carros = []
    for modelo in modelos_unicos[:20]:  # Limitar a 20 para não sobrecarregar
        try:
            preco, _ = buscar_precos_fipe(marca, modelo)
            if preco > 0:
                precos_carros.append({
                    'marca': marca.upper(),
                    'modelo': modelo,
                    'preco': preco,
                    'fonte': 'FIPE'
                })
        except Exception as e:
            print(f"Erro ao buscar preço para {marca} {modelo}: {e}")
            continue
    
    if not precos_carros:
        return {'sucesso': False, 'erro': f'Nenhum preço FIPE encontrado para a marca {marca}'}
    
    # Ordenar por preço
    reverse = (ordem or 'asc').lower() == 'desc'
    precos_carros.sort(key=lambda x: x['preco'], reverse=reverse)
    
    # Retornar top N
    top_carros = precos_carros[:limite]
    
    return {
        'sucesso': True,
        'marca': marca.upper(),
        'ordem': 'desc' if reverse else 'asc',
        'total_encontrados': len(precos_carros),
        'total_modelos_disponiveis': len(modelos_unicos),
        'items': top_carros
    }
