import os
import uuid
import time
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader # Nova importação para PDFs
import torch
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()
# --- CONFIGURAÇÕES ---
PASTA_ARQUIVOS = "knowledge" # Nome da sua pasta
DIMENSION = 768 

# Configurações de Nuvem
CLOUD_PROVIDER = "aws"
REGION = "us-east-1"

# --- INICIALIZAÇÃO (Igual ao anterior) ---
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
existing_indexes = [index.name for index in pc.list_indexes()]

if os.getenv("PINECONE_INDEX_NAME") not in existing_indexes:
    print(f"Criando index '{os.getenv("PINECONE_INDEX_NAME")}'...")
    pc.create_index(
        name=os.getenv("PINECONE_INDEX_NAME"), dimension=DIMENSION, metric="cosine",
        spec=ServerlessSpec(cloud=CLOUD_PROVIDER, region=REGION)
    )
    time.sleep(10)

index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('BAAI/bge-base-en-v1.5', device=device)

# --- NOVAS FUNÇÕES DE LEITURA E CHUNKING ---

def ler_arquivo_pdf(caminho):
    """Extrai texto de PDF página por página"""
    try:
        reader = PdfReader(caminho)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        print(f"Erro ao ler PDF {caminho}: {e}")
        return ""

def processar_pasta(pasta):
    """Lê todos os arquivos suportados na pasta"""
    conteudos = []
    
    if not os.path.exists(pasta):
        print(f"❌ A pasta '{pasta}' não existe! Crie a pasta e coloque seus arquivos.")
        return []

    print(f"📂 Lendo arquivos da pasta '{pasta}'...")

    for nome_arquivo in os.listdir(pasta):
        caminho_completo = os.path.join(pasta, nome_arquivo)
        
        texto_bruto = ""
        
        # Identifica a extensão e escolhe como ler
        if nome_arquivo.endswith(".pdf"):
            texto_bruto = ler_arquivo_pdf(caminho_completo)
        elif nome_arquivo.endswith(".txt") or nome_arquivo.endswith(".md"):
            with open(caminho_completo, "r", encoding="utf-8") as f:
                texto_bruto = f.read()
        else:
            print(f"⚠️ Pulando arquivo não suportado: {nome_arquivo}")
            continue
            
        if texto_bruto:
            # Adiciona o texto bruto e o nome do arquivo (fonte)
            conteudos.append({"texto": texto_bruto, "arquivo": nome_arquivo})
            print(f"   ✅ Lido: {nome_arquivo} ({len(texto_bruto)} caracteres)")

    return conteudos

def criar_chunks(texto, tamanho=1000, overlap=200):
    """
    Divide o texto grande em pedaços menores.
    overlap: garante que o contexto não se perca no corte.
    """
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        # Avança menos que o tamanho total para criar sobreposição (overlap)
        inicio += (tamanho - overlap) 
    return chunks

# --- PROCESSO DE ENVIO ---

def main():
    # 1. Ler arquivos do disco
    dados_brutos = processar_pasta(PASTA_ARQUIVOS)
    
    if not dados_brutos:
        return

    vectors_to_upsert = []
    
    print("\n✂️  Criando chunks e gerando embeddings...")

    for item in dados_brutos:
        texto_original = item["texto"]
        nome_arquivo = item["arquivo"]
        
        # Divide o arquivo em pedaços
        pedacos = criar_chunks(texto_original)
        
        # Para cada pedaço, gera um vetor
        for i, pedaco in enumerate(pedacos):
            # Gera embedding
            vetor = model.encode(pedaco, normalize_embeddings=True).tolist()
            
            # Cria metadados úteis para o RAG depois
            metadata = {
                "text": pedaco,          # O trecho do texto
                "source": nome_arquivo,  # De qual arquivo veio
                "chunk_index": i         # Ordem do pedaço
            }
            
            # Adiciona à lista
            vectors_to_upsert.append({
                "id": str(uuid.uuid4()),
                "values": vetor,
                "metadata": metadata
            })

    # Envia em lotes (batches) para não sobrecarregar
    batch_size = 100
    print(f"\n🚀 Enviando {len(vectors_to_upsert)} vetores para o Pinecone...")
    
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i : i + batch_size]
        try:
            index.upsert(vectors=batch, namespace="knowledge-base")
            print(f"   Lote {i} a {i+len(batch)} enviado.")
        except Exception as e:
            print(f"❌ Erro no lote {i}: {e}")

    print("\n✨ Processo finalizado!")

if __name__ == "__main__":
    main()