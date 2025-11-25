from pydantic import BaseModel, Field

class DashboardOutput(BaseModel):
    """
    Estrutura de saída final do CrewAI para o Streamlit.
    """
    narrative: str = Field(
        ..., 
        description="O texto explicativo e analítico (storytelling) em formato Markdown."
    )
    dashboard_code: str = Field(
        ..., 
        description="O código Python (usando Altair e Streamlit) para gerar os gráficos. "
                    "NÃO inclua 'st.set_page_config'. Assuma que a variável 'df' já existe."
    )