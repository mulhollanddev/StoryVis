import streamlit as st
import pandas as pd
import tempfile
import re

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