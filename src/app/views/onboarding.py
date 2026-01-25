import streamlit as st

@st.dialog("👋 Bem-vindo ao StoryVis!")
def mostrar_tour_inicial():
    """
    Exibe um modal explicativo sobre como usar a ferramenta.
    """
    st.markdown("""
    Que bom ter você aqui! O **StoryVis** transforma seus dados em histórias visuais usando Inteligência Artificial.
    
    Aqui vai um guia rápido de como aproveitar ao máximo:
    """)
    
    # Criando abas dentro do modal para explicar cada seção
    tab1, tab2, tab3, tab4 = st.tabs(["✏️ Dados", "📈 Dashboard", "📝 Narrativa", "🗣️ Feedback"])
    
    with tab1:
        st.info("Passo 1: Comece aqui!")
        st.markdown("""
        * **Identifique-se:** Coloque seu nome.
        * **Upload:** Suba seu arquivo CSV ou Excel.
        * **Mapa Inteligente:** Se seus dados tiverem cidades, nossa IA detecta e cria mapas automáticos!
        """)
        st.image("https://placehold.co/600x200/EEE/31343C?text=Aba+Dados", caption="Configure tudo na primeira aba")

    with tab2:
        st.success("Passo 2: A Mágica Acontece")
        st.markdown("""
        * **Peça o que quiser:** Digite *"Mostre as vendas por estado"* ou *"Qual o produto mais caro?"*.
        * **Evolução:** Gostou do gráfico? Use o campo "Evoluir Dashboard" para adicionar mais visuais na mesma tela.
        * **Cálculos:** A IA também faz contas matemáticas para você.
        """)
    
    with tab3:
        st.warning("Passo 3: Entenda os Dados")
        st.markdown("""
        * Aqui geramos uma **Narrativa Técnica**.
        * Explicamos o "porquê" do gráfico e quais colunas foram usadas.
        * Ideal para copiar e colar em relatórios!
        """)
        
    with tab4:
        st.error("Passo 4: Sua Opinião")
        st.markdown("""
        * Ajude a ciência! 🧪
        * Responda nossa pesquisa rápida.
        * Seus dados ajudam a melhorar o StoryVis.
        """)

    st.divider()
    if st.button("🚀 Entendi, vamos começar!", type="primary", use_container_width=True):
        st.session_state["primeiro_acesso"] = False
        st.rerun()

def verificar_onboarding():
    """
    Função chamada no app.py para checar se deve abrir o tour.
    """
    # Se a variável não existe, é a primeira vez
    if "primeiro_acesso" not in st.session_state:
        st.session_state["primeiro_acesso"] = True

    # Se for true, abre o modal
    if st.session_state["primeiro_acesso"]:
        mostrar_tour_inicial()

def botao_ajuda_sidebar():
    """
    Coloca um botão na sidebar para rever o tour quando quiser.
    """
    if st.sidebar.button("❓ Como usar o sistema"):
        mostrar_tour_inicial()