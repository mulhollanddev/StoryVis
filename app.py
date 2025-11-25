import streamlit as st
import pandas as pd
import altair as alt
import tempfile
import os
import sys
import re

# ===============================================
# Configuração da Página
# ===============================================
st.set_page_config(page_title="StoryVis", layout="wide", page_icon="📊")

# --- Importação da Crew ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from src.app.crew import StoryVisCrew
except ImportError:
    st.error("Erro: Não foi possível importar 'src.app.crew'.")
    st.stop()

# ===============================================
# Funções Auxiliares
# ===============================================
@st.cache_data(ttl=3600, show_spinner=False)
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return None

def salvar_temp_csv(df):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8') as tmp:
        df.to_csv(tmp.name, index=False)
        return tmp.name

def limpar_codigo_ia(texto_bruto):
    """Limpa o código removendo textos extras do robô."""
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
    """
    Tenta separar texto e código mesmo que a IA esqueça o separador.
    """
    narrativa = ""
    codigo_sujo = ""

    # 1. Tenta pelo Separador Oficial
    if "|||SEP|||" in raw_text:
        parts = raw_text.split("|||SEP|||")
        narrativa = parts[0].strip()
        if len(parts) > 1:
            codigo_sujo = parts[1]
    
    # 2. Fallback: Procura por blocos de código markdown
    elif "```python" in raw_text:
        # Tudo antes da crase é narrativa
        parts = raw_text.split("```python")
        narrativa = parts[0].strip()
        codigo_sujo = "```python" + parts[1] # Recostura o código
        
    # 3. Fallback: Procura pelo import do streamlit
    elif "import streamlit" in raw_text:
        idx = raw_text.find("import streamlit")
        narrativa = raw_text[:idx].strip()
        codigo_sujo = raw_text[idx:]
        
    # 4. Se não achar código, assume que é tudo narrativa
    else:
        narrativa = raw_text
        codigo_sujo = ""

    return narrativa, codigo_sujo

# ===============================================
# Inicialização de Estado
# ===============================================
if "codigo_final" not in st.session_state:
    st.session_state["codigo_final"] = ""
if "narrativa_final" not in st.session_state:
    st.session_state["narrativa_final"] = ""

# ===============================================
# Interface Principal
# ===============================================
st.title("📊 StoryVis")

tab_dados, tab_dash, tab_insights = st.tabs([
    "✏️ Dados & Configuração", 
    "📈 Dashboard & Código", 
    "📝 Narrativa de Insights"
])

# -------------------------------------------------------
# ABA 1: DADOS
# -------------------------------------------------------
with tab_dados:
    st.subheader("Preparação dos Dados")
    col_nome, col_upload = st.columns([1, 2], gap="medium")
    
    with col_nome:
        nome = st.text_input("👤 Nome do Participante", placeholder="Ex: Ana Silva")
        if nome: st.session_state["nome_participante"] = nome
    
    with col_upload:
        uploaded_file = st.file_uploader("📂 Arquivo de Dados", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        if "arquivo_cache" not in st.session_state or st.session_state["arquivo_cache"] != uploaded_file.name:
            df_loaded = carregar_dados(uploaded_file)
            if df_loaded is not None:
                st.session_state["df_original"] = df_loaded
                st.session_state["df_final"] = df_loaded.copy()
                st.session_state["arquivo_cache"] = uploaded_file.name
                st.toast("Arquivo carregado!", icon="✅")

    st.divider()

    if "df_final" in st.session_state:
        st.markdown(f"**Tabela Editável** ({len(st.session_state['df_final'])} linhas)")
        df_editado = st.data_editor(st.session_state["df_final"], use_container_width=True, num_rows="dynamic")
        st.session_state["df_final"] = df_editado
        if st.button("↺ Resetar Dados"):
            st.session_state["df_final"] = st.session_state["df_original"].copy()
            st.rerun()
    else:
        st.info("Faça o upload de um arquivo para começar.")

# -------------------------------------------------------
# ABA 2: DASHBOARD + EDITOR
# -------------------------------------------------------
with tab_dash:
    st.subheader("Painel Visual & Editor")

    if "df_final" in st.session_state:
        # Prompt
        p_col, b_col = st.columns([4, 1])
        with p_col:
            instrucao = st.text_input("O que você quer visualizar?", placeholder="Ex: Gráfico de barras de Vendas por Mês...")
        with b_col:
            gerar = st.button("🚀 Gerar com IA", type="primary", use_container_width=True)

        # Lógica IA
        if gerar:
            with st.status("🧠 IA trabalhando...", expanded=True) as status:
                try:
                    df_atual = st.session_state["df_final"]
                    temp_path = salvar_temp_csv(df_atual)
                    
                    # Resumo
                    buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                    user_req = f"Usuário: {st.session_state.get('nome_participante', 'User')}. {instrucao}"
                    inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                    
                    # CrewAI
                    result = StoryVisCrew().crew().kickoff(inputs=inputs)
                    raw = result.raw
                    
                    # --- NOVA LÓGICA DE SEPARAÇÃO INTELIGENTE ---
                    narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                    
                    # Limpeza final do código
                    codigo_limpo = limpar_codigo_ia(codigo_sujo)

                    # Atualiza Estado
                    st.session_state["codigo_final"] = codigo_limpo
                    st.session_state["narrativa_final"] = narrativa
                    st.session_state["editor_codigo_area"] = codigo_limpo 
                    
                    status.update(label="Gráfico Gerado!", state="complete", expanded=False)
                    
                    # Debug Opcional: Se a narrativa vier vazia, avisa
                    if not narrativa:
                        st.toast("A IA gerou o gráfico mas não retornou texto.", icon="⚠️")
                        
                except Exception as e:
                    st.error(f"Erro na geração: {e}")

        st.divider()

        # Layout Dividido
        col_grafico, col_editor = st.columns([2, 1], gap="medium")

        # Esquerda: O Gráfico
        with col_grafico:
            st.markdown("#### 📊 Visualização")
            if st.session_state["codigo_final"]:
                try:
                    local_ctx = {"pd": pd, "st": st, "alt": alt, "df": st.session_state["df_final"]}
                    exec(st.session_state["codigo_final"], globals(), local_ctx)
                except Exception as e:
                    st.error("Erro no código Python:")
                    st.write(e)
            else:
                st.info("O gráfico aparecerá aqui.")

        # Direita: O Editor
        with col_editor:
            st.markdown("#### 🛠️ Código Fonte")
            codigo_editado = st.text_area(
                "Python Script",
                value=st.session_state["codigo_final"],
                height=450,
                key="editor_codigo_area"
            )
            
            if st.button("💾 Aplicar Alterações", use_container_width=True):
                st.session_state["codigo_final"] = codigo_editado
                st.rerun()

    else:
        st.warning("⚠️ Carregue os dados na Aba 1 primeiro.")

# -------------------------------------------------------
# ABA 3: INSIGHTS
# -------------------------------------------------------
with tab_insights:
    st.subheader("📝 Narrativa de Negócios")
    
    if st.session_state["narrativa_final"]:
        with st.container(border=True):
            st.markdown(st.session_state["narrativa_final"])
    else:
        # Mensagem mais amigável
        st.info("A explicação textual da IA aparecerá aqui após você gerar o dashboard.")
        
        # Mostra o que tem no RAW para debug se estiver vazio
        if "codigo_final" in st.session_state and st.session_state["codigo_final"]:
             st.caption("(Se você vê código mas não vê texto, a IA pode ter pulado a narrativa desta vez. Tente gerar novamente).")