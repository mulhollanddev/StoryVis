import pandas as pd

def carregar_demo_inicial():
    """Retorna os dados, código e narrativa do modo Demo."""
    df_fake = pd.DataFrame({
        "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "Produto": ["Smartphone", "Smartphone", "Laptop", "Laptop", "Tablet", "Tablet"],
        "Vendas": [1200, 1500, 3000, 3200, 800, 950],
        "Meta": [1000, 1000, 2500, 2500, 1000, 1000]
    })
    
    codigo_fake = """
import streamlit as st
import altair as alt
import pandas as pd

# Container para restringir largura
c = st.container()
with c:
    st.markdown("### 📈 Demonstração")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Mês', sort=None),
        y='Vendas',
        color='Produto',
        tooltip=['Mês', 'Produto', 'Vendas']
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
"""
    
    narrativa_fake = """
### 🚀 Demonstração Automática
Estes são dados de exemplo. Para começar a usar seus dados, vá na aba **Dados** e insira seu nome.
"""
    return df_fake, codigo_fake, narrativa_fake