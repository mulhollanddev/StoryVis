# src/app/models.py
# -----------------
# Define os modelos de dados Pydantic usados para validação de entrada/saída
# dos LLMs e para a resposta final da API.

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# -----------------------------------------------------------
# Modelos Internos (Usados para comunicação entre Agentes)
# -----------------------------------------------------------

class AnalysisBrief(BaseModel):
    """
    Modelo para o "Analysis Brief" (output da task_analyze_input).
    Estrutura os dados analisados e a intenção do usuário.
    """
    status_validacao: bool = Field(
        ...,
        description="True se os dados (arquivo) foram lidos e validados com sucesso."
    )
    schema_dados: Dict[str, str] = Field(
        ...,
        description="Um dicionário mapeando nome da coluna ao seu tipo de dado (ex: {'coluna_A': 'nominal'})."
    )
    resumo_estatistico: str = Field(
        ...,
        description="Um breve resumo estatístico ou semântico dos dados."
    )
    intencao_clarificada: str = Field(
        ...,
        description="A intenção do usuário para a visualização, clarificada pelo agente."
    )
    dataframe_head_json: str = Field(
        ...,
        description="Amostra (head) do dataframe, serializada como uma string JSON."
    )


class VizAxis(BaseModel):
    """Sub-modelo para definir um eixo (X ou Y) no VizPlan."""
    field: str = Field(..., description="O nome da coluna (campo) a ser usada no eixo.")
    type: str = Field(..., description="O tipo de dado Altair (ex: 'nominal', 'quantitative', 'temporal').")
    title: Optional[str] = Field(None, description="O título customizado para o eixo.")

class VizColor(BaseModel):
    """Sub-modelo para definir a codificação de cor no VizPlan."""
    field: str = Field(..., description="O nome da coluna (campo) a ser usada para a cor.")
    type: str = Field(..., description="O tipo de dado Altair (ex: 'nominal', 'quantitative').")
    title: Optional[str] = Field(None, description="O título customizado para a legenda de cor.")


class VizPlan(BaseModel):
    """
    Modelo para o "VizPlan" (output da task_plan_visualization).
    Define a especificação declarativa completa para o gráfico Altair.
    """
    chart_type: str = Field(
        ..., 
        description="O tipo principal de gráfico (ex: 'bar', 'line', 'scatter', 'heatmap')."
    )
    title: str = Field(
        ..., 
        description="O título narrativo para o gráfico."
    )
    x_axis: VizAxis = Field(
        ..., 
        description="A definição do eixo X."
    )
    y_axis: VizAxis = Field(
        ..., 
        description="A definição do eixo Y."
    )
    color: Optional[VizColor] = Field(
        None, 
        description="A definição (opcional) da codificação de cor."
    )
    tooltip: List[str] = Field(
        default_factory=list, 
        description="Lista de colunas a serem exibidas no tooltip interativo."
    )
    interactive: bool = Field(
        True, 
        description="Flag para habilitar interações (zoom, pan)."
    )
    justification: str = Field(
        ..., 
        description="A justificativa (baseada em 'Storytelling com Dados') para a escolha deste gráfico."
    )

# -----------------------------------------------------------
# Modelo de Saída (Usado para a resposta da API)
# -----------------------------------------------------------

class ChartOutput(BaseModel):
    """
    Define o modelo de saída final da API (output da task_evaluate_and_refine).
    Este é o objeto retornado pelo endpoint /gerar-grafico.
    """
    final_code: str = Field(
        ...,
        description="O bloco de código Python (usando Altair) final e executável para gerar o gráfico.",
        json_schema_extra={"example": "import altair as alt\n\nchart = alt.Chart(df).mark_bar()..."}
    )
    evaluation_report: str = Field(
        ...,
        description="Relatório de avaliação (em markdown) com sugestões de refinamento baseadas no RAG.",
        json_schema_extra={"example": "Avaliação: O gráfico atende aos requisitos. Sugestão: Mover a legenda..."}
    )
    
    # Opcional: Incluir o VizPlan para depuração no frontend
    viz_plan_json: Optional[str] = Field(
        None,
        description="O VizPlan (serializado como string JSON) que foi usado para gerar o código."
    )