import streamlit as st
import pandas as pd
import altair as alt
import time
import io
import contextlib
from src.app.crew import StoryVisCrew
from src.app.utils import salvar_temp_csv, limpar_codigo_ia, separar_narrativa_codigo, is_python_code

def render_tab_dashboard(logging_ativo=True):
    st.subheader("Painel Visual")
    
    nome_atual = st.session_state.get("nome_participante", "Anônimo").strip()
    if not nome_atual: nome_atual = "Anônimo"

    instrucao = st.text_input("🎯 Criar Dashboard Inicial:", placeholder="Ex: Compare a potência e destaque a maior média...")
    
    desabilitado = (nome_atual == "Anônimo" or nome_atual == "")
    if desabilitado: 
        st.error("🚨 **Obrigatório:** Vá na aba 'Dados' e preencha seu Nome para liberar.")
    
    gerar = st.button("🚀 Gerar dashboard", type="primary", width="stretch", disabled=desabilitado)

    if gerar:
        st.session_state["interaction_step"] += 1
        
        start_time = time.time()
        log_buffer = io.StringIO()
        
        with st.status("🧠 Analisando requisição...", expanded=True) as status:
            try:
                precisa_calculo = False
                df_atual = st.session_state["df_final"]
                rows, cols = df_atual.shape
                origem_dados = "Demo" if st.session_state.get("modo_demo") else "Upload"
                
                temp_path = salvar_temp_csv(df_atual)
                st.session_state["temp_csv_path"] = temp_path 
                
                buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                user_req = f"Usuário: {nome_atual}. Pedido: {instrucao}"
                inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                
                est_tokens_in = len(str(inputs)) // 4
                
                with contextlib.redirect_stdout(log_buffer):
                    status.write("Gerando visualização padrão...")
                    result = StoryVisCrew().crew().kickoff(inputs=inputs)
                
                raw = result.raw
                narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                codigo_limpo = limpar_codigo_ia(codigo_sujo)

                if precisa_calculo:
                    try:
                        res_calc = StoryVisCrew().crew_calculation().kickoff(inputs=inputs)
                        st.session_state["codigo_calculo"] = limpar_codigo_ia(res_calc.raw) or res_calc.raw
                    except Exception: pass

                st.session_state["codigo_final"] = codigo_limpo
                st.session_state["narrativa_final"] = narrativa
                st.session_state["editor_codigo_area"] = codigo_limpo 
                st.session_state["modo_demo"] = False
                
                end_time = time.time()
                tempo_total = end_time - start_time
                terminal_output = log_buffer.getvalue()
                est_tokens_out = len(raw) // 4
                
                status.update(label=f"Concluído em {tempo_total:.2f}s!", state="complete", expanded=False)

                if logging_ativo:
                    log_item = {
                        "step": st.session_state["interaction_step"],
                        "action_type": "CREATE",
                        "input": instrucao,
                        "output_code": codigo_limpo,
                        "narrativa": narrativa,
                        "status": "Sucesso",
                        "execution_time": tempo_total,
                        "dataset_info": f"{rows}x{cols} ({origem_dados})",
                        "tokens_total": est_tokens_in + est_tokens_out
                    }
                    st.session_state["buffer_logs_tecnicos"].append(log_item)

            except Exception as e:
                end_time = time.time()
                st.error(f"Erro na geração: {e}")
                if logging_ativo:
                    log_erro = {
                        "step": st.session_state["interaction_step"],
                        "action_type": "ERROR",
                        "input": instrucao,
                        "error_msg": str(e),
                        "status": "Erro",
                        "execution_time": end_time - start_time
                    }
                    st.session_state["buffer_logs_tecnicos"].append(log_erro)

    st.divider()

    # --- Resultado Visual ---
    container_grafico = st.container(border=True)
    with container_grafico:
        st.markdown("#### 📊 Resultado")
        if st.session_state["codigo_final"]:
            try:
                local_ctx = {
                    "pd": pd, "st": st, "alt": alt, 
                    "df": st.session_state["df_final"],
                    "file_path": st.session_state.get("temp_csv_path", "")
                }
                exec(st.session_state["codigo_final"], globals(), local_ctx)
            except Exception as e:
                st.warning("⚠️ Erro ao renderizar gráfico.")
                with st.expander("Detalhes"): st.write(e)
        else:
            st.info("O gráfico aparecerá aqui.")

    # --- Scorecards ---
    if st.session_state.get("codigo_calculo"):
        st.markdown("---")
        with st.container(border=True):
            st.markdown("#### 🧮 Destaques")
            calc_content = st.session_state["codigo_calculo"]
            if is_python_code(calc_content):
                try:
                    local_ctx_calc = {"pd": pd, "st": st, "df": st.session_state["df_final"]}
                    exec(calc_content, globals(), local_ctx_calc)
                except Exception: st.code(calc_content)
            else:
                st.write(calc_content)

    # --- Evolução (Append) ---
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
            st.session_state["interaction_step"] += 1
            
            start_time = time.time()
            log_buffer = io.StringIO()
            
            with st.status("🔧 Adicionando novo visual...", expanded=True) as status:
                try:
                    df_atual = st.session_state["df_final"]
                    inputs_update = {'current_code': st.session_state["codigo_final"], 'user_request': instrucao_add}
                    
                    with contextlib.redirect_stdout(log_buffer):
                        result = StoryVisCrew().crew_update().kickoff(inputs=inputs_update)
                    
                    raw = result.raw
                    codigo_novo_limpo = limpar_codigo_ia(raw) 
                    st.session_state["codigo_final"] = codigo_novo_limpo
                    st.session_state["editor_codigo_area"] = codigo_novo_limpo
                    
                    tempo_total = time.time() - start_time
                    status.update(label="Adicionado!", state="complete", expanded=False)
                    
                    if logging_ativo:
                        log_item = {
                            "step": st.session_state["interaction_step"],
                            "action_type": "APPEND",
                            "input": f"[ADD] {instrucao_add}",
                            "output_code": codigo_novo_limpo,
                            "status": "Sucesso",
                            "execution_time": tempo_total
                        }
                        st.session_state["buffer_logs_tecnicos"].append(log_item)
                    
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
                    if logging_ativo:
                        st.session_state["buffer_logs_tecnicos"].append({
                            "step": st.session_state["interaction_step"],
                            "action_type": "APPEND_ERROR",
                            "error_msg": str(e)
                        })

    st.markdown("---")
    with st.expander("🛠️ Ver/Editar Código Fonte", expanded=False):
        codigo_editado = st.text_area("Python Script", value=st.session_state.get("editor_codigo_area", st.session_state["codigo_final"]), height=400)
        if st.button("💾 Aplicar Alterações"):
            st.session_state["codigo_final"] = codigo_editado
            st.rerun()