import os
import time
import uuid
from datetime import datetime
from pinecone import Pinecone
from dotenv import load_dotenv

# Carrega variáveis
load_dotenv()

# Configurações
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_LOG")
NAMESPACE_LOGS = "app-logs" 
DIMENSION = 1024 

def get_dummy_vector():
    """
    Retorna um vetor válido (não-zero) para servir de placeholder.
    Preenchemos com 0.01 para não ser rejeitado pelo Pinecone.
    """
    return [0.01] * DIMENSION

def salvar_log_pinecone(usuario, input_usuario, output_ia, status="Sucesso"):
    """
    Salva a interação no Pinecone usando Metadata.
    """
    if not PINECONE_API_KEY or not INDEX_NAME:
        print("⚠️ Configuração do Pinecone ausente. Log não salvo.")
        return False

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)

        # 1. Cria ID único
        log_id = f"log_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # 2. Prepara Metadata
        metadata = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": str(usuario),
            "input_prompt": str(input_usuario),
            "output_resumo": str(output_ia)[:2000], 
            "status": status,
            "tipo": "log_sistema"
        }

        # 3. Cria Vetor Válido (Não-Zero)
        # --- CORREÇÃO AQUI ---
        vector_valido = get_dummy_vector()
        # ---------------------

        # 4. Upsert no Namespace de Logs
        index.upsert(
            vectors=[(log_id, vector_valido, metadata)],
            namespace=NAMESPACE_LOGS
        )
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar log no Pinecone: {e}")
        return False

def ler_ultimos_logs(limit=10):
    """
    Busca os logs usando o mesmo vetor dummy como referência.
    """
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        
        # Usa o mesmo vetor de 0.01 para buscar os vizinhos (logs)
        vector_consulta = get_dummy_vector()
        
        results = index.query(
            vector=vector_consulta,
            top_k=limit,
            include_metadata=True,
            namespace=NAMESPACE_LOGS
        )
        
        logs = []
        for match in results.get('matches', []):
            if match.get('metadata'):
                logs.append(match['metadata'])
        
        # Ordena por timestamp (mais recente primeiro) se possível
        # (O Pinecone retorna por similaridade, mas como todos são iguais, a ordem pode variar)
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        return logs
    except Exception as e:
        print(f"Erro ao ler logs: {e}")
        return []