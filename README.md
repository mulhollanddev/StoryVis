# StoryVis 🤖📊

**StoryVis** é uma aplicação inteligente de Business Intelligence que transforma dados brutos (CSV/XLSX) em dashboards interativos e narrativas de dados (Data Storytelling) de forma automatizada, utilizando o poder de Agentes de IA (CrewAI).

## 🚀 Funcionalidades

- **Ingestão Automática de Dados**: Carregamento e validação de arquivos CSV e Excel.
- **Tabela Editável**: Visualize e edite seus dados diretamente na aplicação antes da análise.
- **Análise Inteligente**: Agentes de IA analisam os dados para extrair insights relevantes.
- **Geração de Visualizações**: Criação automática de gráficos interativos usando Altair.
- **Editor de Código Vivo**: Visualize e edite o código Python gerado pela IA em tempo real.
- **Data Storytelling**: Geração de narrativas textuais que explicam os dados em linguagem natural.
- **Dashboard Dinâmico**: Interface organizada em abas para Dados, Dashboard/Editor e Insights.
- **RAG (Retrieval-Augmented Generation)**: Uso de base de conhecimento para aplicar melhores práticas de design e storytelling.

## 🧠 Arquitetura de Agentes (CrewAI)

O sistema foi otimizado para operar com uma equipe enxuta e eficiente de agentes:

1.  **Storyteller**: Analisa os dados e cria uma narrativa envolvente, destacando pontos chave e insights de negócio.
2.  **Dashboard Developer**: Recebe a narrativa e os dados para projetar e implementar o código do gráfico (Altair) mais adequado.

## 🛠️ Instalação

### Pré-requisitos

- Python 3.10+
- Chave de API da Groq (para o modelo LLM `llama-3.1-8b-instant` ou similar)

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/storyvis.git
    cd storyvis
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # venv\Scripts\activate   # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto e adicione sua chave da Groq:
    ```env
    GROQ_API_KEY=sua_chave_aqui
    ```

## ▶️ Como Usar

1.  **Inicie a aplicação:**
    ```bash
    streamlit run app.py
    ```

2.  **Interaja com as Abas:**
    - **✏️ Dados & Configuração**: Faça upload do seu arquivo (CSV/XLSX), visualize e edite os dados se necessário.
    - **📈 Dashboard & Código**: Peça para a IA gerar um gráfico (ex: "Vendas por região"). Veja o gráfico gerado e o código fonte lado a lado. Você pode ajustar o código manualmente e reaplicar!
    - **📝 Narrativa de Insights**: Leia a explicação detalhada e o storytelling gerado pela IA sobre os dados visualizados.

## 📂 Estrutura do Projeto

```
StoryVis/
├── app.py                  # Aplicação principal Streamlit
├── requirements.txt        # Dependências do projeto
├── src/
│   ├── app/
│   │   ├── crew.py         # Orquestração da CrewAI (Storyteller & Dashboard Developer)
│   │   ├── config/         # Configurações dos Agentes e Tarefas (YAML)
│   │   ├── services/       # Lógica de RAG e Modelos
│   │   └── tools/          # Ferramentas personalizadas
│   └── logs/               # Logs de execução
└── knowledge/              # Base de conhecimento para o RAG
```

## 🤝 Contribuição

Sinta-se à vontade para abrir issues e pull requests para melhorias no projeto.

---
Desenvolvido com ❤️ usando [CrewAI](https://crewai.com) e [Streamlit](https://streamlit.io).
