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

# --- DADOS FAKE PARA DEMONSTRAÇÃO IMEDIATA ---
def carregar_demo_inicial():
    """Retorna um kit completo de demonstração para o usuário impaciente."""
    
    # 1. Dados Fictícios
    df_fake = pd.DataFrame({
        "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "Produto": ["Smartphone", "Smartphone", "Laptop", "Laptop", "Tablet", "Tablet"],
        "Vendas": [1200, 1500, 3000, 3200, 800, 950],
        "Meta": [1000, 1000, 2500, 2500, 1000, 1000]
    })

    # 2. Código Pré-pronto (Como se a IA tivesse gerado)
    codigo_fake = """
import streamlit as st
import altair as alt
import pandas as pd

# Gráfico de Vendas vs Meta
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Mês', sort=None),
    y='Vendas',
    color='Produto',
    tooltip=['Mês', 'Produto', 'Vendas', 'Meta']
).interactive()

line = alt.Chart(df).mark_line(color='red').encode(
    x=alt.X('Mês', sort=None),
    y='Meta'
)

st.altair_chart(chart + line, use_container_width=True)
"""

    # 3. Narrativa Pré-pronta
    narrativa_fake = """
### 🚀 Demonstração Automática

Estes são dados de exemplo para você ver o sistema funcionando.
Observe como as vendas de **Smartphones** e **Laptops** superaram a meta consistentemente, enquanto os **Tablets** ficaram um pouco abaixo em Maio.

**Experimente:** Vá na aba 'Dados', mude os valores da tabela e veja este gráfico atualizar!
"""
    return df_fake, codigo_fake, narrativa_fake

# ===============================================
# Inicialização de Estado (CARREGA O DEMO AQUI)
# ===============================================
if "df_final" not in st.session_state:
    # CARREGAMENTO INICIAL INTELIGENTE
    df_demo, cod_demo, narr_demo = carregar_demo_inicial()
    
    st.session_state["df_final"] = df_demo
    st.session_state["codigo_final"] = cod_demo
    st.session_state["narrativa_final"] = narr_demo
    st.session_state["editor_codigo_area"] = cod_demo # Popula o editor
    st.session_state["modo_demo"] = True # Flag para saber que é demo

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
    
    # Upload
    uploaded_file = st.file_uploader("📂 Carregar Arquivo Próprio (Substitui os dados atuais)", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        if "arquivo_cache" not in st.session_state or st.session_state["arquivo_cache"] != uploaded_file.name:
            df_loaded = carregar_dados(uploaded_file)
            if df_loaded is not None:
                st.session_state["df_original"] = df_loaded
                st.session_state["df_final"] = df_loaded.copy()
                st.session_state["arquivo_cache"] = uploaded_file.name
                st.session_state["modo_demo"] = False
                st.toast("Arquivo carregado! Vá para a aba Dashboard para gerar novos gráficos.", icon="✅")

    st.divider()

    # Cabeçalho da Tabela
    col_titulo, col_reset = st.columns([3, 1])
    with col_titulo:
        if st.session_state.get("modo_demo"):
            st.info("ℹ️ **Modo Demonstração:** Estes são dados fictícios. Você pode editá-los ou subir seu arquivo acima.")
        else:
            st.markdown(f"### 📋 Tabela de Dados")

    with col_reset:
        if st.button("🔄 Restaurar Demo", use_container_width=True):
            df_demo, cod_demo, narr_demo = carregar_demo_inicial()
            st.session_state["df_final"] = df_demo
            st.session_state["codigo_final"] = cod_demo
            st.session_state["narrativa_final"] = narr_demo
            st.session_state["editor_codigo_area"] = cod_demo
            st.session_state["modo_demo"] = True
            if "arquivo_cache" in st.session_state: del st.session_state["arquivo_cache"]
            st.rerun()

    # --- Tabela Editável ---
    df_editado = st.data_editor(
        st.session_state["df_final"], 
        use_container_width=True, 
        num_rows="dynamic",
        key="editor_principal"
    )
    st.session_state["df_final"] = df_editado


# -------------------------------------------------------
# ABA 2: DASHBOARD + EDITOR
# -------------------------------------------------------
with tab_dash:
    st.subheader("Painel Visual & Editor")

    instrucao = st.text_input("Gostaria de criar um gráfico diferente?", placeholder="Ex: Mostre a soma de vendas por produto...")
    gerar = st.button("🚀 Gerar Nova Análise com IA", type="primary", use_container_width=True)

    if gerar:
        with st.status("🧠 IA analisando seus dados...", expanded=True) as status:
            try:
                df_atual = st.session_state["df_final"]
                temp_path = salvar_temp_csv(df_atual)
                
                buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                user_req = f"O usuário deseja: {instrucao}"
                inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                
                result = StoryVisCrew().crew().kickoff(inputs=inputs)
                raw = result.raw
                
                narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                codigo_limpo = limpar_codigo_ia(codigo_sujo)

                st.session_state["codigo_final"] = codigo_limpo
                st.session_state["narrativa_final"] = narrativa
                st.session_state["editor_codigo_area"] = codigo_limpo 
                st.session_state["modo_demo"] = False # Saiu do modo demo pois gerou novo
                
                status.update(label="Gráfico Gerado!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Erro na geração: {e}")

    st.divider()

    col_grafico, col_editor = st.columns([2, 1], gap="medium")

    with col_grafico:
        st.markdown("#### 📊 Visualização")
        
        # Se tiver código (Demo ou Gerado), executa
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
        
        # O valor inicial vem do session_state (que pode ser o Demo ou o Gerado)
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