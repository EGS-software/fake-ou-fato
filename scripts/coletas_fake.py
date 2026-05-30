import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def limpar_manchete_fake(titulo):
    """
    Remove os prefixos e sufixos de checagem para isolar apenas o boato.
    Exemplo: "É falso que governo vai cobrar taxa do PIX" -> "governo vai cobrar taxa do PIX"
    """
    # Converte para minúsculas para facilitar a limpeza
    titulo_limpo = titulo.lower()
    
    # Lista de expressões comuns usadas por sites de checagem
    padroes_remocao = [
        r"^é falso que\s*",
        r"^é boato que\s*",
        r"^boato:\s*",
        r"^falso:\s*",
        r"^fake news:\s*",
        r"^fake news sobre\s*",
        r"^nova fake news sobre\s*",
        r"^nova fake news sobe\s*", # Trata erros de digitação do próprio site
        r"^golpe cita que\s*",
        r"^golpe que aponta para\s*",
        r"^golpe (do|da) .*?:\s*",  # Remove coisas como "Golpe do Pix:"
        r"^novo alerta!\s*",
        r"^falso alerta sobre\s*",
        r"^fake sobre\s*",
        r"^mensagens falsas e golpes citando\s*",
        r"não é verdade que\s*",
        r"entenda o caso\s*",
        r"\s*#boato\s*$",           # Limpa a hashtag #boato no final
        r"\s*#fake\s*$"
    ]
    
    # Aplica as expressões regulares para limpar o texto
    for padrao in padroes_remocao:
        titulo_limpo = re.sub(padrao, "", titulo_limpo).strip()
        
    # Capitaliza a primeira letra para manter a formatação bonita no CSV
    if len(titulo_limpo) > 0:
        titulo_limpo = titulo_limpo.capitalize()
        
    return titulo_limpo

def coletar_fakes_boatos_org(termos_busca, paginas_por_termo=2):
    """
    Raspa o site Boatos.org buscando pelos termos específicos.
    """
    dados_coletados = []
    
    # O User-Agent é crucial para o site não achar que somos um ataque DDoS e bloquear a conexão
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for termo in termos_busca:
        print(f"\nIniciando busca por fakes do termo: {termo.upper()}")
        
        for pagina in range(1, paginas_por_termo + 1):
            print(f" -> Lendo página {pagina}...")
            # Estrutura de URL de busca padrão do WordPress
            url = f"https://www.boatos.org/?paged={pagina}&s={termo}"
            
            try:
                resposta = requests.get(url, headers=headers)
                
                # Se a página não existir (erro 404), interrompe a busca para este termo
                if resposta.status_code != 200:
                    break
                    
                soup = BeautifulSoup(resposta.text, 'html.parser')
                
                # No WordPress/Boatos.org, os títulos geralmente ficam em tags <h2> ou <h3> com classes específicas de título (entry-title)
                # O ideal é inspecionar o site e ajustar essa tag se necessário.
                artigos = soup.find_all(['h2', 'h3'], class_=re.compile("title", re.IGNORECASE))
                
                for artigo in artigos:
                    titulo_original = artigo.get_text(strip=True)
                    
                    # Filtro de segurança: só pega se o termo de busca estiver realmente no título
                    if termo.lower() in titulo_original.lower():
                        titulo_filtrado = limpar_manchete_fake(titulo_original)
                        
                        dados_coletados.append({
                            "texto_original": titulo_original, # Guardamos o original para auditoria visual
                            "texto": titulo_filtrado,          # O texto que vai pro Weka
                            "classe": "fake"
                        })
                
                # Pausa de 2 segundos entre as páginas para não sobrecarregar o servidor deles
                time.sleep(2)
                
            except Exception as e:
                print(f"Erro ao acessar {url}: {e}")

    return pd.DataFrame(dados_coletados)

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    termos_alvo = ["PIX", "MEI", "Guia DAS", "Taxa"]
    
    # Rodando a função (buscando 3 páginas de resultados para cada termo)
    df_fakes = coletar_fakes_boatos_org(termos_alvo, paginas_por_termo=3)
    
    if not df_fakes.empty:
        # Exporta o CSV
        nome_arquivo = "base_fakes_bruta.csv"
        # O encoding utf-8-sig garante que acentos fiquem corretos ao abrir no Excel ou Weka
        df_fakes.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        
        print(f"\nSucesso! {len(df_fakes)} manchetes capturadas e limpas.")
        print(f"Arquivo '{nome_arquivo}' salvo na pasta atual.")
        
        # Mostra uma amostra no terminal para você validar a coerência
        print("\nAmostra dos dados capturados:")
        print(df_fakes[['texto_original', 'texto']].head())
    else:
        print("\nNenhum dado foi encontrado. Verifique as tags do HTML.")