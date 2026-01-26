import streamlit as st
import uuid
import sys
import os

# ===============================================
# Configuração da Página
# ===============================================
st.set_page_config(page_title="StoryVis", layout="wide", page_icon="📊")

# --- Importações Locais ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports de Views e Utils
try:
    from src.app.utils import inicializar_session_state
    from src.app.demo import carregar_demo_inicial
    
    # Importando as Views que acabamos de criar
    from src.app.views.tab_dados import render_tab_dados
    from src.app.views.tab_dashboard import render_tab_dashboard
    from src.app.views.tab_insights import render_tab_insights
    from src.app.views.tab_feedback import render_tab_feedback
    from src.app.views.onboarding import verificar_onboarding, botao_ajuda_sidebar
    from src.app.views.tab_resultados import render_tab_resultados # <--- NOVO IMPORT
    
    LOGGING_ATIVO = True
except ImportError as e:
    st.error(f"Erro crítico de importação: {e}")
    st.stop()

# ===============================================
# Gestão de Estado Global
# ===============================================
if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"sess_{uuid.uuid4().hex[:12]}"

if "interaction_step" not in st.session_state:
    st.session_state["interaction_step"] = 0

if "buffer_logs_tecnicos" not in st.session_state:
    st.session_state["buffer_logs_tecnicos"] = []

if "codigo_calculo" not in st.session_state:
    st.session_state["codigo_calculo"] = ""

inicializar_session_state(carregar_demo_inicial)

# ===============================================
# Interface Principal
# ===============================================
st.title("📊 StoryVis: Analytics com IA")

# --- 1. CHAMADA DO ONBOARDING (Coloque logo após o título) ---
verificar_onboarding()


# Definição das Abas
tab_dados, tab_dash, tab_insights, tab_feedback, tab_admin = st.tabs([
    "✏️ Dados & Configuração", 
    "📈 Dashboard", 
    "📝 Sobre os gráficos",
    "🗣️ Feedback",
    "🔐 "
])

# Renderização do Conteúdo de Cada Aba
with tab_dados:
    render_tab_dados()

with tab_dash:
    render_tab_dashboard(logging_ativo=LOGGING_ATIVO)

with tab_insights:
    render_tab_insights()

with tab_feedback:
    render_tab_feedback(logging_ativo=LOGGING_ATIVO)

with tab_admin:
    # Dica de segurança simples: só mostra se você quiser, ou pode deixar aberto
    render_tab_resultados()

st.divider()
st.caption("LABVIS - UFPA © 2026")