from crewai import Crew 
from app.models import ChartOutput  # Importa Pydantic de saída
from app.crew import StoryVisCrew    # Importa a classe principal da crew

def run_storyvis_crew(
    user_prompt: str, 
    llm_choice: str, 
    file_path: str | None = None
) -> ChartOutput:
    """
    Instancia e executa a StoryVisCrew para gerar uma visualização.
    
    Args:
        user_prompt: O prompt em linguagem natural do usuário.
        llm_choice: A string que identifica o LLM (ex: 'gemini', 'openai').
        file_path: O caminho opcional para o arquivo de dados (CSV, XLS).

    Returns:
        Um objeto ChartOutput (Pydantic) estruturado com o resultado final.
    """
    
    print(f"--- [CrewRunner] Iniciando StoryVisCrew ---")
    print(f"--- [CrewRunner] LLM Escolhido: {llm_choice} ---")
    print(f"--- [CrewRunner] Prompt: {user_prompt[:50]}... ---")
    print(f"--- [CrewRunner] Arquivo: {file_path} ---")

    # 1. Instancia a Classe da Crew
    # O __init__ da StoryVisCrew já configura o LLM e as ferramentas
    crew_class = StoryVisCrew(llm_choice=llm_choice)
    
    # 2. Obtém a instância da Crew pronta para rodar
    crew_instance: Crew = crew_class.crew()
    
    # 3. Define as entradas
    # As chaves 'user_prompt' e 'data_path' devem corresponder
    # às variáveis que você usará no template do seu tasks.yaml
    inputs = {
        'user_prompt': user_prompt,
        'data_path': file_path
    }
    
    # 4. Executa a Crew (Kickoff)
    # O kickoff executa todas as tarefas na ordem SEQUENTIAL.
    # Como a última tarefa tem 'output_pydantic', o 'result'
    # final terá um atributo .pydantic
    result = crew_instance.kickoff(inputs=inputs)
    
    if not hasattr(result, 'pydantic') or not isinstance(result.pydantic, ChartOutput):
        print(f"--- [CrewRunner] ERRO: A saída da crew não foi um Pydantic model 'ChartOutput'.")
        print(f"--- [CrewRunner] Saída Recebida: {result} ---")
        # Você pode querer levantar um erro aqui ou retornar um ChartOutput de erro
        raise TypeError("A saída final da crew não foi o modelo Pydantic 'ChartOutput' esperado.")

    print(f"--- [CrewRunner] Execução concluída com sucesso. ---")
    
    # 5. O resultado final é o Pydantic Object da última Task
    return result.pydantic