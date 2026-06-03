import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def coletar_fatos_google_news(termos, sites_confiaveis):
    dados = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for termo in termos:
        for site in sites_confiaveis:
            print(f"Buscando notícias reais sobre '{termo}' no site '{site}'...")
            
            # Monta a query de busca avançada para o Google News RSS
            query = f'"{termo}" site:{site}'
            url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            
            try:
                resposta = requests.get(url, headers=headers)
                if resposta.status_code == 200:
                    # O Google News retorna os dados em XML
                    soup = BeautifulSoup(resposta.content, 'xml')
                    itens = soup.find_all('item')
                    
                    for item in itens:
                        titulo_completo = item.title.text
                        
                        # O Google News costuma colocar " - G1" ou " - Agência Brasil" no fim da manchete.
                        # O comando rsplit isola a manchete do nome do portal para não sujar os dados.
                        titulo_limpo = titulo_completo.rsplit(' - ', 1)[0].strip()
                        
                        dados.append({
                            "texto": titulo_limpo,
                            "classe": "fato"
                        })
                time.sleep(2) # Pausa para não sobrecarregar a API
                
            except Exception as e:
                print(f"Erro na busca do termo {termo} no site {site}: {e}")
                
    return pd.DataFrame(dados)

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    # Termos mais associados ao universo do seu problema
    termos_busca = ["PIX", "MEI", "Banco Central", "Receita Federal", "Simples Nacional"]
    
    # Fontes jornalísticas e governamentais de alta credibilidade
    sites_oficiais = ["g1.globo.com/economia", "agenciabrasil.ebc.com.br", "gov.br/receitafederal"]
    
    df_fatos = coletar_fatos_google_news(termos_busca, sites_oficiais)
    
    if not df_fatos.empty:
        # Remove possíveis manchetes duplicadas (caso dois termos achem a mesma notícia)
        df_fatos = df_fatos.drop_duplicates(subset=['texto']).reset_index(drop=True)
        
        # Exporta o CSV
        nome_arquivo = "base_fatos.csv"
        df_fatos.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"\nSucesso! {len(df_fatos)} manchetes verdadeiras coletadas.")
        print(f"Arquivo '{nome_arquivo}' salvo.")
        print("\nAmostra dos fatos coletados:")
        print(df_fatos.head())
    else:
        print("\nNenhum dado encontrado.")