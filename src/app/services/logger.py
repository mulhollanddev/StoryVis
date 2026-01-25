import os
import time
import uuid
import json
from datetime import datetime
from pinecone import Pinecone
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_LOG")
NAMESPACE_LOGS = "app-logs" 

# Dimensão do seu índice (conforme seu erro anterior)
DIMENSION = 1024 

def get_dummy_vector():
    """
    Retorna um vetor válido (não-zero) para servir de placeholder.
    Preenchemos com 0.01 para não ser rejeitado pelo Pinecone.
    """
    return [0.01] * DIMENSION

def salvar_sessao_completa(session_id, usuario, feedback_data, logs_buffer):
    """
    Consolida Feedback + Perfil + Histórico de Ações em um ÚNICO registro no Pinecone.
    """
    if not PINECONE_API_KEY or not INDEX_NAME:
        print("⚠️ Erro: Configurações do Pinecone ausentes.")
        return False

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)

        # O ID do registro é o ID da Sessão (único por visita)
        record_id = str(session_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Monta os Metadados "Planos" (Para filtros e gráficos no BI)
        metadata = {
            "record_type": "sessao_consolidada",
            "session_id": str(session_id),
            "timestamp": timestamp,
            "usuario": str(usuario),
            
            # --- Dados do Feedback ---
            "nota_estrelas": int(feedback_data.get("estrelas", 0)),
            "comentario": str(feedback_data.get("comentario", ""))[:1000],
            
            # --- Dados Demográficos (Achatados) ---
            "demo_sexo": str(feedback_data.get("sexo", "N/A")),
            "demo_idade": str(feedback_data.get("faixa_etaria", "N/A")),
            "demo_escolaridade": str(feedback_data.get("escolaridade", "N/A")),
            "demo_area": str(feedback_data.get("area", "N/A")),
            
            # --- Dados Técnicos (Perfil) ---
            "tec_nivel_dados": str(feedback_data.get("tec_nivel_dados", "N/A")),
            "tec_nivel_viz": str(feedback_data.get("tec_nivel_viz", "N/A")),
            "tec_freq_ai": str(feedback_data.get("tec_freq_ai", "N/A")),
            "tec_prog": str(feedback_data.get("tec_prog", "N/A")),
            
            # --- Checklist de Testes ---
            "teste_bloqueio": str(feedback_data.get("checklist", {}).get("C1_Bloqueio", "N/A")),
            "teste_demo": str(feedback_data.get("checklist", {}).get("C2_Demo", "N/A")),
            "teste_geo": str(feedback_data.get("checklist", {}).get("C3_Geo", "N/A")),
            "teste_evolucao": str(feedback_data.get("checklist", {}).get("C4_Evolucao", "N/A")),
            "teste_codigo": str(feedback_data.get("checklist", {}).get("C5_Codigo", "N/A")),

            # --- Resumo da Sessão ---
            "qtd_interacoes": len(logs_buffer),
            "tempo_total_gasto": sum([log.get('execution_time', 0) for log in logs_buffer])
        }

        # 2. Guarda o Histórico Completo como JSON String
        # (Isso permite salvar vários gráficos dentro de um único metadata)
        historico_json = json.dumps(logs_buffer, ensure_ascii=False)
        
        # Pinecone tem limite de 40KB por metadado. Vamos cortar se for gigante.
        if len(historico_json) > 38000:
            metadata["full_history_json"] = historico_json[:19000] + "...[CORTADO]..." + historico_json[-19000:]
            metadata["history_truncated"] = "True"
        else:
            metadata["full_history_json"] = historico_json
            metadata["history_truncated"] = "False"

        # 3. Envia para o Pinecone
        vector_valido = get_dummy_vector()
        index.upsert(
            vectors=[(record_id, vector_valido, metadata)],
            namespace=NAMESPACE_LOGS
        )
        
        print(f"✅ Sessão {record_id} consolidada com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar sessão completa: {e}")
        return False