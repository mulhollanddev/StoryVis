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
import json
#from groq import Groq 

# ===============================================
# Configuração da Página
# ===============================================
st.set_page_config(page_title="StoryVis", layout="wide", page_icon="📊")

# --- Importações Locais ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports de Lógica
try:
    from src.app.crew import StoryVisCrew
    from src.app.services.logger import salvar_log_pinecone, salvar_feedback_pinecone
    from src.app.utils import (
        carregar_dados, salvar_temp_csv, limpar_codigo_ia, 
        separar_narrativa_codigo, inicializar_session_state,
        buscar_coordenadas_ia, detectar_coluna_geo_ia
    )
    from src.app.demo import carregar_demo_inicial
    
    LOGGING_ATIVO = True
except ImportError as e:
    st.error(f"Erro crítico de importação: {e}")
    st.stop()

# ===============================================
# Funções Auxiliares (Ajustadas para Robustez)
# ===============================================

def router_intencao(prompt_usuario):
    """
    Decide se o pedido é complexo e se precisa de cálculo matemático.
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        system_prompt = """
        Classifique o pedido em JSON:
        1. "complexidade": "alta" se pedir gráficos combinados, camadas, arcos, duplo eixo ou visualizações avançadas. "baixa" para gráficos padrão.
        2. "calculo": true se pedir explicitamente médias, máximos, mínimos, "destaque o maior", "calcule a diferença" ou KPIs. false se for apenas visual.
        """
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_usuario}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Erro no router: {e}")
        return {"complexidade": "baixa", "calculo": False}

def is_python_code(text):
    """Verifica se o texto parece código Python ou texto natural."""
    keywords = ['import ', 'st.', 'pd.', 'print(', 'def ', '=', 'return']
    return any(k in text for k in keywords)

# Inicialização de Estado
inicializar_session_state(carregar_demo_inicial)
if "codigo_calculo" not in st.session_state:
    st.session_state["codigo_calculo"] = ""

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
    
    # --- Upload e Nome ---
    col_nome, col_upload = st.columns([1, 2], gap="medium")
    with col_nome:
        nome_input = st.text_input("👤 Nome Completo (Obrigatório)", placeholder="Digite seu nome...", key="input_nome_user")
        st.session_state["nome_participante"] = nome_input
        
    with col_upload:
        uploaded_file = st.file_uploader("📂 Carregar Arquivo Próprio", type=["csv", "xlsx", "xls"])

    # --- Processamento do Upload ---
    if uploaded_file:
        if "arquivo_cache" not in st.session_state or st.session_state["arquivo_cache"] != uploaded_file.name:
            df_loaded = carregar_dados(uploaded_file)
            if df_loaded is not None:
                st.session_state["df_original"] = df_loaded
                st.session_state["df_final"] = df_loaded.copy()
                st.session_state["arquivo_cache"] = uploaded_file.name
                st.session_state["modo_demo"] = False
                
                # Resets
                st.session_state["codigo_final"] = ""
                st.session_state["codigo_calculo"] = "" 
                st.session_state["narrativa_final"] = ""
                st.toast("Arquivo carregado!", icon="✅")

    st.divider()

    # ==========================================================
    # 🧠 ÁREA DE INTELIGÊNCIA GEOGRÁFICA (VISUAL NOVO)
    # ==========================================================
    
    # 1. Detecta silenciosamente usando o DF atual
    df_atual = st.session_state["df_final"]
    col_geo_sugerida = detectar_coluna_geo_ia(df_atual)

    # 2. Se detectar, mostra o novo layout
    if col_geo_sugerida:
        # Cálculos prévios
        locais_unicos = df_atual[col_geo_sugerida].dropna().unique().tolist()
        qtd_locais = len(locais_unicos)
        LIMITE_MAXIMO = 30
        
        # --- A. O ALERTA AMARELO (Visualização rápida) ---
        st.warning(
            f"📍 **Inteligência Geográfica:** Detectamos a coluna `{col_geo_sugerida}` com **{qtd_locais}** locais únicos.", 
            icon="🌍"
        )
        
        # --- B. O EXPANDER (A "coluna que abaixa e levanta") ---
        with st.expander("🌍 Clique aqui para utilizar Inteligência Geográfica e gerar mapas"):
            
            st.markdown("""
            <small>A IA irá buscar Latitude, Longitude e Códigos de Área (Estados/Países) 
            para permitir a criação de mapas de pontos e mapas de calor (coropléticos).</small>
            """, unsafe_allow_html=True)
            
            st.write("") # Espaço para respiro
            
            # Lógica da Trava de Segurança
            if qtd_locais > LIMITE_MAXIMO:
                st.error(
                    f"⚠️ **Limite excedido para processamento via IA.**\n\n"
                    f"Você possui **{qtd_locais}** locais únicos, mas o limite é **{LIMITE_MAXIMO}**.\n"
                    "Por favor, filtre seus dados (ex: selecione apenas um ano ou região) para habilitar o mapeamento."
                )
            else:
                # Botão (Só aparece se estiver dentro do limite)
                if st.button("✨ Iniciar Mapeamento Automático", type="primary", use_container_width=True):
                    
                    with st.status(f"🤖 IA analisando {qtd_locais} locais...", expanded=True) as status:
                        coords = buscar_coordenadas_ia(locais_unicos)
                        
                        if coords:
                            df_temp = df_atual.copy()
                            
                            # Função auxiliar blindada
                            def get_safe(local, key):
                                dados = coords.get(local)
                                if isinstance(dados, dict):
                                    return dados.get(key)
                                return None

                            # 1. Injeta PONTOS
                            df_temp['Latitude'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'lat'))
                            df_temp['Longitude'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'lon'))
                            
                            # 2. Injeta ÁREAS (GeoCode/ISO)
                            df_temp['geo_code'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'geo_code'))
                            df_temp['country_iso'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'country_iso'))
                            
                            # 3. Limpeza de Tipos
                            df_temp['Latitude'] = pd.to_numeric(df_temp['Latitude'], errors='coerce')
                            df_temp['Longitude'] = pd.to_numeric(df_temp['Longitude'], errors='coerce')
                            df_temp['geo_code'] = df_temp['geo_code'].fillna('').astype(str).replace({'nan': '', 'None': ''})
                            df_temp['country_iso'] = df_temp['country_iso'].fillna('').astype(str).replace({'nan': '', 'None': ''})
                            
                            st.session_state["df_final"] = df_temp
                            status.update(label="✅ Dados Geográficos Completos!", state="complete")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro: A IA não retornou dados válidos.")

    # ==========================================================
    # 📊 ÁREA DA TABELA (ABAIXO DA INTELIGÊNCIA)
    # ==========================================================
    
    col_tit, col_btn_res = st.columns([3, 1])
    with col_tit:
        origem = "Demo" if st.session_state.get("modo_demo") else "Seu Arquivo"
        st.markdown(f"**Tabela de Dados ({origem})**")
    
    with col_btn_res:
        if st.button("🔄 Restaurar Demo", use_container_width=True):
            df_d, cod_d, narr_d = carregar_demo_inicial()
            st.session_state["df_final"] = df_d
            st.session_state["modo_demo"] = True
            st.rerun()

    # Editor de dados (Agora com a key para evitar erro de ID)
    df_editado = st.data_editor(
        st.session_state["df_final"], 
        width="stretch", 
        num_rows="dynamic",
        key="main_data_editor"
    )
    # Atualiza o estado se houver edição manual
    st.session_state["df_final"] = df_editado
# -------------------------------------------------------
# ABA 2: DASHBOARD + MONITORAMENTO
# -------------------------------------------------------
with tab_dash:
    st.subheader("Painel Visual")
    
    nome_atual = st.session_state.get("nome_participante", "Anônimo").strip()
    if not nome_atual: nome_atual = "Anônimo"

    # --- Área de Criação ---
    instrucao = st.text_input("🎯 Criar Dashboard Inicial:", placeholder="Ex: Compare a potência e destaque a maior média...")
    
    desabilitado = (nome_atual == "Anônimo" or nome_atual == "")
    if desabilitado: 
        st.error("🚨 **Obrigatório:** Vá na aba 'Dados' e preencha seu Nome para liberar.")
    
    gerar = st.button("🚀 Gerar dashboard", type="primary", width="stretch", disabled=desabilitado)

    if gerar:
        start_time = time.time()
        log_buffer = io.StringIO()
        
        with st.status("🧠 Analisando requisição...", expanded=True) as status:
            try:
                # 1. ROTEAMENTO DE INTENÇÃO
                #intencao = router_intencao(instrucao)
                #eh_complexo = intencao.get("complexidade") == "alta"
                precisa_calculo = False
                
                # Prepara Inputs
                df_atual = st.session_state["df_final"]
                rows, cols = df_atual.shape
                origem_dados = "Demo" if st.session_state.get("modo_demo") else "Upload"
                
                temp_path = salvar_temp_csv(df_atual)
                # Adiciona caminho ao session state para uso no exec
                st.session_state["temp_csv_path"] = temp_path 
                
                buffer = [f"Colunas: {list(df_atual.columns)}", df_atual.head(3).to_markdown(index=False)]
                user_req = f"Usuário: {nome_atual}. Pedido: {instrucao}"
                inputs = {'file_path': temp_path, 'user_request': user_req, 'data_summary': "\n".join(buffer)}
                
                est_tokens_in = len(str(inputs)) / 4
                
                # 2. EXECUÇÃO DO FLUXO PRINCIPAL (Visual)
                with contextlib.redirect_stdout(log_buffer):
                    eh_complexo = False  # Temporariamente desativado
                    if eh_complexo:
                        st.toast("Modo Visual Avançado Ativado! 🔥", icon="🎨")
                        status.write("Gerando visualização complexa...")
                        result = StoryVisCrew().crew_complex().kickoff(inputs=inputs)
                    else:
                        status.write("Gerando visualização padrão...")
                        result = StoryVisCrew().crew().kickoff(inputs=inputs)
                
                raw = result.raw
                narrativa, codigo_sujo = separar_narrativa_codigo(raw)
                codigo_limpo = limpar_codigo_ia(codigo_sujo)

                # 3. EXECUÇÃO DO FLUXO DE CÁLCULO (Opcional)
                codigo_calc_limpo = ""
                if precisa_calculo:
                    status.write("🧮 Calculando métricas exatas (Pandas)...")
                    try:
                        res_calc = StoryVisCrew().crew_calculation().kickoff(inputs=inputs)
                        # Tenta limpar, mas se não for código, usa o texto puro
                        codigo_calc_limpo = limpar_codigo_ia(res_calc.raw)
                        if not codigo_calc_limpo: # Se limpou demais, pega o raw
                            codigo_calc_limpo = res_calc.raw
                    except Exception as e_calc:
                        print(f"Erro no cálculo: {e_calc}")

                # 4. Atualização de Estado
                st.session_state["codigo_final"] = codigo_limpo
                st.session_state["codigo_calculo"] = codigo_calc_limpo
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
                    tipo_acao = "CREATE_COMPLEX" if eh_complexo else "CREATE"
                    salvar_log_pinecone(
                        usuario=nome_atual, input_usuario=instrucao, 
                        output_ia=codigo_limpo, output_narrativa=narrativa,
                        status="Sucesso", execution_time=tempo_total,
                        terminal_log=terminal_output, dataset_rows=rows, dataset_cols=cols,
                        data_source=origem_dados, action_type=tipo_acao,
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
                # Injeta variáveis essenciais no contexto local
                local_ctx = {
                    "pd": pd, 
                    "st": st, 
                    "alt": alt, 
                    "df": st.session_state["df_final"],
                    "file_path": st.session_state.get("temp_csv_path", "") # Injeta o caminho do arquivo
                }
                exec(st.session_state["codigo_final"], globals(), local_ctx)
            except Exception as e:
                st.warning("⚠️ O código gerado contém erros ou os dados mudaram.")
                with st.expander("Ver erro técnico"): st.write(e)
        else:
            st.info("O gráfico aparecerá aqui.")

    # --- Área de Cálculos (Scorecards) ---
    if st.session_state.get("codigo_calculo"):
        st.markdown("---")
        container_calc = st.container(border=True)
        with container_calc:
            st.markdown("#### 🧮 Destaques Calculados")
            calc_content = st.session_state["codigo_calculo"]
            
            # Verificação Inteligente: É código ou texto?
            if is_python_code(calc_content):
                try:
                    local_ctx_calc = {
                        "pd": pd, "st": st, 
                        "df": st.session_state["df_final"],
                        "file_path": st.session_state.get("temp_csv_path", "")
                    }
                    exec(calc_content, globals(), local_ctx_calc)
                except Exception as e:
                    st.warning("Erro ao executar cálculo matemático.")
                    # Se falhar, mostra o código para debug
                    with st.expander("Ver código do cálculo"): st.code(calc_content)
            else:
                # Se não for código, assume que o agente respondeu em texto direto
                st.write(calc_content)

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

# -------------------------------------------------------
# ABA 4: FEEDBACK
# -------------------------------------------------------
with tab_feedback:
    st.subheader("🗣️ Pesquisa de Satisfação e Perfil")
    
    # --- 1. Verificação de Identidade ---
    nome_feedback = st.session_state.get("nome_participante", "").strip()
    if not nome_feedback:
        st.warning("⚠️ Para participar da pesquisa, preencha seu **Nome** na aba '✏️ Dados'.")
    else:
        st.success(f"Participante Identificado: **{nome_feedback}**")

    # --- 2. O Grande Formulário ---
    with st.form("form_feedback"):
        
        # =======================================
        # BLOCO A: PERFIL DEMOGRÁFICO
        # =======================================
        st.markdown("### 1. Perfil do Participante")
        
        col_demo1, col_demo2 = st.columns(2)
        with col_demo1:
            sexo = st.selectbox(
                "Sexo:", 
                ["Masculino", "Feminino", "Prefiro não informar", "Outro"],
                index=None, placeholder="Selecione..."
            )
            idade_faixa = st.selectbox(
                "Faixa Etária:",
                ["18-24 anos", "25-34 anos", "35-44 anos", "45-54 anos", "55+ anos"],
                index=None, placeholder="Selecione..."
            )

        with col_demo2:
            escolaridade = st.selectbox(
                "Nível de Escolaridade:", 
                ["Ensino Médio", "Graduação (Cursando)", "Graduação (Completo)", "Pós-Graduação (Mestrado/Doutorado)"],
                index=None, placeholder="Selecione..."
            )
            area_atuacao = st.selectbox(
                "Área de Formação/Atuação:",
                ["Ciências Exatas/Tecnologia", "Ciências Humanas/Sociais", "Ciências da Saúde/Biológicas", "Linguística/Letras/Artes", "Outra"],
                index=None, placeholder="Selecione..."
            )

        st.divider()

        # =======================================
        # BLOCO B: PERFIL TÉCNICO (NOVAS PERGUNTAS!)
        # =======================================
        st.markdown("### 2. Perfil Técnico e Experiência")
        st.caption("Ajude-nos a entender sua familiaridade com as tecnologias envolvidas.")

        # Pergunta 1: Frequência de IA (Refinada)
        freq_ai = st.select_slider(
            "Com que frequência você utiliza IAs Generativas (ChatGPT, Gemini, etc.)?",
            options=["Nunca utilizei", "Raramente", "Mensalmente", "Semanalmente", "Diariamente"],
            value="Raramente"
        )
        
        col_tec1, col_tec2 = st.columns(2)
        with col_tec1:
            # Pergunta 2: Nível em Dados
            nivel_dados = st.selectbox(
                "Nível de conhecimento em Análise de Dados:",
                ["Iniciante (Curioso)", "Básico (Entendo tabelas)", "Intermediário (Faço análises)", "Avançado/Especialista"],
                index=None, placeholder="Selecione..."
            )
            
        with col_tec2:
            # Pergunta 3: Experiência com Gráficos
            nivel_viz = st.selectbox(
                "Experiência com criação de Gráficos/Dashboards:",
                ["Nunca criei", "Básico (Excel simples)", "Intermediário (PowerBI/Tableau)", "Avançado (Programação/D3.js)"],
                index=None, placeholder="Selecione..."
            )

        # Pergunta Extra (Sugestão): Programação
        st.write("")
        conhece_prog = st.radio(
            "Você tem algum conhecimento de programação (Python, R, etc)?",
            ["Não, nenhum", "Básico (Lógica)", "Sim, programo regularmente"],
            horizontal=True
        )

        st.divider()

        # =======================================
        # BLOCO C: AVALIAÇÃO DA FERRAMENTA
        # =======================================
        st.markdown("### 3. Avaliação da Experiência (Checklist)")
        
        col_testes_A, col_testes_B = st.columns(2)
        with col_testes_A:
            c1_resp = st.radio("1. Bloqueio de Segurança (Nome):", ["Funcionou", "Fiquei confuso", "Não testei"], index=2)
            c2_resp = st.radio("2. Gráfico Demo (IA):", ["Funcionou", "Deu erro", "Não testei"], index=2)
            c3_resp = st.radio("3. Mapa/Geocodificação:", ["Mapa gerado", "Erro no mapa", "Não testei"], index=2)

        with col_testes_B:
            c4_resp = st.radio("4. Evolução (2º Gráfico):", ["Adicionou ok", "Substituiu o anterior", "Não testei"], index=2)
            c5_resp = st.radio("5. Edição de Código:", ["Funcionou", "Falhou", "Não testei"], index=2)

        st.write("")
        st.markdown("#### Nota Final")
        st.write("Qual sua nota geral para o StoryVis?")
        feedback_stars = st.feedback("stars")
        
        comentario = st.text_area("Comentários, sugestões ou bugs:", placeholder="Digite aqui...")
        
        # Botão de Envio
        enviou = st.form_submit_button("✅ Enviar Pesquisa Completa", type="primary", disabled=(not nome_feedback))
        
        if enviou:
            # Validação dos campos obrigatórios
            campos_demo_ok = all([sexo, idade_faixa, escolaridade, area_atuacao])
            campos_tec_ok = all([nivel_dados, nivel_viz])
            
            if not campos_demo_ok or not campos_tec_ok:
                st.error("⚠️ Por favor, preencha todos os campos de **Perfil Demográfico** e **Perfil Técnico**.")
            elif feedback_stars is None:
                st.error("⚠️ Por favor, dê uma nota (estrelas) para a ferramenta.")
            else:
                if LOGGING_ATIVO:
                    nota_final = feedback_stars + 1
                    
                    # Agrupa TODO o perfil (Demográfico + Técnico) num dicionário só
                    # Isso facilita para a função salvar sem precisar criar muitos argumentos novos
                    dados_perfil_completo = {
                        # Demográfico
                        "sexo": sexo,
                        "faixa_etaria": idade_faixa,
                        "escolaridade": escolaridade,
                        "area": area_atuacao,
                        # Técnico (Novos!)
                        "tec_freq_ai": freq_ai,
                        "tec_nivel_dados": nivel_dados,
                        "tec_nivel_viz": nivel_viz,
                        "tec_prog": conhece_prog
                    }
                    
                    detalhes_cenarios = {
                        "C1_Bloqueio": c1_resp,
                        "C2_Demo": c2_resp,
                        "C3_Geo": c3_resp,
                        "C4_Evolucao": c4_resp,
                        "C5_Codigo": c5_resp
                    }
                    
                    # Salva no Pinecone
                    salvou = salvar_feedback_pinecone(
                        usuario=nome_feedback,
                        estrelas=nota_final,
                        comentario=comentario,
                        dados_demograficos=dados_perfil_completo, # Passamos tudo aqui
                        detalhes_tecnicos=detalhes_cenarios
                    )
                    
                    if salvou:
                        st.balloons()
                        st.success("Pesquisa enviada com sucesso! Muito obrigado.")
                        time.sleep(2)
                        st.rerun()
                else:
                    st.error("Erro: Sistema de logs desativado.")

st.divider()
st.caption("LABVIS - UFPA © 2025")