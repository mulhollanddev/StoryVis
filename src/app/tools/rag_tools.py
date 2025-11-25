# rag_tools.py
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import torch

# ------------------------------------------------------
# Carrega configs
# ------------------------------------------------------
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
NAMESPACE = "knowledge-base"
DIMENSION = 768

# ------------------------------------------------------
# Inicializa Pinecone e modelo
# ------------------------------------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

device = "cuda" if torch.cuda.is_available() else "cpu"
embed_model = SentenceTransformer("BAAI/bge-base-en-v1.5", device=device)

# ------------------------------------------------------
# Função genérica de consulta ao Pinecone
# ------------------------------------------------------
def consultar_rag(query: str, top_k=5):
    """
    Converte a query em embedding e busca nos documentos armazenados.
    """
    emb = embed_model.encode(query, normalize_embeddings=True).tolist()

    results = index.query(
        vector=emb,
        top_k=top_k,
        include_metadata=True,
        namespace=NAMESPACE
    )

    trechos = []
    for match in results.get("matches", []):
        texto = match["metadata"].get("text", "")
        arquivo = match["metadata"].get("source", "")
        score = match.get("score", 0)

        trechos.append(
            f"Fonte: {arquivo} | Score: {score:.3f}\n{texto}\n"
        )

    return "\n\n---\n\n".join(trechos) if trechos else "Nenhum resultado encontrado."


# ------------------------------------------------------
# TOOL 1 → Rag para Storyteller
# ------------------------------------------------------
def storyteller_rag_tool():
    """
    Tool usada pelo agente Storyteller para consultar conteúdos sobre:
    - boas práticas de narrativa
    - construção de storytelling visual
    - princípios de análise visual
    """
    def run(query: str):
        return consultar_rag(query)

    return {
        "name": "storyteller_rag_lookup",
        "description": (
            "Consulta conteúdos da base de conhecimento relacionados a "
            "storytelling, narrativa visual e boas práticas de explicar gráficos."
        ),
        "func": run,
    }


# ------------------------------------------------------
# TOOL 2 → Rag para UI Builder
# ------------------------------------------------------
def ui_builder_rag_tool():
    """
    Tool usada pelo agente UI Builder para consultar conteúdos sobre:
    - layout de dashboards
    - boas práticas de UI/UX
    - organização visual
    - componentes adequados no Streamlit
    """
    def run(query: str):
        return consultar_rag(query)

    return {
        "name": "ui_builder_rag_lookup",
        "description": (
            "Consulta conteúdos da base de conhecimento relacionados a "
            "UI/UX, design de dashboards, layout e boas práticas visuais."
        ),
        "func": run,
    }
