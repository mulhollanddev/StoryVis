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

# 2. Logger (Pinecone)
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

        # Container para restringir largura
        c = st.container()
        with c:
            st.markdown("### Gráfico Demonstração")
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
    st.session_state["nome_participante"] = "" 
    st.session_state["input_add_chart"] = "" # Controle do input de adicionar

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
    
    col_nome, col_upload = st.columns([1, 2], gap="medium")
    with col_nome:
        nome_input = st.text_input("👤 Nome Completo (Obrigatório)", placeholder="Digite seu nome aqui...")
        st.session_state["nome_participante"] = nome_input
        
    with col_upload:
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
# ABA 2: DASHBOARD + LOGGING
# -------------------------------------------------------
with tab_dash:
    st.subheader("Painel Visual")
    
    # Validação do Nome no topo
    nome_atual = st.session_state.get("nome_participante", "Anônimo").strip()
    if not nome_atual: nome_atual = "Anônimo"

    # ===================================================
    # ÁREA 1: CRIAÇÃO INICIAL (GERAR DO ZERO)
    # ===================================================
    
    instrucao = st.text_input("🎯 Criar Dashboard Inicial:", placeholder="Ex: Dashboard completo de Vendas com 3 gráficos...")
    
    if nome_atual != "Anônimo" and nome_atual != "":
        gerar = st.button("🚀 Gerar dashboard", type="primary", use_container_width=True, help="Isso apaga o dashboard atual e cria um novo.")
    else:
        gerar = st.button("🚀 Gerar dashboard", type="primary", use_container_width=True, disabled=True)
        st.caption("Preencha seu nome na Aba 1.")

    # Lógica de Geração (Mantida)
    if gerar:
        with st.status("🧠 Construindo Dashboard...", expanded=True) as status:
            try:
                df_atual = st.session_state["df_final"]
                temp_path = salvar_temp_csv(df_atual)
                
                buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                user_req = f"Usuário: {nome_atual}. Pedido: {instrucao}"
                inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                
                result = StoryVisCrew().crew().kickoff(inputs=inputs)
                raw = result.raw
                
                narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                codigo_limpo = limpar_codigo_ia(codigo_sujo)

                st.session_state["codigo_final"] = codigo_limpo
                st.session_state["narrativa_final"] = narrativa
                st.session_state["editor_codigo_area"] = codigo_limpo 
                st.session_state["modo_demo"] = False
                
                status.update(label="Dashboard Criado!", state="complete", expanded=False)

                if LOGGING_ATIVO:
                    salvar_log_pinecone(nome_atual, instrucao, codigo_limpo, "Sucesso")
            except Exception as e:
                st.error(f"Erro: {e}")
                if LOGGING_ATIVO: salvar_log_pinecone(nome_atual, instrucao, str(e), "Erro")

    st.divider()

    # ===================================================
    # ÁREA 2: VISUALIZAÇÃO E EVOLUÇÃO (AQUI ESTÁ A MUDANÇA UX)
    # ===================================================
    
    # Container do Gráfico
    container_grafico = st.container(border=True)
    with container_grafico:
        st.markdown("#### 📊 Resultado")
        if st.session_state["codigo_final"]:
            try:
                local_ctx = {"pd": pd, "st": st, "alt": alt, "df": st.session_state["df_final"]}
                exec(st.session_state["codigo_final"], globals(), local_ctx)
            except Exception as e:
                st.warning("Erro na renderização.")
                with st.expander("Detalhes"): st.write(e)
        else:
            st.info("O gráfico aparecerá aqui.")

    # ===================================================
    # ÁREA 3: EVOLUÇÃO INFINITA (ABAIXO DO GRÁFICO)
    # ===================================================
    if st.session_state["codigo_final"]:
        st.markdown("### ✨ Evoluir Dashboard")
        st.caption("Adicione mais gráficos ao painel acima sem perder o que já foi feito.")
        
        c_add1, c_add2 = st.columns([4, 1], gap="small")
        with c_add1:
            # Input com Key para podermos limpar depois se quisermos, mas manter o histórico é bom
            instrucao_add = st.text_input("O que você quer adicionar agora?", placeholder="Ex: Adicione um gráfico de pizza de Lucro...", key="input_evolucao")
        with c_add2:
            st.write("")
            st.write("")
            btn_adicionar = st.button("➕ Inserir Gráfico", use_container_width=True)

        if btn_adicionar and instrucao_add:
            with st.status("🔧 Adicionando novo visual...", expanded=True) as status:
                try:
                    inputs_update = {
                        'current_code': st.session_state["codigo_final"], 
                        'user_request': instrucao_add
                    }
                    
                    result = StoryVisCrew().crew_update().kickoff(inputs=inputs_update)
                    
                    codigo_novo_bruto = result.raw
                    codigo_novo_limpo = limpar_codigo_ia(codigo_novo_bruto)
                    
                    # Atualiza e mantém o ciclo
                    st.session_state["codigo_final"] = codigo_novo_limpo
                    st.session_state["editor_codigo_area"] = codigo_novo_limpo
                    
                    status.update(label="Adicionado com Sucesso!", state="complete", expanded=False)
                    
                    if LOGGING_ATIVO:
                        salvar_log_pinecone(nome_atual, f"[ADD] {instrucao_add}", codigo_novo_limpo, "Sucesso")
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao adicionar: {e}")

    # ===================================================
    # ÁREA 4: CÓDIGO FONTE (ESCONDIDO)
    # ===================================================
    st.markdown("---")
    with st.expander("🛠️ Ver/Editar Código Fonte (Avançado)", expanded=False):
        codigo_editado = st.text_area(
            "Python Script",
            value=st.session_state.get("editor_codigo_area", st.session_state["codigo_final"]),
            height=400,
            key="editor_codigo_area_widget"
        )
        if st.button("💾 Aplicar Alterações Manuais", use_container_width=True):
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