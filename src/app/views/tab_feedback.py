import streamlit as st
import time
from src.app.services.logger import salvar_sessao_completa

def render_tab_feedback(logging_ativo=True):
    st.subheader("🗣️ Pesquisa de Satisfação")
    
    nome_feedback = st.session_state.get("nome_participante", "").strip()
    if not nome_feedback:
        st.warning("⚠️ Preencha seu **Nome** na aba 'Dados' para liberar o envio.")
    else:
        st.success(f"Participante: **{nome_feedback}**")

    with st.form("form_feedback"):
        st.markdown("### 1. Perfil")
        c1, c2 = st.columns(2)
        with c1:
            sexo = st.selectbox("Sexo:", ["Masculino", "Feminino", "Outro"], index=None)
            idade_faixa = st.selectbox("Faixa Etária:", ["18-24", "25-34", "35-44", "45-54", "55+"], index=None)
        with c2:
            escolaridade = st.selectbox("Escolaridade:", ["Ensino Médio", "Graduação", "Pós-Graduação"], index=None)
            area_atuacao = st.selectbox("Área:", ["Exatas/Tech", "Humanas", "Saúde", "Outra"], index=None)

        st.divider()
        st.markdown("### 2. Perfil Técnico")
        freq_ai = st.select_slider("Uso de IA:", options=["Nunca", "Raro", "Mensal", "Semanal", "Diário"])
        
        ct1, ct2 = st.columns(2)
        with ct1: nivel_dados = st.selectbox("Nível Dados:", ["Iniciante", "Básico", "Intermediário", "Avançado"], index=None)
        with ct2: nivel_viz = st.selectbox("Experiência Gráficos:", ["Nenhuma", "Básico", "Intermediário", "Avançado"], index=None)
        
        conhece_prog = st.radio("Sabe programar?", ["Não", "Básico", "Sim"], horizontal=True)

        st.divider()
        st.markdown("### 3. Satisfação com as visualizações geradas pela IA")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            c1_resp = st.radio("Satisfação com os gráficos gerados:", ["OK", "Confuso", "N/A"], index=2)
            c2_resp = st.radio("Satisfação com Dashboard como um todo:", ["OK", "Erro", "N/A"], index=2)
            c3_resp = st.radio("Satisfação com a geração de Mapa(s):", ["OK", "Erro", "N/A"], index=2)
        with col_t2:
            c4_resp = st.radio("Satisfação com a Evolução dos Gráficos:", ["OK", "Erro", "N/A"], index=2)
            c5_resp = st.radio("Satisfação com o Editor Código:", ["OK", "Erro", "N/A"], index=2)
            nivel_complexidade = st.radio("Nível de Complexidade do Projeto:", ["Fácil", "Médio", "Difícil"], index=None)

        st.write("")
        st.write("Nota Final:")
        feedback_stars = st.feedback("stars")
        comentario = st.text_area("Comentários:")
        
        enviou = st.form_submit_button("✅ Enviar Pesquisa Completa", type="primary", disabled=(not nome_feedback))
        
        if enviou:
            # Adicionei 'nivel_complexidade' na validação para ser obrigatório
            if not all([sexo, idade_faixa, escolaridade, area_atuacao, nivel_dados, nivel_viz, nivel_complexidade]):
                st.error("⚠️ Preencha todos os campos de Perfil e Complexidade.")
            elif feedback_stars is None:
                st.error("⚠️ Dê uma nota (estrelas).")
            else:
                if logging_ativo:
                    with st.spinner("Consolidando dados da sessão..."):
                        
                        pacote_feedback = {
                            "estrelas": feedback_stars + 1,
                            "comentario": comentario,
                            "sexo": sexo, "faixa_etaria": idade_faixa,
                            "escolaridade": escolaridade, "area": area_atuacao,
                            "tec_freq_ai": freq_ai, "tec_nivel_dados": nivel_dados,
                            "tec_nivel_viz": nivel_viz, "tec_prog": conhece_prog,
                            "checklist": {
                                "C1_Bloqueio": c1_resp, "C2_Demo": c2_resp,
                                "C3_Geo": c3_resp, "C4_Evolucao": c4_resp, 
                                "C5_Codigo": c5_resp,
                                "C6_Complexidade": nivel_complexidade # <--- Enviando o novo dado
                            }
                        }
                        
                        logs_historico = st.session_state["buffer_logs_tecnicos"]
                        
                        sucesso = salvar_sessao_completa(
                            session_id=st.session_state["session_id"],
                            usuario=nome_feedback,
                            feedback_data=pacote_feedback,
                            logs_buffer=logs_historico
                        )
                        
                        if sucesso:
                            st.session_state["buffer_logs_tecnicos"] = [] 
                            st.balloons()
                            st.success("Pesquisa enviada! Registro único criado.")
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error("Erro no Pinecone.")