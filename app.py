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
import time # Import já existente, agora usado para o timer

# --- NOVOS IMPORTS PARA LOGGING ---
from datetime import datetime
import uuid
# ----------------------------------

# Importações dos módulos do projeto
from src.app.crew import StoryVisCrew
from src.app.models import ChartOutput 

# --- NOVA CONFIGURAÇÃO DE LOGS ---
LOGS_DIR = "src/logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# --- 'save_log' ATUALIZADA PARA INCLUIR DURAÇÃO ---
def save_log(participant, llm, prompt, status, data_payload, duration_sec=None):
    """Salva um registro da execução em um arquivo JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    safe_participant_name = re.sub(r'[^a-zA-Z0-9]', '_', participant)
    
    filename = f"{timestamp}_{safe_participant_name}_{unique_id}.json"
    filepath = os.path.join(LOGS_DIR, filename)

    log_entry = {
        "log_id": f"{timestamp}_{unique_id}",
        "participant_name": participant,
        "llm_provider": llm,
        "duration_seconds": duration_sec, # <-- CAMPO ADICIONADO
        "user_prompt": prompt,
        "status": status,
        "payload": data_payload,
        # "token_usage": (
        #     result.token_usage.model_dump() 
        #     if hasattr(result, 'token_usage') and result.token_usage 
        #     else None
        # )
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"--- CRITICAL: FALHA AO SALVAR O LOG ---")
        print(f"--- Erro: {e} ---")
# --- FIM DA CONFIGURAÇÃO DE LOGS ---


# --- Configuração Inicial ---
st.set_page_config(
    page_title="StoryVis",
    layout="wide"
)

# --- Título e Popover da Galeria (COM CAMPO DE NOME) ---
col_title, col_popover = st.columns([10, 1])

with col_title:
    st.title("StoryVis")

with col_popover:
    popover = st.popover("🧑‍💻", help="Configurações")
    
    with popover:
        st.subheader("Configuração da Sessão")
        st.text_input(
            "Nome do Participante (Obrigatório)",
            key="participant_name", 
            placeholder="Ex: Ana Silva"
        )
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
                    # --- 1. Preparação do Arquivo e DataFrame ---
                    temp_dir = tempfile.mkdtemp()
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    
                    df = None
                    if file_path.endswith('.csv'): df = pd.read_csv(file_path)
                    elif file_path.endswith('.xlsx'): df = pd.read_excel(file_path)
                    if df is None: raise ValueError("Não foi possível ler o arquivo como DataFrame.")

                    # --- 2. Preparação dos Inputs da Crew ---
                    graph_type_selection = st.session_state.get("graph_type", "IA")
                    full_prompt = prompt 
                    if graph_type_selection != "IA":
                        full_prompt += f"\n\nInstrução Adicional: O usuário sugeriu um gráfico do tipo: {graph_type_selection}."
                    
                    inputs = { 'user_prompt': full_prompt, 'data_path': file_path }

                    # --- 3. Instanciação e Execução da Crew ---
                    st.write(f"Iniciando fluxo (Participante: {participant_name}, Modelo: {llm_provider})...")
                    crew_class = StoryVisCrew(llm_choice=llm_provider)
                    storyvis_crew = crew_class.crew()
                    
                    # --- TEMPO INICIA AQUI ---
                    start_time = time.monotonic() 
                    result = storyvis_crew.kickoff(inputs=inputs)
                    # --- TEMPO TERMINA (PROVISORIAMENTE) AQUI ---
                    
                    # --- 4. Processamento do Resultado (PLANO C: PARSER REGEX v5) ---
                    raw_output = result.raw if hasattr(result, 'raw') else str(result)
                    if not raw_output: raise ValueError("A crew retornou uma saída vazia.")
                    
                    code_match = re.search(r"""(?s)(?:final_code=|"final_code":\s*["'])(.*?)(?:evaluation_report=|",\s*"evaluation_report")""", raw_output)
                    report_match = re.search(r"""(?s)(?:evaluation_report=|"evaluation_report":\s*["'])(.*?)(?:viz_plan_json=|",\s*"viz_plan_json")""", raw_output)
                    plan_match = re.search(r"""(?s)(?:viz_plan_json=|"viz_plan_json":\s*["'])(\{.*\})""", raw_output)

                    if not code_match or not report_match or not plan_match:
                        raise ValueError("Não foi possível extrair (Regex) os campos 'final_code', 'evaluation_report' ou 'viz_plan_json' da saída bruta.")

                    final_code = code_match.group(1).strip().strip("'\"")
                    report = report_match.group(1).strip().strip("'\"")
                    viz_plan_str = plan_match.group(1).strip().strip("'\"")
                    
                    # Limpeza Agressiva v5
                    final_code = final_code.replace('\\"', '"').replace("\\'", "'")
                    report = report.replace('\\"', '"').replace("\\'", "'")
                    final_code = final_code.replace("\\n", "\n")
                    report = report.replace("\\n", "\n")
                    
                    linhas_limpas_code = []
                    for linha in final_code.splitlines():
                        if linha.rstrip().endswith('\\'): linhas_limpas_code.append(linha.rstrip()[:-1])
                        else: linhas_limpas_code.append(linha)
                    final_code = "\n".join(linhas_limpas_code)
                    
                    linhas_limpas_report = []
                    for linha in report.splitlines():
                        if linha.rstrip().endswith('\\'): linhas_limpas_report.append(linha.rstrip()[:-1])
                        else: linhas_limpas_report.append(linha)
                    report = "\n".join(linhas_limpas_report)
                    
                    # --- 5. Execução do Código Gerado ---
                    chart_object = None
                    exec_globals = {'alt': alt, 'pd': pd, 'df': df, 'st': st}
                    exec_locals = {} 
                    
                    chart_var_name = "chart" 
                    matches = re.findall(r"st\.altair_chart\((\w+),", final_code)
                    if matches: chart_var_name = matches[-1] 
                    else:
                        fallback_matches = re.findall(r"(\w+)\s*=\s*alt\.Chart", final_code)
                        if fallback_matches: chart_var_name = fallback_matches[-1]
                    
                    final_code_cleaned = re.sub(r"st\.altair_chart\(.*\)", "", final_code)
                    exec_code_block = f"{final_code_cleaned}\n\nchart = {chart_var_name}"
                    
                    exec(exec_code_block, exec_globals, exec_locals)
                    chart_object = exec_locals.get('chart')

                    # --- 6. Renderização no Streamlit ---
                    if chart_object:
                        # --- CAPTURA TEMPO DE SUCESSO ---
                        end_time = time.monotonic()
                        duration_sec = end_time - start_time
                        
                        st.session_state.messages.append({"role": "assistant", "chart": chart_object})
                        st.altair_chart(chart_object, use_container_width=True)
                        
                        with st.expander("Ver Relatório, Código e Métricas"):
                            
                            # --- EXIBE O TEMPO ---
                            st.metric(label="Tempo de Geração", value=f"{duration_sec:.2f} segundos")
                            
                            st.subheader("Relatório de Avaliação")
                            st.markdown(report)
                            st.subheader("Código Python Gerado")
                            st.code(final_code, language="python")
                            st.subheader("Plano de Visualização (JSON)")
                            if viz_plan_str:
                                try: st.json(json.loads(viz_plan_str))
                                except: st.text(viz_plan_str) 
                            else: st.caption("Nenhum plano de visualização foi retornado.")
                        
                        # --- CHAMADA DE LOG (SUCESSO) ---
                        log_data = {
                            "final_code": final_code,
                            "evaluation_report": report,
                            "viz_plan_json": viz_plan_str,
                            # Adiciona as métricas de token/uso
                            "token_usage": result.token_usage if hasattr(result, 'token_usage') else None
                        }
                        save_log(participant_name, llm_provider, full_prompt, "SUCCESS", log_data, duration_sec=duration_sec)
                        # -----------------------------
                    
                    else:
                        raise ValueError(f"O fluxo foi concluído, mas o código gerado não criou um objeto de gráfico (esperado: '{chart_var_name}').")

                except Exception as e:
                    # --- CAPTURA TEMPO DE FALHA ---
                    end_time = time.monotonic()
                    duration_sec = end_time - start_time
                    
                    error_str = f"Ocorreu um erro durante a execução: {e}"
                    st.session_state.messages.append({"role": "assistant", "error": error_str})
                    st.error(error_str)
                    print(f"Erro no app.py: {e}") 
                    
                    # --- CHAMADA DE LOG (FALHA) ---
                    raw_output_on_error = "N/A (Erro antes da execução da crew)"
                    token_usage_on_error = None
                    if 'result' in locals():
                        if hasattr(result, 'raw'): raw_output_on_error = result.raw
                        if hasattr(result, 'token_usage'): token_usage_on_error = result.token_usage
                    
                    log_data = {
                        "error_message": str(e),
                        "raw_output": raw_output_on_error,
                        "token_usage": token_usage_on_error
                    }
                    save_log(participant_name, llm_provider, full_prompt, "ERROR", log_data, duration_sec=duration_sec)
                    # ---------------------------
                
                finally:
                    if temp_dir and os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)