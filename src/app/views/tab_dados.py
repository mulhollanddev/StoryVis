import streamlit as st
import pandas as pd
import time
from src.app.utils import carregar_dados, buscar_coordenadas_ia, detectar_coluna_geo_ia
from src.app.demo import carregar_demo_inicial

def render_tab_dados():
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

    # --- Inteligência Geográfica ---
    df_atual = st.session_state["df_final"]
    col_geo_sugerida = detectar_coluna_geo_ia(df_atual)

    if col_geo_sugerida:
        locais_unicos = df_atual[col_geo_sugerida].dropna().unique().tolist()
        qtd_locais = len(locais_unicos)
        LIMITE_MAXIMO = 30
        
        st.warning(f"📍 **Inteligência Geográfica:** Detectamos a coluna `{col_geo_sugerida}` com **{qtd_locais}** locais únicos.", icon="🌍")
        
        with st.expander("🌍 Clique aqui para utilizar Inteligência Geográfica e gerar mapas"):
            st.markdown("<small>A IA irá buscar Latitude, Longitude e Códigos de Área.</small>", unsafe_allow_html=True)
            st.write("") 
            
            if qtd_locais > LIMITE_MAXIMO:
                st.error(f"⚠️ Limite excedido ({qtd_locais}/{LIMITE_MAXIMO}). Filtre os dados.")
            else:
                if st.button("✨ Iniciar Mapeamento Automático", type="primary", use_container_width=True):
                    with st.status(f"🤖 IA analisando {qtd_locais} locais...", expanded=True) as status:
                        coords = buscar_coordenadas_ia(locais_unicos)
                        if coords:
                            df_temp = df_atual.copy()
                            def get_safe(local, key):
                                d = coords.get(local)
                                return d.get(key) if isinstance(d, dict) else None

                            df_temp['Latitude'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'lat'))
                            df_temp['Longitude'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'lon'))
                            df_temp['geo_code'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'geo_code'))
                            df_temp['country_iso'] = df_temp[col_geo_sugerida].apply(lambda x: get_safe(x, 'country_iso'))
                            
                            # Limpeza Numérica
                            df_temp['Latitude'] = pd.to_numeric(df_temp['Latitude'], errors='coerce')
                            df_temp['Longitude'] = pd.to_numeric(df_temp['Longitude'], errors='coerce')
                            df_temp['geo_code'] = df_temp['geo_code'].fillna('').astype(str).replace({'nan': '', 'None': ''})
                            df_temp['country_iso'] = df_temp['country_iso'].fillna('').astype(str).replace({'nan': '', 'None': ''})
                            
                            st.session_state["df_final"] = df_temp
                            status.update(label="✅ Mapeamento concluído!", state="complete")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro na geocodificação.")

    # --- Tabela ---
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

    df_editado = st.data_editor(st.session_state["df_final"], width="stretch", num_rows="dynamic", key="main_data_editor")
    st.session_state["df_final"] = df_editado