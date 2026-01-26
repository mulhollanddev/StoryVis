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
    Analisa as colunas para tentar identificar qual contém dados geográficos (Cidade, Estado, País).
    """
    if df is None or df.empty:
        return None
        
    # --- A CORREÇÃO ESTÁ AQUI ---
    # Convertemos o nome de todas as colunas para string antes de usar .lower()
    # Isso evita erro se o cabeçalho for um número (ex: 2024, 2025)
    colunas = [str(c) for c in df.columns] 
    colunas_lower = [c.lower() for c in colunas]
    
    # Palavras-chave para identificar local
    keywords_geo = ['cidade', 'city', 'municipio', 'município', 
                    'estado', 'state', 'uf', 'pais', 'country', 'local', 'location']
    
    # 1. Tenta match exato ou parcial
    for col_orig, col_low in zip(df.columns, colunas_lower):
        if any(k in col_low for k in keywords_geo):
            # Verifica se o conteúdo parece texto (não numérico)
            try:
                amostra = df[col_orig].dropna().iloc[0]
                if isinstance(amostra, str):
                    return col_orig
            except:
                continue
                
    return None


# --- 3. GEOCODIFICAÇÃO EM LOTES (IA) ---
def buscar_coordenadas_ia(lista_locais):
    """
    Geocodifica com estratégia de Rate Limit e traz chaves para Altair (geo_code).
    """
    llm = get_llm()
    dicionario_mestre = {}
    
    # Mantemos lote pequeno
    tamanho_lote = 5 
    lotes = [lista_locais[i:i + tamanho_lote] for i in range(0, len(lista_locais), tamanho_lote)]
    
    print(f"DEBUG: Processando {len(lista_locais)} locais...")

    for i, lote in enumerate(lotes):
        # --- PROMPT ATUALIZADO PARA ALTAIR ---
        # Pedimos geo_code (Sigla) além de Lat/Lon
        prompt = f"""
        Analise a lista: {lote}
        
        TAREFA: Retorne JSON com Lat/Lon e CÓDIGOS DE MAPA.
        
        REGRAS:
        1. 'geo_code': A Sigla do Estado/Província (ex: "SP", "PA", "NY"). 
           (ISSO É OBRIGATÓRIO PARA O MAPA COROPLÉTICO).
        2. 'country_iso': Código ISO Alpha-3 do País (ex: "BRA").
        3. 'lat'/'lon': Decimais.
        
        FORMATO JSON PURO:
        {{
           "Nome do Local": {{ 
               "lat": -1.45, 
               "lon": -48.50, 
               "geo_code": "PA",
               "country_iso": "BRA"
           }}
        }}
        """
        
        # --- Lógica de Retry e Sleep (Mantida igual à sua) ---
        tentativas = 0
        max_tentativas = 3
        sucesso_lote = False
        
        while tentativas < max_tentativas and not sucesso_lote:
            try:
                res = llm.call([{"role": "user", "content": prompt}])
                
                match = re.search(r'(\{.*\})', res, re.DOTALL)
                if match:
                    dicionario_mestre.update(json.loads(match.group(1)))
                
                sucesso_lote = True
                print(f"✅ Lote {i+1} OK.")
                time.sleep(3) # Freio

            except Exception as e:
                if "rate limit" in str(e).lower():
                    print(f"⚠️ Rate Limit. Esfriando 15s...")
                    time.sleep(15)
                    tentativas += 1
                else:
                    print(f"❌ Erro: {e}")
                    break 
            
    return dicionario_mestre

def is_python_code(text):
    """Verifica se o texto parece código Python ou texto natural."""
    keywords = ['import ', 'st.', 'pd.', 'print(', 'def ', '=', 'return']
    return any(k in text for k in keywords)