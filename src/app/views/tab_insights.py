import streamlit as st

def render_tab_insights():
    st.subheader("Narrativa Técnica")
    if st.session_state["narrativa_final"]:
        with st.container(border=True):
            st.markdown(st.session_state["narrativa_final"])
    else:
        st.info("O relatório da Gramática dos Gráficos aparecerá aqui.")