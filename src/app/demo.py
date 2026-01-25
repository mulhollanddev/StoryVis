import pandas as pd
import random
from datetime import datetime, timedelta

def gerar_dados_demo(qtd_linhas=60):
    """
    Gera um DataFrame aleatório com dados de vendas e geolocalização real.
    """
    
    # 1. Base de Locais Reais (Para o mapa funcionar perfeitamente)
    # Inclui Cidade, Latitude, Longitude e a "Outra Coluna" (Estado/UF)
    locais_reais = [
        {"Cidade": "Belém", "Latitude": -1.4558, "Longitude": -48.4902, "Estado": "PA"},
        {"Cidade": "Santarém", "Latitude": -2.4430, "Longitude": -54.7081, "Estado": "PA"},
        {"Cidade": "Manaus", "Latitude": -3.1190, "Longitude": -60.0217, "Estado": "AM"},
        {"Cidade": "São Paulo", "Latitude": -23.5505, "Longitude": -46.6333, "Estado": "SP"},
        {"Cidade": "Rio de Janeiro", "Latitude": -22.9068, "Longitude": -43.1729, "Estado": "RJ"},
        {"Cidade": "Salvador", "Latitude": -12.9777, "Longitude": -38.5016, "Estado": "BA"},
        {"Cidade": "Brasília", "Latitude": -15.7801, "Longitude": -47.9292, "Estado": "DF"},
        {"Cidade": "Fortaleza", "Latitude": -3.7172, "Longitude": -38.5434, "Estado": "CE"},
        {"Cidade": "Curitiba", "Latitude": -25.4284, "Longitude": -49.2733, "Estado": "PR"},
        {"Cidade": "Recife", "Latitude": -8.0476, "Longitude": -34.8770, "Estado": "PE"},
        {"Cidade": "Porto Alegre", "Latitude": -30.0346, "Longitude": -51.2177, "Estado": "RS"},
        {"Cidade": "Belo Horizonte", "Latitude": -19.9167, "Longitude": -43.9345, "Estado": "MG"},
    ]

    produtos = [
        "Notebook Gamer", "Smartphone Pro", "Monitor 4K", 
        "Teclado Mecânico", "Mouse Sem Fio", "Tablet Gráfico", 
        "Cadeira Ergonômica", "Headset Noise-Cancel"
    ]

    canais = ["E-commerce", "Loja Física", "Marketplace", "Venda Direta"]

    dados = []
    
    # Data inicial (começo do ano atual)
    data_base = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0)

    for _ in range(qtd_linhas):
        # Sorteia um local real
        local = random.choice(locais_reais)
        
        # Sorteia produto e gera valores
        prod = random.choice(produtos)
        qtd = random.randint(1, 20)
        preco_unit = round(random.uniform(150.0, 5000.0), 2)
        total = round(qtd * preco_unit, 2)
        custo = round(total * random.uniform(0.4, 0.7), 2)
        lucro = round(total - custo, 2)
        
        # Sorteia data dentro dos últimos 365 dias
        dias_aleatorios = random.randint(0, 365)
        data_venda = data_base + timedelta(days=dias_aleatorios)

        dados.append({
            "Data": data_venda.strftime("%Y-%m-%d"),
            "Produto": prod,
            "Categoria": "Eletrônicos" if "Cadeira" not in prod else "Móveis",
            "Canal": random.choice(canais),
            "Quantidade": qtd,
            "Valor_Unitario": preco_unit,
            "Vendas": total,
            "Lucro": lucro,
            # --- COLUNAS GEOGRÁFICAS ---
            "Cidade": local["Cidade"],
            "Estado": local["Estado"],    # A "outra coluna" (GeoCode)
            "Latitude": local["Latitude"],
            "Longitude": local["Longitude"]
        })

    return pd.DataFrame(dados)

def carregar_demo_inicial():
    """
    Função chamada pelo app.py para carregar a demonstração.
    """
    # 1. Gera dados novos a cada chamada
    df = gerar_dados_demo(qtd_linhas=80)
    
    # 2. Define o código inicial (Exemplo fixo para o usuário ver)
    codigo_inicial = """
import streamlit as st
import pandas as pd
import altair as alt

# Dashboard de Vendas por Estado e Lucro
c1, c2 = st.columns(2)

with c1:
    st.metric("Total de Vendas", f"R$ {df['Vendas'].sum():,.2f}")

with c2:
    st.metric("Lucro Total", f"R$ {df['Lucro'].sum():,.2f}")

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Estado', sort='-y'),
    y='Vendas',
    color='Categoria',
    tooltip=['Cidade', 'Vendas', 'Lucro']
).properties(title="Vendas por Estado").interactive()

st.altair_chart(chart, use_container_width=True)

# Mapa Simples (Já que temos Lat/Lon)
st.map(df, latitude='Latitude', longitude='Longitude', size='Vendas')
"""

    # 3. Define a narrativa inicial
    narrativa_inicial = """
    ### 📊 Dados de Demonstração (Gerados Aleatoriamente)
    
    Estes dados representam vendas de varejo em diversas capitais brasileiras.
    
    **Colunas Disponíveis:**
    - **Geográficas:** Cidade, Estado, Latitude, Longitude.
    - **Financeiras:** Vendas, Lucro, Quantidade, Valor Unitário.
    - **Categorias:** Produto, Canal, Data.
    
    > **Dica:** Tente pedir: *"Crie um mapa de calor usando latitude e longitude"* ou *"Mostre a evolução das vendas no tempo"*.
    """

    return df, codigo_inicial, narrativa_inicial