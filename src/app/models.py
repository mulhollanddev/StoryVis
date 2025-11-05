# src/app/models.py
# -----------------
# Define os modelos de dados Pydantic usados para validação e comunicação
# entre os agentes (contratos de dados) e para a saída final da crew.

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# -----------------------------------------------------------
# Modelo 1: Saída do 'data_analyst'
# -----------------------------------------------------------

class AnalysisBrief(BaseModel):
    """
    Pacote de dados do 'data_analyst' para o 'dashboard_architect'.
    Contém os dados limpos e o resumo estatístico.
    """
    status_validacao: bool = Field(
        ...,
        description="True se os dados (arquivo) foram lidos e validados com sucesso."
    )
    schema_dados: Dict[str, str] = Field(
        ...,
        description="Dicionário mapeando nome da coluna ao seu tipo (ex: {'Vendas': 'quantitative'})."
    )
    resumo_estatistico: str = Field(
        ...,
        description="Um breve resumo estatístico ou semântico dos dados."
    )
    intencao_clarificada: str = Field(
        ...,
        description="A interpretação do agente sobre o que o usuário quer fazer (ex: 'Comparar Vendas por Região')."
    )
    # Os dados limpos, prontos para serem embutidos no JSON do Altair
    dados_limpos_json: str = Field(
        ...,
        description="Os dados limpos serializados como uma string JSON (formato 'records')."
    )


# -----------------------------------------------------------
# Modelo 2: Saída do 'dashboard_architect'
# -----------------------------------------------------------

class VizEncoding(BaseModel):
    """Sub-modelo para definir um eixo (X, Y) ou canal (Cor, Tooltip)."""
    field: str = Field(..., description="O nome da coluna (campo) a ser usada.")
    type: str = Field(..., description="O tipo de dado Altair (ex: 'nominal', 'quantitative', 'temporal').")
    title: Optional[str] = Field(None, description="O título customizado para o eixo.")

class VizInteraction(BaseModel):
    """Sub-modelo para definir uma interação (filtro, seleção)."""
    type: str = Field(..., description="Tipo de interação (ex: 'brushing', 'dropdown_filter').")
    name: str = Field(..., description="Nome da seleção (ex: 'filtro_regiao').")
    field: Optional[str] = Field(None, description="Campo ao qual o filtro se aplica.")

class VizComponent(BaseModel):
    """Sub-modelo para definir um único gráfico dentro do dashboard."""
    title: str = Field(..., description="O título para este gráfico específico.")
    chart_type: str = Field(..., description="O 'mark' do Altair (ex: 'bar', 'line', 'point').")
    x_axis: VizEncoding
    y_axis: VizEncoding
    color: Optional[VizEncoding] = None
    tooltip: List[str] = Field(default_factory=list, description="Campos para o tooltip.")

class DashboardPlan(BaseModel):
    """
    A 'planta' (blueprint) do 'dashboard_architect' para o 'viz_generator'.
    Descreve um dashboard completo com múltiplos gráficos e interações.
    """
    dashboard_title: str = Field(..., description="O título principal para todo o dashboard.")
    
    # Suporta "Visualização Composta"
    componentes: List[VizComponent] = Field(
        ...,
        description="Uma lista de todos os gráficos que compõem o dashboard."
    )
    
    # Suporta "Filtros Dinâmicos"
    interacoes: Optional[List[VizInteraction]] = Field(
        None,
        description="Uma lista de interações (filtros) que conectam os gráficos."
    )
    layout: str = Field(
        "vconcat",
        description="Como organizar os componentes (ex: 'vconcat', 'hconcat')."
    )
    justificativa: str = Field(
        ...,
        description="A explicação (XAI) do Arquiteto sobre POR QUE este design foi escolhido."
    )


# -----------------------------------------------------------
# Modelo 3: Saída Final da Crew (Montado pelo 'viz_manager')
# -----------------------------------------------------------

class ChartOutput(BaseModel):
    """
    Define o pacote de entrega final da Crew para o Streamlit (app.py).
    """
    
    # --- A MUDANÇA CRÍTICA ---
    final_code: str = Field(
        ...,
        description="A especificação JSON COMPLETA do Altair (NÃO é código Python). "
                    "Esta string JSON é usada diretamente com 'alt.Chart.from_json()'.",
        json_schema_extra={"example": "{ \"data\": ..., \"mark\": \"bar\", ... }"}
    )
    # --- FIM DA MUDANÇA ---
    
    evaluation_report: str = Field(
        ...,
        description="A narrativa em Markdown (do 'narrative_generator') explicando o "
                    "dashboard para o usuário.",
        json_schema_extra={"example": "# Análise do seu Dashboard\n\nNotei que..."}
    )
    
    viz_plan_json: Optional[str] = Field(
        None,
        description="O 'DashboardPlan' original (serializado como string JSON) "
                    "usado para gerar o gráfico, para fins de log e debug."
    )