# src/app/app.py
# -----------------
# Aplicação Streamlit (Frontend) para o StoryVis

import streamlit as st
import altair as alt
import json
import re  # <-- ADICIONADO IMPORT DE REGEX
import pandas as pd
import os
import tempfile
import shutil
from io import StringIO
import time 

# Importações dos módulos do projeto
# (Assumindo que você roda 'streamlit run src/app/app.py' da raiz do projeto)
from src.app.crew import StoryVisCrew
from src.app.models import ChartOutput 

# --- Configuração Inicial ---
st.set_page_config(
    page_title="StoryVis",
    layout="wide"
)

# --- Título e Popover da Galeria ---
col_title, col_popover = st.columns([10, 1])

with col_title:
    st.title("StoryVis")

with col_popover:
    popover = st.popover("📊", help="Galeria de Gráficos e Visualizações")
    
    with popover:
        st.subheader("Galeria de Visualizações")
        st.caption("Clique para forçar um tipo de gráfico.")
        col1, col2, col3 = st.columns(3)
        def set_graph_type(graph_type):
            st.session_state["graph_type"] = graph_type
            st.toast(f"{graph_type} selecionado!")
        with col1:
            if st.button("📈 Linhas", use_container_width=True): set_graph_type("Linhas")
            if st.button("🍕 Pizza", use_container_width=True): set_graph_type("Pizza") 
        with col2:
            if st.button("📊 Barras", use_container_width=True): set_graph_type("Barras")
            if st.button("🫧 Dispersão", use_container_width=True): set_graph_type("Dispersão")
        with col3:
            if st.button("🌳 Treemap", use_container_width=True): set_graph_type("Treemap")
            if st.button("🤖 Escolha por mim", use_container_width=True): set_graph_type("IA")
        if "graph_type" not in st.session_state: st.session_state["graph_type"] = "IA" 
        st.info(f"Seleção: **{st.session_state['graph_type']}**")
        

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
        # (Nota: 'ollama' precisará de configuração no crew.py)
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
    
    if uploaded_file is None:
        error_msg = "Por favor, faça o upload de um arquivo (CSV ou XLSX) na barra lateral primeiro."
        st.session_state.messages.append({"role": "assistant", "error": error_msg})
        st.chat_message("assistant").error(error_msg)
    
    else:
        temp_dir: str | None = None
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
                    st.write(f"Iniciando fluxo (Modelo: {llm_provider})...")
                    crew_class = StoryVisCrew(llm_choice=llm_provider)
                    storyvis_crew = crew_class.crew()
                    result = storyvis_crew.kickoff(inputs=inputs)
                    
                    # --- 4. Processamento do Resultado (PLANO C: PARSER REGEX) ---
                    raw_output = result.raw if hasattr(result, 'raw') else str(result)
                    
                    if not raw_output:
                        raise ValueError("A crew retornou uma saída vazia.")

                    try:
                        # Regex para extrair o código
                        code_match = re.search(
                            r"""(?s)(?:final_code=|"final_code":\s*["'])(.*?)(?:evaluation_report=|",\s*"evaluation_report")""",
                            raw_output
                        )
                        # Regex para extrair o relatório
                        report_match = re.search(
                            r"""(?s)(?:evaluation_report=|"evaluation_report":\s*["'])(.*?)(?:viz_plan_json=|",\s*"viz_plan_json")""",
                            raw_output
                        )
                        # Regex para extrair o plano
                        plan_match = re.search(
                            r"""(?s)(?:viz_plan_json=|"viz_plan_json":\s*["'])(\{.*\})""",
                            raw_output
                        )

                        if not code_match or not report_match or not plan_match:
                            raise ValueError("Não foi possível extrair (Regex) os campos 'final_code', 'evaluation_report' ou 'viz_plan_json' da saída bruta.")

                        final_code = code_match.group(1).strip().strip("'\"")
                        report = report_match.group(1).strip().strip("'\"")
                        viz_plan_str = plan_match.group(1).strip().strip("'\"")
                        
                        # --- CORREÇÃO / LIMPEZA AGRESSIVA v5 (Manual) ---
                        
                        # Etapa 1: Corrigir aspas duplas e simples (ex: `\"` -> `"`)
                        final_code = final_code.replace('\\"', '"').replace("\\'", "'")
                        report = report.replace('\\"', '"').replace("\\'", "'")
                        
                        # Etapa 2: Corrigir newlines escapados (ex: `\\n` -> `\n`)
                        final_code = final_code.replace("\\n", "\n")
                        report = report.replace("\\n", "\n")

                        # Etapa 3: Corrigir backslashes de continuação de linha (O que causa o SyntaxError)
                        # Vamos dividir o código em linhas, remover o '\' do final de cada linha,
                        # e depois juntar tudo de volta.
                        
                        linhas_limpas_code = []
                        for linha in final_code.splitlines():
                            # Remove espaços em branco do final e depois verifica se termina com '\'
                            if linha.rstrip().endswith('\\'):
                                # Adiciona a linha SEM o último caractere
                                linhas_limpas_code.append(linha.rstrip()[:-1])
                            else:
                                linhas_limpas_code.append(linha)
                        final_code = "\n".join(linhas_limpas_code)
                        
                        # Faz o mesmo para o relatório
                        linhas_limpas_report = []
                        for linha in report.splitlines():
                            if linha.rstrip().endswith('\\'):
                                linhas_limpas_report.append(linha.rstrip()[:-1])
                            else:
                                linhas_limpas_report.append(linha)
                        report = "\n".join(linhas_limpas_report)
                        
                        # --- FIM DA CORREÇÃO ---

                    except Exception as e:
                        print(f"--- ERRO DE PARSE REGEX (app.py) ---")
                        print(f"Erro: {e}")
                        raise TypeError(
                            "A saída da crew não pôde ser parseada com Regex.\n"
                            f"Saída Bruta do LLM: {raw_output}"
                        )

                    # --- 5. Execução do Código Gerado ---

                    chart_object = None

                    exec_globals = {
                        'alt': alt, 'pd': pd, 'df': df, 'st': st
                    }
                    exec_locals = {} # Onde o resultado (chart) aparecerá

                    # --- CORREÇÃO DO PARSER DE VARIÁVEL ---
                    # O Regex anterior pegava 'base = alt.Chart', que é incompleto.
                    # Este Regex novo encontra a variável DENTRO da chamada 'st.altair_chart(VARIAVEL, ...)'

                    chart_var_name = "chart" # Padrão

                    # Encontra todas as chamadas st.altair_chart(NOME_DA_VARIAVEL, ...)
                    matches = re.findall(r"st\.altair_chart\((\w+),", final_code)

                    if matches:
                        # Pega o NOME DA VARIÁVEL da *última* chamada st.altair_chart
                        chart_var_name = matches[-1] 
                    else:
                        # Fallback: Se não houver 'st.altair_chart', procura pelo último 'alt.Chart'
                        fallback_matches = re.findall(r"(\w+)\s*=\s*alt\.Chart", final_code)
                        if fallback_matches:
                            chart_var_name = fallback_matches[-1] # Pega o último

                    # O agente está incluindo o st.altair_chart() em seu código.
                    # Vamos removê-lo para que NÓS possamos controlar a renderização e salvar no histórico.
                    final_code_cleaned = re.sub(r"st\.altair_chart\(.*\)", "", final_code)

                    exec_code_block = f"{final_code_cleaned}\n\nchart = {chart_var_name}"

                    # --- FIM DA CORREÇÃO ---


                    # --- Bloco de Debug (Pode manter por enquanto) ---
                    print("\n" + "="*30)
                    print("--- [DEBUG] ANTES DO EXEC() ---")
                    print(f"Variável do Gráfico (detectada): {chart_var_name}")
                    print("--- Conteúdo de 'final_code' (limpo): ---")
                    print(final_code_cleaned)
                    print("--- Fim de 'final_code'. ---")
                    print("="*30 + "\n")
                    # --- FIM DO DEBUG ---


                    exec(exec_code_block, exec_globals, exec_locals)
                    chart_object = exec_locals.get('chart')

                    # --- 6. Renderização no Streamlit ---
                    
                    if chart_object:
                        st.session_state.messages.append({"role": "assistant", "chart": chart_object})
                        st.altair_chart(chart_object, use_container_width=True)
                        
                        with st.expander("Ver Relatório, Código e Métricas"):
                            st.subheader("Relatório de Avaliação")
                            st.markdown(report)
                            
                            st.subheader("Código Python Gerado")
                            st.code(final_code, language="python")
                            
                            st.subheader("Plano de Visualização (JSON)")
                            if viz_plan_str:
                                # Tenta formatar o JSON para exibição bonita
                                try:
                                    st.json(json.loads(viz_plan_str))
                                except:
                                    st.text(viz_plan_str) # Mostra como texto se o JSON estiver quebrado
                            else:
                                st.caption("Nenhum plano de visualização foi retornado.")
                    
                    else:
                        raise ValueError(f"O fluxo foi concluído, mas o código gerado não criou um objeto de gráfico (esperado: '{chart_var_name}').")

                except Exception as e:
                    error_str = f"Ocorreu um erro durante a execução: {e}"
                    st.session_state.messages.append({"role": "assistant", "error": error_str})
                    st.error(error_str)
                    print(f"Erro no app.py: {e}") 
                
                finally:
                    if temp_dir and os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)