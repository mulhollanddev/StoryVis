import streamlit as st
import pandas as pd
import tempfile
import re
import time
import os
import json
from crewai import LLM

@st.cache_data(ttl=3600, show_spinner=False)
def carregar_dados(uploaded_file):
    """Carrega CSV ou Excel com Cache."""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return None

def salvar_temp_csv(df):
    """Salva dataframe em temp file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8') as tmp:
        df.to_csv(tmp.name, index=False)
        return tmp.name

def limpar_codigo_ia(texto_bruto):
    """Limpa o código Python removendo textos extras."""
    if not texto_bruto: return ""
    padrao = r"```(?:python)?\s*(.*?)```"
    match = re.search(padrao, texto_bruto, re.DOTALL)
    if match: return match.group(1).strip()
    
    linhas = texto_bruto.split('\n')
    linhas_limpas = []
    for linha in linhas:
        l = linha.lower().strip()
        if l.startswith(("espero que", "hope this", "segue o", "aqui está", "qualquer dúvida")):
            break
        linhas_limpas.append(linha)
    return "\n".join(linhas_limpas).strip()

def separar_narrativa_codigo(raw_text):
    """Separa narrativa e código usando separador ou heurística."""
    narrativa = ""
    codigo_sujo = ""
    if "|||SEP|||" in raw_text:
        parts = raw_text.split("|||SEP|||")
        narrativa = parts[0].strip()
        if len(parts) > 1: codigo_sujo = parts[1]
    elif "```python" in raw_text:
        parts = raw_text.split("```python")
        narrativa = parts[0].strip()
        codigo_sujo = "```python" + parts[1]
    elif "import streamlit" in raw_text:
        idx = raw_text.find("import streamlit")
        narrativa = raw_text[:idx].strip()
        codigo_sujo = raw_text[idx:]
    else:
        narrativa = raw_text
    return narrativa, codigo_sujo

def inicializar_session_state(demo_func):
    """Inicializa todas as variáveis de estado necessárias."""
    if "df_final" not in st.session_state:
        df_demo, cod_demo, narr_demo = demo_func()
        st.session_state["df_final"] = df_demo
        st.session_state["codigo_final"] = cod_demo
        st.session_state["narrativa_final"] = narr_demo
        st.session_state["editor_codigo_area"] = cod_demo
        st.session_state["modo_demo"] = True
        st.session_state["nome_participante"] = ""

# --- 1. CONFIGURAÇÃO CENTRALIZADA DO LLM ---
def get_llm():
    """Retorna uma instância configurada do LLM (Groq) pronta para uso."""
    modelo_env = os.getenv("GROQ_MODEL", "")
    # Tratamento para prefixo do LiteLLM
    modelo_final = f"groq/{modelo_env}" if not modelo_env.startswith("groq/") else modelo_env
    
    return LLM(
        model=modelo_final,
        temperature=0, # Zero para máxima precisão lógica
        api_key=os.getenv("GROQ_API_KEY")
    )

# --- 2. DETECÇÃO INTELIGENTE DE COLUNAS (IA) ---
def detectar_coluna_geo_ia(df):
    """
    Estratégia Híbrida v2:
    1. Busca por palavras-chave expandida (Plurais, sem acento, prefixos comuns).
    2. Fallback para IA se nada óbvio for encontrado.
    """
    # Se já tem coordenadas, não faz nada
    if any(c.lower() in ['latitude', 'longitude', 'lat', 'lon'] for c in df.columns):
        return None

    colunas = list(df.columns)
    
    # --- FASE 1: BUSCA RÁPIDA (Expandida) ---
    # Adicionamos plurais e variações sem acento
    termos_comuns = [
        'município', 'municipio', 'municípios', 'municipios',
        'cidade', 'cidades', 'city', 'cities',
        'nm_mun', 'no_municipio', 'nome_municipio', 'nom_municipio',
        'localidade', 'local', 'cidade/uf', 'municipio_residencia'
    ]
    
    # 1. Busca Exata (case insensitive)
    for col in colunas:
        if col.lower().strip() in termos_comuns:
            return col
            
    # 2. Busca Parcial (ex: "Nome dos Municipios")
    for col in colunas:
        c_lower = col.lower()
        for termo in termos_comuns:
            # Verifica se o termo está contido na coluna (mas evita falsos positivos curtos)
            if termo in c_lower:
                return col

    # --- FASE 2: INTELIGÊNCIA ARTIFICIAL (Fallback) ---
    # Só aciona o LLM se a busca simples falhar
    try:
        llm = get_llm()
        amostra = df.head(3).to_dict(orient='records')
        
        prompt = f"""
        Analise estas colunas: {colunas}
        Amostra: {amostra}

        Tarefa: Qual coluna representa o NOME DA CIDADE ou MUNICÍPIO?
        
        Responda APENAS JSON: {{ "coluna_encontrada": "nome_exato_da_coluna" }}
        Se nada servir, {{ "coluna_encontrada": null }}
        """
        
        res = llm.call([{"role": "user", "content": prompt}])
        match = re.search(r'(\{.*\})', res, re.DOTALL)
        if match:
            dados = json.loads(match.group(1))
            return dados.get("coluna_encontrada")
            
    except Exception as e:
        print(f"Erro no fallback IA: {e}")
    
    return None

# --- 3. GEOCODIFICAÇÃO EM LOTES (IA) ---
def buscar_coordenadas_ia(lista_locais):
    """Geocodifica com estratégia de Rate Limit (Freio) para evitar erros da Groq."""
    llm = get_llm()
    dicionario_mestre = {}
    
    # 1. REDUÇÃO DRÁSTICA DO LOTE
    # De 20 para 5. Isso garante que cada requisição use poucos tokens.
    tamanho_lote = 5 
    lotes = [lista_locais[i:i + tamanho_lote] for i in range(0, len(lista_locais), tamanho_lote)]
    
    print(f"DEBUG: Processando {len(lista_locais)} locais em {len(lotes)} lotes...")

    for i, lote in enumerate(lotes):
        prompt = f"""
        Tarefa: Lat/Lon decimal para: {lote}.
        JSON Obrigatório: {{ "Nome do Local": {{ "lat": -10.0, "lon": -50.0 }} }}
        Use null se não souber.
        """
        
        # Lógica de RETRY (Tentativas)
        tentativas = 0
        max_tentativas = 3
        sucesso_lote = False
        
        while tentativas < max_tentativas and not sucesso_lote:
            try:
                res = llm.call([{"role": "user", "content": prompt}])
                
                # Extração do JSON
                match = re.search(r'(\{.*\})', res, re.DOTALL)
                if match:
                    dados_lote = json.loads(match.group(1))
                    dicionario_mestre.update(dados_lote)
                
                sucesso_lote = True
                print(f"✅ Lote {i+1}/{len(lotes)} processado.")
                
                # 2. FREIO DE MÃO (Sleep maior)
                # Espera 3 segundos para garantir que o TPM baixe
                time.sleep(3) 

            except Exception as e:
                erro_str = str(e).lower()
                if "rate limit" in erro_str or "429" in erro_str:
                    tempo_espera = 15 # Espera 15 segundos se bater no teto
                    print(f"⚠️ Rate Limit atingido no lote {i+1}. Esfriando por {tempo_espera}s... (Tentativa {tentativas+1})")
                    time.sleep(tempo_espera)
                    tentativas += 1
                else:
                    print(f"❌ Erro fatal no lote {i+1}: {e}")
                    break # Se não for rate limit, aborta o lote
            
    return dicionario_mestre