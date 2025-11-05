# src/app/services/streamlit_runner.py
# ------------------------------------
# (Versão Revertida - "Plano C" Robusto)
# Esta versão espera CÓDIGO PYTHON da crew e usa
# Regex e exec() para renderizar.

import re
import time
import altair as alt
import pandas as pd
import streamlit as st # Necessário para o escopo do exec()

from src.app.crew import StoryVisCrew
from src.app.models import ChartOutput # Usado na verificação

# Esta é a função que o app.py irá chamar
def run_storyvis_flow(
    llm_choice: str, 
    full_prompt: str, 
    file_path: str,
    participant_name: str,
    df: pd.DataFrame # O DataFrame carregado, OBRIGATÓRIO para o exec()
):
    """
    Executa o fluxo completo da crew (Kickoff + Parse Regex + Exec)
    Retorna um dicionário com os artefatos ou levanta uma exceção.
    """
    
    st.write(f"Iniciando fluxo (Participante: {participant_name}, Modelo: {llm_choice})...")
    
    inputs = { 'user_prompt': full_prompt, 'data_path': file_path }
    
    # --- 3. Instanciação e Execução da Crew ---
    crew_class = StoryVisCrew(llm_choice=llm_choice)
    storyvis_crew = crew_class.crew()
    
    start_time = time.monotonic()
    result = storyvis_crew.kickoff(inputs=inputs)
    
    # --- 4. Processamento do Resultado (PLANO C: PARSER REGEX v5) ---
    raw_output = result.raw if hasattr(result, 'raw') else str(result)
    if not raw_output:
        raise ValueError("A crew retornou uma saída vazia.")

    try:
        # Regex (como estava no app.py)
        code_match = re.search(r"""(?s)(?:final_code=|"final_code":\s*["'])(.*?)(?:evaluation_report=|",\s*"evaluation_report")""", raw_output)
        report_match = re.search(r"""(?s)(?:evaluation_report=|"evaluation_report":\s*["'])(.*?)(?:viz_plan_json=|",\s*"viz_plan_json")""", raw_output)
        plan_match = re.search(r"""(?s)(?:viz_plan_json=|"viz_plan_json":\s*["'])(\{.*\})""", raw_output)

        if not code_match or not report_match or not plan_match:
            # Fallback se o Pydantic (Plano A) falhou mas retornou algo
            if hasattr(result, 'pydantic') and isinstance(result.pydantic, ChartOutput):
                 print("--- [Debug Runner] Pydantic SUCESSO, usando Pydantic.")
                 chart_output = result.pydantic
                 final_code = chart_output.final_code
                 report = chart_output.evaluation_report
                 viz_plan_str = chart_output.viz_plan_json
            else:
                 raise ValueError("Não foi possível extrair (Regex) os campos 'final_code', 'evaluation_report' ou 'viz_plan_json' da saída bruta.")
        else:
            # Sucesso do Regex
            print("--- [Debug Runner] Parse Regex SUCESSO. ---")
            final_code = code_match.group(1).strip().strip("'\"")
            report = report_match.group(1).strip().strip("'\"")
            viz_plan_str = plan_match.group(1).strip().strip("'\"")
        
        # Limpeza Agressiva v5 (como estava no app.py)
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
        
    except Exception as e:
        print(f"--- ERRO DE PARSE REGEX (streamlit_runner.py) ---")
        print(f"Erro: {e}")
        raise TypeError(f"A saída da crew não pôde ser parseada com Regex.\nSaída Bruta do LLM: {raw_output}")

    # --- 5. Execução do Código Gerado (com exec()) ---
    chart_object = None
    # 'df' (o DataFrame) é injetado aqui!
    exec_globals = {'alt': alt, 'pd': pd, 'df': df, 'st': st}
    exec_locals = {} 
    
    chart_var_name = "chart" 
    matches = re.findall(r"st\.altair_chart\((\w+),", final_code)
    if matches: chart_var_name = matches[-1] 
    else:
        fallback_matches = re.findall(r"(\w+)\s*=\s*alt\.Chart", final_code)
        if fallback_matches: chart_var_name = fallback_matches[-1]
    
    final_code_cleaned = re.sub(r"st\.altair_chart\(.*\)", "", final_code)
    # Remove imports que o LLM possa ter alucinado
    final_code_cleaned = re.sub(r"import .*\n", "", final_code_cleaned)
    
    exec_code_block = f"{final_code_cleaned}\n\nchart = {chart_var_name}"
    
    try:
        exec(exec_code_block, exec_globals, exec_locals)
        chart_object = exec_locals.get('chart')
    except Exception as e:
        print(f"--- ERRO NO EXEC() ---")
        print(f"Código que falhou:\n{exec_code_block}")
        raise SyntaxError(f"Erro de sintaxe no código gerado pelo LLM: {e}")
    
    # --- Fim da Execução ---
    
    end_time = time.monotonic()
    duration_sec = end_time - start_time
    
    if chart_object:
        # Empacota os resultados de sucesso
        return {
            "status": "SUCCESS",
            "chart_object": chart_object,
            "final_code": final_code, # Retorna o código Python (para log)
            "report": report,
            "viz_plan_str": viz_plan_str,
            "duration_sec": duration_sec,
            "token_usage": result.token_usage if hasattr(result, 'token_usage') else None
        }
    else:
        raise ValueError(f"O fluxo foi concluído, mas o código gerado não criou um objeto de gráfico (esperado: '{chart_var_name}').")