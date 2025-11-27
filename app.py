import streamlit as st
import pandas as pd
import altair as alt
import tempfile
import os
import sys
import re
import time
import io
import contextlib

# ===============================================
# Configuração da Página
# ===============================================
st.set_page_config(page_title="StoryVis - Analytics & Logs", layout="wide", page_icon="📊")

# --- Importações Dinâmicas ---
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
    # Função dummy para não quebrar o código se o logger falhar
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

# Container para restringir largura e manter estilo
c = st.container()
with c:
    st.markdown("### 📈 Demonstração")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Mês', sort=None),
        y='Vendas',
        color='Produto',
        tooltip=['Mês', 'Produto', 'Vendas']
    ).interactive()

    st.altair_chart(chart, width="stretch")
"""
    narrativa_fake = """
### 🚀 Demonstração Automática
Estes são dados de exemplo. Para começar a usar seus dados, vá na aba **Dados** e insira seu nome.
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

# ===============================================
# Interface Principal
# ===============================================
st.title("📊 StoryVis: Analytics com IA")

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
                
                # Limpa estado anterior
                st.session_state["codigo_final"] = ""
                st.session_state["narrativa_final"] = ""
                st.session_state["editor_codigo_area"] = ""
                
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

    df_editado = st.data_editor(st.session_state["df_final"], width="stretch", num_rows="dynamic")
    st.session_state["df_final"] = df_editado

# -------------------------------------------------------
# ABA 2: DASHBOARD + MONITORAMENTO
# -------------------------------------------------------
with tab_dash:
    st.subheader("Painel Visual")
    
    nome_atual = st.session_state.get("nome_participante", "Anônimo").strip()
    if not nome_atual: nome_atual = "Anônimo"

    # ===================================================
    # ÁREA 1: CRIAÇÃO INICIAL
    # ===================================================
    instrucao = st.text_input("🎯 Criar Dashboard Inicial:", placeholder="Ex: Dashboard completo de Vendas com 3 gráficos...")
    if nome_atual != "Anônimo" and nome_atual != "":
        gerar = st.button("🚀 Criar do Zero", type="primary", width="stretch")
    else:
        gerar = st.button("🚀 Criar do Zero", type="primary", width="stretch", disabled=True)
        st.caption("Preencha seu nome na Aba 1.")

    if gerar:
        # Iniciando cronômetros e buffers
        start_time = time.time()
        log_buffer = io.StringIO()
        
        with st.status("🧠 IA trabalhando...", expanded=True) as status:
            try:
                # 1. Estatísticas Pré-Execução
                df_atual = st.session_state["df_final"]
                rows, cols = df_atual.shape
                origem_dados = "Demo" if st.session_state.get("modo_demo") else "Upload"
                
                temp_path = salvar_temp_csv(df_atual)
                
                buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                user_req = f"Usuário: {nome_atual}. Pedido: {instrucao}"
                inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                
                # Estimativa de Tokens Input
                est_tokens_in = len(str(inputs)) / 4
                
                # 2. Execução com Captura de Terminal
                with contextlib.redirect_stdout(log_buffer):
                    result = StoryVisCrew().crew().kickoff(inputs=inputs)
                
                raw = result.raw
                
                # 3. Pós-Processamento
                narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                codigo_limpo = limpar_codigo_ia(codigo_sujo)

                st.session_state["codigo_final"] = codigo_limpo
                st.session_state["narrativa_final"] = narrativa
                st.session_state["editor_codigo_area"] = codigo_limpo 
                st.session_state["modo_demo"] = False
                
                # 4. Finalização Estatística
                end_time = time.time()
                tempo_total = end_time - start_time
                terminal_output = log_buffer.getvalue()
                est_tokens_out = len(raw) / 4
                
                status.update(label=f"Concluído em {tempo_total:.2f}s!", state="complete", expanded=False)

                # 5. Logging Avançado
                if LOGGING_ATIVO:
                    salvar_log_pinecone(
                        usuario=nome_atual,
                        input_usuario=instrucao,
                        output_ia=codigo_limpo,
                        status="Sucesso",
                        execution_time=tempo_total,
                        terminal_log=terminal_output,
                        dataset_rows=rows,
                        dataset_cols=cols,
                        data_source=origem_dados,
                        action_type="CREATE",
                        est_input_tokens=est_tokens_in,
                        est_output_tokens=est_tokens_out
                    )

            except Exception as e:
                # Tratamento de erro com Log
                end_time = time.time()
                tempo_total = end_time - start_time
                terminal_output = log_buffer.getvalue()
                
                st.error(f"Erro na geração: {e}")
                if LOGGING_ATIVO:
                    salvar_log_pinecone(
                        usuario=nome_atual,
                        input_usuario=instrucao,
                        output_ia=str(e),
                        status="Erro",
                        execution_time=tempo_total,
                        terminal_log=terminal_output
                    )

    st.divider()

    # ===================================================
    # ÁREA 2: VISUALIZAÇÃO
    # ===================================================
    container_grafico = st.container(border=True)
    with container_grafico:
        st.markdown("#### 📊 Resultado")
        if st.session_state["codigo_final"]:
            try:
                local_ctx = {"pd": pd, "st": st, "alt": alt, "df": st.session_state["df_final"]}
                exec(st.session_state["codigo_final"], globals(), local_ctx)
            except Exception as e:
                st.warning("⚠️ O código gerado contém erros ou os dados mudaram.")
                with st.expander("Ver erro técnico"): st.write(e)
        else:
            st.info("O gráfico aparecerá aqui.")

    # ===================================================
    # ÁREA 3: EVOLUÇÃO INFINITA
    # ===================================================
    if st.session_state["codigo_final"]:
        st.markdown("### ✨ Evoluir Dashboard")
        
        c_add1, c_add2 = st.columns([4, 1], gap="small")
        with c_add1:
            instrucao_add = st.text_input("O que adicionar agora?", placeholder="Ex: Adicione um gráfico de pizza...", key="input_evolucao")
        with c_add2:
            st.write("")
            st.write("")
            btn_adicionar = st.button("➕ Inserir Gráfico", width="stretch")

        if btn_adicionar and instrucao_add:
            # Cronômetro Update
            start_time = time.time()
            log_buffer = io.StringIO()
            
            with st.status("🔧 Adicionando novo visual...", expanded=True) as status:
                try:
                    df_atual = st.session_state["df_final"]
                    rows, cols = df_atual.shape
                    
                    inputs_update = {
                        'current_code': st.session_state["codigo_final"], 
                        'user_request': instrucao_add
                    }
                    est_tokens_in = len(str(inputs_update)) / 4
                    
                    with contextlib.redirect_stdout(log_buffer):
                        result = StoryVisCrew().crew_update().kickoff(inputs=inputs_update)
                    
                    raw = result.raw
                    codigo_novo_limpo = limpar_codigo_ia(raw) # Update geralmente não tem narrativa separada
                    
                    st.session_state["codigo_final"] = codigo_novo_limpo
                    st.session_state["editor_codigo_area"] = codigo_novo_limpo
                    
                    end_time = time.time()
                    tempo_total = end_time - start_time
                    terminal_output = log_buffer.getvalue()
                    est_tokens_out = len(raw) / 4
                    
                    status.update(label="Adicionado!", state="complete", expanded=False)
                    
                    if LOGGING_ATIVO:
                        salvar_log_pinecone(
                            usuario=nome_atual,
                            input_usuario=f"[ADD] {instrucao_add}",
                            output_ia=codigo_novo_limpo,
                            status="Sucesso",
                            execution_time=tempo_total,
                            terminal_log=terminal_output,
                            dataset_rows=rows,
                            dataset_cols=cols,
                            data_source="Existing",
                            action_type="APPEND",
                            est_input_tokens=est_tokens_in,
                            est_output_tokens=est_tokens_out
                        )
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao adicionar: {e}")
                    # Log de erro simplificado aqui
                    if LOGGING_ATIVO: salvar_log_pinecone(nome_atual, f"[ADD] {instrucao_add}", str(e), "Erro")

    # ===================================================
    # ÁREA 4: CÓDIGO FONTE
    # ===================================================
    st.markdown("---")
    with st.expander("🛠️ Ver/Editar Código Fonte (Avançado)", expanded=False):
        codigo_editado = st.text_area(
            "Python Script",
            value=st.session_state.get("editor_codigo_area", st.session_state["codigo_final"]),
            height=400,
            key="editor_codigo_area_widget"
        )
        if st.button("💾 Aplicar Alterações Manuais", width="stretch"):
            st.session_state["codigo_final"] = codigo_editado
            st.rerun()

# -------------------------------------------------------
# ABA 3: INSIGHTS
# -------------------------------------------------------
with tab_insights:
    st.subheader("📝 Narrativa Técnica")
    if st.session_state["narrativa_final"]:
        with st.container(border=True):
            st.markdown(st.session_state["narrativa_final"])
    else:
        st.info("O relatório da Gramática dos Gráficos aparecerá aqui.")