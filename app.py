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
st.set_page_config(page_title="StoryVis - Editor Vivo", layout="wide", page_icon="📊")

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
    """Limpa o código removendo textos extras e comandos obsoletos."""
    if not texto_bruto: return ""
    
    # 1. Extrai o conteúdo das crases
    padrao = r"```(?:python)?\s*(.*?)```"
    match = re.search(padrao, texto_bruto, re.DOTALL)
    if match: 
        codigo = match.group(1).strip()
    else:
        # Fallback se não tiver crases
        linhas = texto_bruto.split('\n')
        linhas_limpas = []
        for linha in linhas:
            l = linha.lower().strip()
            if l.startswith(("espero que", "hope this", "segue o", "aqui está", "qualquer dúvida")):
                break
            linhas_limpas.append(linha)
        codigo = "\n".join(linhas_limpas).strip()

    # 2. CORREÇÃO "NA MARRA" DO CACHE
    # Se o robô teimoso colocar @st.cache, a gente comenta a linha.
    # Isso impede o erro de depreciação sem quebrar a função abaixo dele.
    codigo = codigo.replace("@st.cache", "# @st.cache (Removido por segurança)")
    
    # Opcional: Remove também tentativas de st.experimental_memo que modelos velhos gostam
    codigo = codigo.replace("@st.experimental_memo", "# @st.experimental_memo")
    
    return codigo

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
st.title("📊 StoryVis: Editor & Dashboard Vivo")

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
# ABA 2: DASHBOARD + EDITOR (Onde estava o problema)
# -------------------------------------------------------
with tab_dash:
    st.subheader("Painel Visual & Editor")

    if "df_final" in st.session_state:
        # Prompt
        p_col, b_col = st.columns([4, 1])
        with p_col:
            instrucao = st.text_input("O que você quer visualizar?", placeholder="Ex: Gráfico de barras de Vendas por Mês...")
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
                    
                    # Parse e Limpeza
                    if "|||SEP|||" in raw:
                        parts = raw.split("|||SEP|||")
                        narrativa = parts[0].strip()
                        codigo_sujo = parts[1]
                    else:
                        narrativa = "Narrativa integrada."
                        codigo_sujo = raw[raw.find("import"):] if "import" in raw else ""

                    codigo_limpo = limpar_codigo_ia(codigo_sujo)

                    # --- CORREÇÃO CRÍTICA AQUI ---
                    # Atualizamos a variável mestre
                    st.session_state["codigo_final"] = codigo_limpo
                    st.session_state["narrativa_final"] = narrativa
                    
                    # FORÇAMOS a atualização do widget de texto (o editor da direita)
                    # Isso garante que o código NOVO apareça na caixa imediatamente
                    st.session_state["editor_codigo_area"] = codigo_limpo 
                    
                    status.update(label="Gráfico Gerado!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Erro na geração: {e}")

        st.divider()

        # Layout Dividido: Gráfico (Esq) | Editor (Dir)
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

        # Direita: O Editor de Código
        with col_editor:
            st.markdown("#### 🛠️ Código Fonte")
            st.caption("Edite o código e clique em Aplicar.")
            
            # O Widget Text Area
            # key="editor_codigo_area" liga este campo à variável que atualizamos lá em cima
            codigo_editado = st.text_area(
                "Python Script",
                value=st.session_state["codigo_final"], # Valor inicial (fallback)
                height=450,
                key="editor_codigo_area" # Chave fundamental para sincronia
            )
            
            if st.button("💾 Aplicar Alterações", use_container_width=True):
                # Se o usuário editou na mão, salvamos a edição na variável mestre
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
        st.info("A explicação textual da IA aparecerá aqui.")