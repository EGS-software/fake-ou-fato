import pandas as pd
import re

# Carrega os dados fakes já limpos
df_fakes = pd.read_csv('base_fakes_limpa.csv')
# Mantém apenas as colunas necessárias
if 'texto_original' in df_fakes.columns:
    df_fakes = df_fakes[['texto', 'classe']]

# Carrega a base de fatos original
df_fatos = pd.read_csv('base_fatos.csv')
df_fatos = df_fatos.dropna(subset=['texto'])

# Sistema de pontuação para pegar as manchetes MAIS relevantes para o contexto
def pontuar_relevancia(texto):
    texto_lower = str(texto).lower()
    score = 0
    
    # Palavras de alto valor (peso 3) - Foco central do seu projeto
    altos = [r'\bmei\b', r'\btaxa\b', r'\bdas\b', r'\bsimples nacional\b', r'\bboleto\b', r'\bregulariza\w*\b', r'\bcobran[çc]a\b']
    for p in altos:
        if re.search(p, texto_lower): score += 3
        
    # Palavras de médio valor (peso 2)
    medios = [r'\bpix\b', r'\breceita federal\b', r'\bbanco central\b', r'\bcnpj\b', r'\bdeclara\w*\b', r'\bimpostos?\b', r'\bpagamento\b']
    for p in medios:
        if re.search(p, texto_lower): score += 2
        
    # Palavras de baixo valor (peso 1)
    baixos = [r'\bmulta\b', r'\btarifas?\b', r'\bguia\b', r'\bfazenda\b']
    for p in baixos:
        if re.search(p, texto_lower): score += 1
        
    # Penalidades severas para remover ruído (política, internacional, e palavras que confundem o modelo com fakes)
    penalidades = [r'trump', r'bolsonaro', r'lula', r'eua', r'estados unidos', r'golpe', r'fake', r'boato', r'fraude', r'falso']
    for p in penalidades:
        if re.search(p, texto_lower): score -= 10
        
    return score

# Aplica a pontuação
df_fatos['score'] = df_fatos['texto'].apply(pontuar_relevancia)

# Filtra apenas quem tem score positivo e ordena pelos mais relevantes
df_fatos_relevantes = df_fatos[df_fatos['score'] > 0].sort_values(by='score', ascending=False)

# Pega o mesmo número de linhas da base fake para ficar perfeitamente balanceado
num_fakes = len(df_fakes)
df_fatos_top = df_fatos_relevantes.head(num_fakes)[['texto', 'classe']]

# Junta as duas bases
df_final = pd.concat([df_fakes, df_fatos_top])

# Embaralha as linhas (Shuffle) e reseta o índice
df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

# Salva o arquivo final
nome_arquivo_weka = 'dataset_pix_mei_weka.csv'
df_final.to_csv(nome_arquivo_weka, index=False, encoding='utf-8-sig')

print(f"Total de Fakes: {len(df_fakes)}")
print(f"Total de Fatos selecionados: {len(df_fatos_top)}")
print(f"Total no Dataset Final: {len(df_final)}")
print("\n--- Amostra do Dataset Final Embaralhado ---")
print(df_final.head(10).to_string(index=False))