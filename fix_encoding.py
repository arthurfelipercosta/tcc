import pandas as pd
import re

# 1. Carregue o arquivo original
print("Carregando dados.csv...")
df = pd.read_csv(
    'dados.csv',
    sep=';',
    encoding='utf-8',  # ou 'latin-1', 'cp1252' se necessário
    dtype=str,
    engine='python',
    keep_default_na=False
)

# 2. Carregue o arquivo de mapeamento (que já tem as palavras corretas)
palavras_corretas = pd.read_csv('corrompidos.csv', sep=';', encoding='utf-8-sig')

# 3. Crie o dicionário de mapeamento (vamos buscar as palavras com no CSV original)
mapeamento = {}

# Execute uma busca por todos os valores que contêm ''
print("Buscando valores com caracteres corrompidos...")
for coluna in df.columns:
    mask = df[coluna].astype(str).str.contains('', regex=False, na=False)
    valores_corrompidos = df.loc[mask, coluna].unique()
    
    for valor_corrompido in valores_corrompidos:
        # Tente encontrar a palavra correspondente no arquivo de mapeamento
        # Remova todos os, acentos e deixe apenas letras básicas para comparação
        valor_simplificado = re.sub(r'[^a-zA-Z0-9]', '', valor_corrompido.lower())
        
        for _, row in palavras_corretas.iterrows():
            palavra_correta = row['novos']
            palavra_simplificada = re.sub(r'[^a-zA-Z0-9]', '', palavra_correta.lower())
            
            # Se a versão simplificada bater, use como mapeamento
            if valor_simplificado == palavra_simplificada:
                mapeamento[valor_corrompido] = palavra_correta
                print(f"Mapeamento: '{valor_corrompido}' → '{palavra_correta}'")
                break

print(f"Total de {len(mapeamento)} mapeamentos encontrados")

# 4. Aplique as correções
print("Aplicando correções...")
df_corrigido = df.replace(mapeamento)

# 5. Salve o resultado
print("Salvando arquivo corrigido...")
df_corrigido.to_csv('dados_corrigidos.csv', sep=';', index=False, encoding='utf-8')

print("✓ Concluído! Arquivo salvo como 'dados_corrigidos.csv'")