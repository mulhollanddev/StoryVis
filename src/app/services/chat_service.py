# src/app/services/chat_service.py
# ---------------------------------
# Este serviço lida com chamadas de LLM simples e conversacionais
# que não precisam da complexidade (e custo) da Crew inteira.

import os
from crewai import LLM
# Reutilizamos a função LLMRequest para manter a configuração do LLM centralizada
from src.app.crew import LLMRequest 

def get_chatbot_response(llm_choice: str, chat_history: list, user_prompt: str):
    """
    Chama um LLM simples (fora do crewai) para uma conversa.
    """
    try:
        # 1. Configura o LLM que o usuário escolheu
        llm = LLMRequest(llm_choice)
        
        # 2. Define o "cérebro" do chatbot
        system_prompt = """
        Você é o "StoryVis", um assistente de IA amigável e prestativo.
        Seu principal objetivo é conversar com o usuário, dar boas-vindas 
        e ajudá-lo a se preparar para criar um dashboard. 
        
        IMPORTANTE: Se o usuário ainda não enviou um arquivo, seu trabalho
        é lembrá-lo gentilmente que, para começar a gerar os gráficos,
        ele precisa primeiro fazer o upload de um arquivo (CSV ou XLSX) 
        na barra lateral.
        
        Seja breve, amigável e foque na tarefa de preparar o usuário.
        """
        
        # 3. Monta o prompt como uma única string
        full_prompt = system_prompt + "\n\n--- Histórico da Conversa ---\n"
        
        for msg in chat_history:
            if "content" in msg:
                # Evita duplicar o prompt atual no histórico
                if msg["role"] == "user" and msg["content"] == user_prompt:
                    continue
                full_prompt += f"{msg['role']}: {msg['content']}\n"
        
        # Adiciona o novo prompt do usuário
        full_prompt += f"user: {user_prompt}\n"
        full_prompt += "assistant: " # Pede ao LLM para completar a resposta

        # --- CORREÇÃO AQUI ---
        # 4. Chama o LLM usando .run() (o método legado para strings)
        # .chat() e .invoke() estavam incorretos para este objeto.
        response = llm.call(full_prompt)
        
        # O resultado do .run() é diretamente uma string
        return response

    except Exception as e:
        # Retorna o erro real para debugarmos
        return f"Desculpe, tive um problema para processar sua mensagem: {e}"