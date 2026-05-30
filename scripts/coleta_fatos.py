import feedparser
import pandas as pd
import re

def limpar_html(texto_bruto):
    """Remove tags HTML (como <a>, <img>) que costumam vir no resumo do RSS"""
    limpador = re.compile('<.*?>')
    return re.sub(limpador, '', texto_bruto).strip()

# 1. Definindo as fontes oficiais (RSS Feeds)
feeds_oficiais = [
    "https://g1.globo.com/rss/g1/economia/",
    "https://www12.senado.leg.br/noticias/feed/todas",
    "https://www.camara.leg.br/noticias/rss/"
]

# 2. Filtro de palavras-chave do nosso escopo
palavras_chave = ['pix', 'golpe', 'fraude', 'banco central', 'taxa', 'mei']

textos_coletados = []

print("Iniciando varredura de RSS...")

# 3. Varrendo cada link de RSS
for url in feeds_oficiais:
    feed = feedparser.parse(url)
    print(f"Lendo: {url} - ({len(feed.entries)} artigos encontrados no feed)")
    
    for artigo in feed.entries:
        # Juntamos o título e o resumo para ter um texto com mais contexto
        texto_completo = f"{artigo.title}. {artigo.description}"
        texto_limpo = limpar_html(texto_completo)
        
        # 4. Verificando se o artigo pertence ao nosso tema
        texto_minusculo = texto_limpo.lower()
        if any(palavra in texto_minusculo for palavra in palavras_chave):
            textos_coletados.append({
                'Texto': texto_limpo,
                'Classe': 'Fato'
            })

# 5. Criando o DataFrame e exportando
if textos_coletados:
    df_fatos = pd.DataFrame(textos_coletados)
    
    # Exporta para CSV, pronto para o Weka ou Scikit-Learn
    df_fatos.to_csv('base_fatos_pix.csv', index=False, encoding='utf-8')
    print(f"\nSucesso! {len(df_fatos)} textos reais sobre Pix/Golpes foram salvos em 'base_fatos_pix.csv'.")
else:
    print("\nNenhum artigo recente com as palavras-chave foi encontrado nestes feeds de hoje.")