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

# --- Importações ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 1. CrewAI
try:
    from src.app.crew import StoryVisCrew
except ImportError:
    st.error("Erro crítico: Não foi possível importar 'src.app.crew'.")
    st.stop()

# 2. Logger (Pinecone) - Rodando silenciosamente
try:
    from src.app.services.logger import salvar_log_pinecone
    LOGGING_ATIVO = True
except ImportError:
    LOGGING_ATIVO = False
    def salvar_log_pinecone(*args, **kwargs): pass

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

def carregar_demo_inicial():
    """Modo Demonstração."""
    df_fake = pd.DataFrame({
        "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "Produto": ["Smartphone", "Smartphone", "Laptop", "Laptop", "Tablet", "Tablet"],
        "Vendas": [1200, 1500, 3000, 3200, 800, 950],
        "Meta": [1000, 1000, 2500, 2500, 1000, 1000]
    })
    codigo_fake = """
import streamlit as st
import altair as alt
import pandas as pd

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Mês', sort=None),
    y='Vendas',
    color='Produto',
    tooltip=['Mês', 'Produto', 'Vendas']
).interactive()

st.altair_chart(chart, use_container_width=True)
"""
    narrativa_fake = """
### 🚀 Demonstração Automática
Estes são dados de exemplo. Para começar, vá na aba **Dados** e insira seu nome.
"""
    return df_fake, codigo_fake, narrativa_fake

# ===============================================
# Inicialização de Estado
# ===============================================
if "df_final" not in st.session_state:
    df_demo, cod_demo, narr_demo = carregar_demo_inicial()
    st.session_state["df_final"] = df_demo
    st.session_state["codigo_final"] = cod_demo
    st.session_state["narrativa_final"] = narr_demo
    st.session_state["editor_codigo_area"] = cod_demo
    st.session_state["modo_demo"] = True
    st.session_state["nome_participante"] = "" # Começa vazio para forçar o input

# ===============================================
# Interface Principal
# ===============================================
st.title("📊 StoryVis: Dashboard com IA")

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
    
    nome_input = st.text_input("👤 Nome Completo (Obrigatório)", placeholder="Digite seu nome aqui...")
    # Atualiza o estado sempre que digitar
    st.session_state["nome_participante"] = nome_input
    uploaded_file = st.file_uploader("📂 Carregar Arquivo Próprio", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        if "arquivo_cache" not in st.session_state or st.session_state["arquivo_cache"] != uploaded_file.name:
            df_loaded = carregar_dados(uploaded_file)
            if df_loaded is not None:
                st.session_state["df_original"] = df_loaded
                st.session_state["df_final"] = df_loaded.copy()
                st.session_state["arquivo_cache"] = uploaded_file.name
                st.session_state["modo_demo"] = False
                st.toast("Arquivo carregado!", icon="✅")

    st.divider()

    col_tit, col_btn = st.columns([3, 1])
    with col_tit:
        origem = "Demo" if st.session_state.get("modo_demo") else "Seu Arquivo"
        st.markdown(f"**Tabela de Dados ({origem})**")
    with col_btn:
        if st.button("🔄 Restaurar Demo"):
            df_demo, cod_demo, narr_demo = carregar_demo_inicial()
            st.session_state["df_final"] = df_demo
            st.session_state["codigo_final"] = cod_demo
            st.session_state["narrativa_final"] = narr_demo
            st.session_state["editor_codigo_area"] = cod_demo
            st.session_state["modo_demo"] = True
            st.rerun()

    df_editado = st.data_editor(st.session_state["df_final"], use_container_width=True, num_rows="dynamic")
    st.session_state["df_final"] = df_editado

# -------------------------------------------------------
# ABA 2: DASHBOARD + LOGGING (Com Trava de Nome)
# -------------------------------------------------------
with tab_dash:
    st.subheader("Painel Visual & Editor")

    instrucao = st.text_input("O que deseja visualizar?", placeholder="Ex: Gráfico de Vendas por Categoria...")
    
    # --- TRAVA DE SEGURANÇA DO NOME ---
    nome_atual = st.session_state.get("nome_participante", "").strip()
    
    if nome_atual:
        # Se tem nome, botão habilitado
        gerar = st.button("🚀 Gerar Nova Análise com IA", type="primary", use_container_width=True)
    else:
        # Se não tem nome, aviso e botão desabilitado
        st.warning("⚠️ **Atenção:** Para gerar o dashboard, volte na aba 'Dados' e preencha seu **Nome**.")
        gerar = st.button("🚀 Gerar Nova Análise com IA", type="primary", use_container_width=True, disabled=True)

    if gerar:
        with st.status("🧠 IA trabalhando...", expanded=True) as status:
            try:
                df_atual = st.session_state["df_final"]
                temp_path = salvar_temp_csv(df_atual)
                
                buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                
                # Usa o nome validado
                user_req = f"Usuário: {nome_atual}. Pedido: {instrucao}"
                inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                
                # --- CHAMA A CREW ---
                result = StoryVisCrew().crew().kickoff(inputs=inputs)
                raw = result.raw
                
                narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                codigo_limpo = limpar_codigo_ia(codigo_sujo)

                st.session_state["codigo_final"] = codigo_limpo
                st.session_state["narrativa_final"] = narrativa
                st.session_state["editor_codigo_area"] = codigo_limpo 
                st.session_state["modo_demo"] = False
                
                status.update(label="Concluído!", state="complete", expanded=False)

                # --- 🌲 LOGGING SILENCIOSO NO PINECONE ---
                if LOGGING_ATIVO:
                    salvar_log_pinecone(
                        usuario=nome_atual,
                        input_usuario=instrucao,
                        output_ia=codigo_limpo,
                        status="Sucesso"
                    )
                # -----------------------------------------

            except Exception as e:
                st.error(f"Erro na geração: {e}")
                if LOGGING_ATIVO:
                    salvar_log_pinecone(
                        usuario=nome_atual,
                        input_usuario=instrucao,
                        output_ia=str(e),
                        status="Erro"
                    )

    st.divider()

    col_grafico, col_editor = st.columns([2, 1], gap="medium")

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

    with col_editor:
        st.markdown("#### 🛠️ Código Fonte")
        codigo_editado = st.text_area(
            "Python Script",
            value=st.session_state.get("editor_codigo_area", st.session_state["codigo_final"]),
            height=450,
            key="editor_codigo_area_widget"
        )
        if st.button("💾 Aplicar Alterações", use_container_width=True):
            st.session_state["codigo_final"] = codigo_editado
            st.rerun()

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