import pandas as pd

try:
    # Lendo o arquivo CSV com ponto e vírgula como separador
    df = pd.read_csv('projeto-busca-carros/dados_corrigidos_sem_duplicatas.csv', sep=';')
    
    print("\nColunas do DataFrame:")
    print(df.columns.tolist())
    
    print("\nValores únicos na coluna 'Selo CONPET de Eficiência Energética':")
    print(df['Selo CONPET de Eficiência Energética'].unique())
    
    print("\nValores únicos na coluna 'Classificação PBE (Absoluta na Categoria)':")
    print(df['Classificação PBE (Absoluta na Categoria)'].unique())
    
    print("\nPrimeiras 5 linhas do DataFrame:")
    print(df.head())

except Exception as e:
    print(f"Erro ao processar o arquivo: {str(e)}") 