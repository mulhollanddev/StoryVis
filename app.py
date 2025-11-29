import streamlit as st
import pandas as pd
import altair as alt
import os
import sys
import time
import io
import contextlib

# Configuração da Página
st.set_page_config(page_title="StoryVis", layout="wide", page_icon="📊")

# --- Importações Locais ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports de Lógica
try:
    from src.app.crew import StoryVisCrew
    from src.app.services.logger import salvar_log_pinecone, salvar_feedback_pinecone
    from src.app.utils import (
        carregar_dados, salvar_temp_csv, limpar_codigo_ia, 
        separar_narrativa_codigo, inicializar_session_state
    )
    from src.app.demo import carregar_demo_inicial
    
    LOGGING_ATIVO = True
except ImportError as e:
    st.error(f"Erro crítico de importação: {e}")
    st.stop()

# Inicialização de Estado (Refatorado para utils)
inicializar_session_state(carregar_demo_inicial)

# ===============================================
# Interface Principal
# ===============================================
st.title("📊 StoryVis: Analytics com IA")

tab_dados, tab_dash, tab_insights, tab_feedback = st.tabs([
    "✏️ Dados & Configuração", 
    "📈 Dashboard", 
    "📝 Sobre os gráficos",
    "🗣️ Feedback"
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
                
                # Reset limpo
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
        if st.button("🔄 Restaurar Demo", width="stretch"):
            df_d, cod_d, narr_d = carregar_demo_inicial()
            st.session_state["df_final"] = df_d
            st.session_state["codigo_final"] = cod_d
            st.session_state["narrativa_final"] = narr_d
            st.session_state["editor_codigo_area"] = cod_d
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

    # --- Área de Criação ---
    
    instrucao = st.text_input("🎯 Criar Dashboard Inicial:", placeholder="Ex: Dashboard completo de Vendas...")
    estado_btn = "primary" if (nome_atual != "Anônimo" and nome_atual != "") else "secondary"
    desabilitado = (nome_atual == "Anônimo" or nome_atual == "")
    if desabilitado: st.error("🚨 **Obrigatório:** Vá na aba 'Dados' e preencha seu Nome para liberar.")
    gerar = st.button("🚀 Gerar dashboard", type="primary", width="stretch", disabled=desabilitado)

    if gerar:
        start_time = time.time()
        log_buffer = io.StringIO()
        
        with st.status("🧠 IA trabalhando...", expanded=True) as status:
            try:
                # Estatísticas
                df_atual = st.session_state["df_final"]
                rows, cols = df_atual.shape
                origem_dados = "Demo" if st.session_state.get("modo_demo") else "Upload"
                
                temp_path = salvar_temp_csv(df_atual)
                buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                user_req = f"Usuário: {nome_atual}. Pedido: {instrucao}"
                inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                
                est_tokens_in = len(str(inputs)) / 4
                
                # Execução
                with contextlib.redirect_stdout(log_buffer):
                    result = StoryVisCrew().crew().kickoff(inputs=inputs)
                
                raw = result.raw
                narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                codigo_limpo = limpar_codigo_ia(codigo_sujo)

                st.session_state["codigo_final"] = codigo_limpo
                st.session_state["narrativa_final"] = narrativa
                st.session_state["editor_codigo_area"] = codigo_limpo 
                st.session_state["modo_demo"] = False
                
                # Finalização
                end_time = time.time()
                tempo_total = end_time - start_time
                terminal_output = log_buffer.getvalue()
                est_tokens_out = len(raw) / 4
                
                status.update(label=f"Concluído em {tempo_total:.2f}s!", state="complete", expanded=False)

                if LOGGING_ATIVO:
                    salvar_log_pinecone(
                        usuario=nome_atual, input_usuario=instrucao, output_ia=codigo_limpo,
                        output_narrativa=narrativa, status="Sucesso", execution_time=tempo_total,
                        terminal_log=terminal_output, dataset_rows=rows, dataset_cols=cols,
                        data_source=origem_dados, action_type="CREATE",
                        est_input_tokens=est_tokens_in, est_output_tokens=est_tokens_out
                    )

            except Exception as e:
                end_time = time.time()
                tempo_total = end_time - start_time
                terminal_output = log_buffer.getvalue()
                st.error(f"Erro na geração: {e}")
                if LOGGING_ATIVO:
                    salvar_log_pinecone(
                        usuario=nome_atual, input_usuario=instrucao, output_ia=str(e),
                        output_narrativa="Erro", status="Erro", execution_time=tempo_total,
                        terminal_log=terminal_output
                    )

    st.divider()

    # --- Área Visualização ---
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

    # --- Área Evolução ---
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
            start_time = time.time()
            log_buffer = io.StringIO()
            with st.status("🔧 Adicionando novo visual...", expanded=True) as status:
                try:
                    df_atual = st.session_state["df_final"]
                    rows, cols = df_atual.shape
                    
                    inputs_update = {'current_code': st.session_state["codigo_final"], 'user_request': instrucao_add}
                    est_tokens_in = len(str(inputs_update)) / 4
                    
                    with contextlib.redirect_stdout(log_buffer):
                        result = StoryVisCrew().crew_update().kickoff(inputs=inputs_update)
                    
                    raw = result.raw
                    codigo_novo_limpo = limpar_codigo_ia(raw) 
                    
                    st.session_state["codigo_final"] = codigo_novo_limpo
                    st.session_state["editor_codigo_area"] = codigo_novo_limpo
                    
                    end_time = time.time()
                    tempo_total = end_time - start_time
                    terminal_output = log_buffer.getvalue()
                    est_tokens_out = len(raw) / 4
                    
                    status.update(label="Adicionado!", state="complete", expanded=False)
                    
                    if LOGGING_ATIVO:
                        salvar_log_pinecone(
                            usuario=nome_atual, input_usuario=f"[ADD] {instrucao_add}",
                            output_ia=codigo_novo_limpo, output_narrativa="Update", status="Sucesso",
                            execution_time=tempo_total, terminal_log=terminal_output,
                            dataset_rows=rows, dataset_cols=cols, data_source="Existing",
                            action_type="APPEND", est_input_tokens=est_tokens_in, est_output_tokens=est_tokens_out
                        )
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
                    if LOGGING_ATIVO: salvar_log_pinecone(nome_atual, f"[ADD] {instrucao_add}", str(e), "Erro", status="Erro")

    # --- Área Código Fonte ---
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
    st.subheader("Narrativa Técnica")
    if st.session_state["narrativa_final"]:
        with st.container(border=True):
            st.markdown(st.session_state["narrativa_final"])
    else:
        st.info("O relatório da Gramática dos Gráficos aparecerá aqui.")

with tab_feedback:
    st.subheader(" Feedback")

    nome_feedback = st.session_state.get("nome_participante", "").strip()
    
    if not nome_feedback:
        st.warning("⚠️ **Atenção:** Você precisa preencher seu **Nome** na aba '✏️ Dados' para poder enviar feedback.")

    with st.form("form_feedback"):
        st.write("O que achou da análise?")
        
        # --- MUDANÇA AQUI: ESTRELAS NATIVAS ---
        # st.feedback retorna: 0, 1, 2, 3, 4 (ou None se não clicou)
        feedback_stars = st.feedback("stars")
        
        comentario = st.text_area(
            "Comentário (Opcional):", 
            placeholder="Ex: O gráfico ficou ótimo, mas a cor estava ruim..."
        )
        
        # Botão de envio
        enviou = st.form_submit_button(
            "Enviar Avaliação", 
            type="primary",
            disabled=(not nome_feedback) # True se vazio, False se tiver nome
        )
        
        if enviou:
            if LOGGING_ATIVO:
                # Lógica para converter 0-4 para 1-5
                # Se for None (usuário não clicou), assumimos 0 ou tratamos como erro
                nota_final = (feedback_stars + 1) if feedback_stars is not None else 0
                
                if nota_final > 0:
                    user_feedback = st.session_state.get("nome_participante", "Anônimo")
                    
                    salvou = salvar_feedback_pinecone(
                        usuario=user_feedback,
                        estrelas=nota_final, # Salva 1 a 5
                        comentario=comentario
                    )
                    
                    if salvou:
                        st.toast("Obrigado pelo feedback! 🌟", icon="✅")
                        time.sleep(2)
                        st.rerun() # Limpa o form
                else:
                    st.warning("Por favor, selecione as estrelas antes de enviar.")
            else:
                st.error("Erro: Logger desativado.")


st.divider()
st.caption("LABVIS - UFPA © 2025")