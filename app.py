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
import time
#from io import StringIO
# Importações dos módulos do projeto
from src.app.services.streamlit_runner import run_storyvis_flow
from src.app.crew import StoryVisCrew
from src.app.models import ChartOutput 
from src.app.utils import save_log


# --- Configuração Inicial ---
st.set_page_config(
    page_title="StoryVis",
    page_icon="📊",
    layout="wide"
)

# --- Título e Popover da Galeria (COM CAMPO DE NOME) ---
col_title, col_popover = st.columns([10, 1])

with col_title:
    st.title("Sistema Conversacional de Geração e Design de Dashboards V2.0")

# with col_popover:
#     popover = st.popover("🧑‍💻", help="Configurações")
    
#     with popover:
#         st.subheader("Configuração da Sessão")
#         st.text_input(
#             "Nome do Participante (Obrigatório)",
#             key="participant_name", 
#             placeholder="Ex: Ana Silva"
#         )
        # st.divider()
        # st.subheader("Galeria de Visualizações")
        # st.caption("Clique para forçar um tipo de gráfico.")
        # col1, col2, col3 = st.columns(3)
        # def set_graph_type(graph_type):
        #     st.session_state["graph_type"] = graph_type
        #     st.toast(f"{graph_type} selecionado!")
        # with col1:
        #     if st.button("📈 Linhas", use_container_width=True): set_graph_type("Linhas")
        #     if st.button("🍕 Pizza", use_container_width=True): set_graph_type("Pizza") 
        # with col2:
        #     if st.button("📊 Barras", use_container_width=True): set_graph_type("Barras")
        #     if st.button("🫧 Dispersão", use_container_width=True): set_graph_type("Dispersão")
        # with col3:
        #     if st.button("🌳 Treemap", use_container_width=True): set_graph_type("Treemap")
        #     if st.button("🤖 Escolha por mim", use_container_width=True): set_graph_type("IA")
        # if "graph_type" not in st.session_state: st.session_state["graph_type"] = "IA" 
        # st.info(f"Seleção: **{st.session_state['graph_type']}**")
        

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.header("1. Upload dos Dados")
    uploaded_file = st.file_uploader(
        "Faça upload (CSV, XLSX)",
        type=["csv", "xlsx"]
    )
    st.divider()
    st.header("2. Ajustes de IA")
    llm_provider = st.radio(
        "Escolha o modelo:",
        options=["gemini", "openai", "deepseek", "ollama"],
        index=0,
        format_func=lambda x: {
            "openai":   "🟢 OpenAI (GPT-4o-mini)",
            "gemini":   "🔵 Google Gemini Flash",
            "deepseek": "🟣 DeepSeek",
            "ollama":   "⚪️ Ollama (Local)",
        }[x]
    )
    st.divider()
    st.header("3. Participante")
    st.text_input(
            "Nome do Participante (Obrigatório)",
            key="participant_name", 
            placeholder="Ex: Ana Silva"
        )
    st.divider()
    if st.button("Limpar Conversa", type="primary"):
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Olá! Faça upload de um arquivo e me peça um gráfico."}
        ]
        st.session_state["graph_type"] = "IA"
        st.rerun()  

# --- Lógica do Chat Principal ---

# 1. Inicializa o Histórico
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Olá! Faça upload de um arquivo e me peça um gráfico."}
    ]
if "participant_name" not in st.session_state:
    st.session_state.participant_name = ""

# 2. Exibe o Histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message: st.markdown(message["content"])
        if "chart" in message: st.altair_chart(message["chart"], use_container_width=True)
        if "error" in message: st.error(message["error"])

# 3. Campo de Entrada de Texto
if prompt := st.chat_input("Descreva o gráfico que você quer..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- VERIFICAÇÃO E EXECUÇÃO DO CREW ---
    
    participant_name = st.session_state.get("participant_name", "").strip()

    if uploaded_file is None:
        error_msg = "Por favor, faça o upload de um arquivo (CSV ou XLSX) na barra lateral primeiro."
        st.session_state.messages.append({"role": "assistant", "error": error_msg})
        st.chat_message("assistant").error(error_msg)
    
    elif not participant_name:
        error_msg = "Por favor, preencha o seu **Nome do Participante** (no ícone 📊 no topo) antes de começar."
        st.session_state.messages.append({"role": "assistant", "error": error_msg})
        st.chat_message("assistant").error(error_msg)
    
    else:
        temp_dir: str | None = None
        full_prompt = ""
        start_time = time.monotonic() # <-- Inicia o timer geral
        duration_sec = None
        
        with st.chat_message("assistant"):
            with st.spinner("Analisando dados e gerando visualização..."):
                try:
                    print("chegou aqui")
                    run_storyvis_flow(
                        uploaded_file, 
                        prompt, 
                        llm_provider, 
                        participant_name, 
                        st
                    )
                except Exception as e:
                    print("Erro ", e)
