# src/app/app.py
# -----------------
# Aplicação Streamlit (Frontend) para o StoryVis

import streamlit as st
import altair as alt
import json
import re  
import pandas as pd
import os
import tempfile
import shutil
from io import StringIO
import time 

# Importações dos módulos do projeto (Refatoradas)
from src.app.crew import StoryVisCrew
from src.app.models import ChartOutput 
from src.app.utils import save_log # Importa a função de log
from src.app.services.streamlit_runner import run_storyvis_flow # Importa o runner
from src.app.services.chat_service import get_chatbot_response # Importa o chatbot simples

# --- Configuração Inicial ---
st.set_page_config(page_title="StoryVis", layout="wide")

# --- TÍTULO (Bloco Popover REMOVIDO) ---
# O 'col_popover' foi removido para simplificar a UI.
st.title("StoryVis")
# --- FIM DA MUDANÇA ---
        

# --- Barra Lateral (Sidebar) (ATUALIZADA) ---
with st.sidebar:
    st.header("1. Configuração da Sessão")
    
    # --- CAMPO DE NOME MOVIDO PARA CÁ ---
    st.text_input(
        "Nome do Participante (Obrigatório)",
        key="participant_name", 
        placeholder="Ex: Ana Silva"
    )
    # --- FIM DA MUDANÇA ---

    st.header("2. Ajustes de IA")
    llm_provider = st.radio(
        "Escolha o modelo:",
        options=["gemini", "openai", "deepseek", "ollama"], index=0,
        format_func=lambda x: {
            "openai":   "🟢 OpenAI (GPT-4o-mini)",
            "gemini":   "🔵 Google Gemini Flash",
            "deepseek": "🟣 DeepSeek (via OpenRouter)",
            "ollama":   "⚪️ Ollama (Local)",
        }[x]
    )
    st.divider()

    st.header("3. Upload dos Dados")
    uploaded_file = st.file_uploader("Faça upload (CSV, XLSX)", type=["csv", "xlsx"])
    
    st.divider()
    
    if st.button("Limpar Conversa", type="primary"):
        st.session_state["messages"] = [{"role": "assistant", "content": "Olá! Faça upload de um arquivo e me peça um gráfico."}]
        # A galeria foi removida, então 'graph_type' será sempre o padrão 'IA'
        st.session_state["graph_type"] = "IA" 
        st.rerun()  

# --- Lógica do Chat Principal ---

# 1. Inicializa o Histórico
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá! Estou pronto para ajudar a criar seu dashboard."}]
if "participant_name" not in st.session_state:
    st.session_state.participant_name = ""

# 2. Exibe o Histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message: st.markdown(message["content"])
        if "chart" in message: st.altair_chart(message["chart"], use_container_width=True)
        if "error" in message: st.error(message["error"])

# 3. Campo de Entrada de Texto (LÓGICA REFATATORADA)
if prompt := st.chat_input("Converse comigo ou descreva o gráfico que você quer..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- VERIFICAÇÃO E EXECUÇÃO (Refatorado) ---
    
    participant_name = st.session_state.get("participant_name", "").strip()

    # 1. Verifica o NOME (Bloqueador principal)
    if not participant_name:
        error_msg = "Por favor, preencha o seu **Nome do Participante** (na barra lateral) antes de começar."
        st.session_state.messages.append({"role": "assistant", "error": error_msg})
        st.chat_message("assistant").error(error_msg)
    
    # 2. Decide: Modo Conversa ou Modo Geração?
    elif uploaded_file is None:
        # --- MODO CONVERSA (ARQUIVO AINDA NÃO ENVIADO) ---
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response_text = get_chatbot_response(
                    llm_choice=llm_provider,
                    chat_history=st.session_state.messages,
                    user_prompt=prompt
                )
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

    else:
        # --- MODO GERAÇÃO (ARQUIVO EXISTE) ---
        temp_dir: str | None = None
        full_prompt = ""
        start_time = time.monotonic() 
        
        with st.chat_message("assistant"):
            with st.spinner("Analisando dados e gerando visualização..."):
                try:
                    # --- 1. Preparação (Leve) ---
                    temp_dir = tempfile.mkdtemp()
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    
                    df = None
                    if file_path.endswith('.csv'): df = pd.read_csv(file_path)
                    elif file_path.endswith('.xlsx'): df = pd.read_excel(file_path)
                    if df is None: raise ValueError("Não foi possível ler o arquivo como DataFrame.")

                    # A galeria foi removida, o prompt agora é direto
                    full_prompt = prompt 
                    
                    # --- 2. CHAMADA DO RUNNER ---
                    result_data = run_storyvis_flow(
                        llm_choice=llm_provider,
                        full_prompt=full_prompt,
                        file_path=file_path,
                        participant_name=participant_name,
                        df=df
                    )

                    # --- 3. Renderização (Sucesso) ---
                    chart_object = result_data["chart_object"]
                    duration_sec = result_data["duration_sec"]
                    
                    st.session_state.messages.append({"role": "assistant", "chart": chart_object})
                    st.altair_chart(chart_object, use_container_width=True)
                    
                    with st.expander("Ver Relatório, Código e Métricas"):
                        st.metric(label="Tempo de Geração", value=f"{duration_sec:.2f} segundos")
                        st.subheader("Relatório de Avaliação")
                        st.markdown(result_data["report"])
                        st.subheader("Código Python Gerado")
                        st.code(result_data["final_code"], language="python")
                        st.subheader("Plano de Visualização (JSON)")
                        if result_data["viz_plan_str"]:
                            try: st.json(json.loads(result_data["viz_plan_str"]))
                            except: st.text(result_data["viz_plan_str"]) 
                        else: st.caption("Nenhum plano de visualização foi retornado.")
                    
                    # --- 4. LOG (SUCESSO) ---
                    log_payload = {
                        "final_code": result_data["final_code"],
                        "evaluation_report": result_data["report"],
                        "viz_plan_json": result_data["viz_plan_str"],
                        "token_usage": result_data["token_usage"].model_dump() if result_data["token_usage"] else None
                    }
                    save_log(participant_name, llm_provider, full_prompt, "SUCCESS", log_payload, duration_sec=duration_sec)

                except Exception as e:
                    # --- 4. LOG (FALHA) ---
                    end_time = time.monotonic()
                    duration_sec = end_time - start_time
                    
                    error_str = f"Ocorreu um erro durante a execução: {e}"
                    st.session_state.messages.append({"role": "assistant", "error": error_str})
                    st.error(error_str)
                    print(f"Erro no app.py: {e}") 
                    
                    log_payload = { "error_message": str(e) }
                    save_log(participant_name, llm_provider, full_prompt, "ERROR", log_payload, duration_sec=duration_sec)
                
                finally:
                    # Limpeza do arquivo temporário
                    if temp_dir and os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)