import streamlit as st

# Configuração da página (deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Extração de Informações de Sites",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importações
import warnings
from dotenv import load_dotenv
import os
import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import tiktoken
import tempfile
import shutil
from pathlib import Path

# Suprimir avisos específicos
warnings.filterwarnings('ignore', message='.*torch.classes.*')
warnings.filterwarnings('ignore', category=UserWarning)

# Adicionar CSS customizado
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        padding-top: 0 !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    
    section[data-testid="stSidebarContent"] {
        padding-top: 0 !important;
    }
    
    [data-testid="stSidebarContent"] > div:first-child {
        margin-top: -4rem !important;
        padding-top: 0 !important;
    }
    
    [data-testid="stSidebarContent"] img {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    [data-testid="stImage"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Estilo metálico para botões */
    .stButton button {
        height: 45px;
        width: auto !important;
        min-width: 160px;
        background: linear-gradient(180deg, #1e3d59 0%, #0a1b2a 100%);
        border: 1px solid #2d5a8b;
        color: #89CFF0;
        text-shadow: 0 0 5px #89CFF0;
        font-weight: bold;
        font-size: 18px !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(30, 61, 89, 0.3);
        margin-left: 0 !important;
        padding: 0 30px;
        line-height: 1.2;
    }
    
    .stButton {
        display: flex;
        justify-content: flex-start;
        width: 100%;
    }
    
    .stButton > div {
        display: flex;
        justify-content: flex-start;
        width: auto !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(180deg, #2d5a8b 0%, #1e3d59 100%);
        color: #ADD8E6;
        text-shadow: 0 0 8px #ADD8E6;
        box-shadow: 0 0 15px rgba(45, 90, 139, 0.5);
        border: 1px solid #4d7ab1;
        font-size: 18.5px !important;
    }
    
    .stButton button:active {
        background: linear-gradient(180deg, #0a1b2a 0%, #1e3d59 100%);
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.3);
    }

    .stTextInput > div > div > input {
        height: 35px;
        margin-bottom: 10px;
    }
    .stButton button {
        height: 35px;
        width: 100%;
    }
    [data-testid="stSidebar"] {
        width: 320px !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 320px !important;
        padding-top: 0 !important;
    }
    section[data-testid="stSidebarContent"] {
        width: 320px !important;
        padding-top: 0 !important;
    }
    /* Centralização da imagem na barra lateral */
    [data-testid="stSidebarContent"] img {
        display: block;
        margin: 0 auto;
        margin-bottom: 20px;
    }
    .title-container {
        background-color: #1e3d59;
        padding: 20px;
        border-radius: 5px;
        margin: 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
        box-sizing: border-box;
    }
    /* Remover padding padrão do Streamlit */
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stAppViewContainer"] > section:first-child {
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] {
        width: 320px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 320px !important;
    }
    section[data-testid="stSidebarContent"] {
        width: 320px !important;
    }
    /* Centralização da imagem na barra lateral */
    [data-testid="stSidebarContent"] img {
        display: block;
        margin: 0 auto;
        margin-bottom: 20px;
    }
    .neon-title {
        color: #fff;
        text-align: center;
        font-size: 3.25em;
        font-weight: bold;
        text-shadow: 0 0 5px #fff,
                     0 0 10px #fff,
                     0 0 20px #0ff,
                     0 0 30px #0ff,
                     0 0 40px #0ff;
        animation: neon 1.5s ease-in-out infinite alternate;
    }
    [data-testid="stAppViewContainer"] > section:first-child {
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
    }
    [data-testid="stAppViewContainer"] > section:first-child > div:first-child {
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
    }
    [data-testid="stSidebarContent"] img {
        display: block;
        margin: 0 auto;
        margin-bottom: 20px;
    }
    @keyframes neon {
        from {
            text-shadow: 0 0 5px #fff,
                         0 0 10px #fff,
                         0 0 20px #0ff,
                         0 0 30px #0ff,
                         0 0 40px #0ff;
        }
        to {
            text-shadow: 0 0 2.5px #fff,
                         0 0 5px #fff,
                         0 0 10px #0ff,
                         0 0 15px #0ff,
                         0 0 20px #0ff;
        }
    }
    div[data-testid="stToolbar"] {
        visibility: hidden;
    }
    div[data-testid="stDecoration"] {
        visibility: hidden;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
    }
    #MainMenu {
        visibility: hidden;
    }
    header {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Título principal com efeito neon
st.markdown("""
    <div class="title-container">
        <h1 class="neon-title">🌐 Saas - Extração de informações de Sites</h1>
        <p style="color: #fff; text-align: center; font-size: 1.2em; margin-top: 10px; text-shadow: 0 0 5px #0ff;">
            Desenvolvido por Mauro de Souza Guimarães
        </p>
    </div>
""", unsafe_allow_html=True)

# Wrapper para o conteúdo principal
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Campo de entrada da URL e botão
url_input = st.text_input("URL do site:", key="url_input", help="Insira a URL do site que deseja analisar")
carregar_url = st.button("Carregar URL", use_container_width=False)

# Função para criar diretório temporário
def get_temp_dir():
    """Cria um diretório temporário único para esta sessão"""
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
    return st.session_state.temp_dir

# Função para limpar diretório temporário
def cleanup_temp_dir():
    """Limpa o diretório temporário"""
    if 'temp_dir' in st.session_state:
        try:
            shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)
            del st.session_state.temp_dir
        except Exception:
            pass

# Configuração do User-Agent e headers
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

def get_session():
    """Configurar uma sessão com retry e headers personalizados"""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(HEADERS)
    return session

# Classe customizada do WebLoader
class CustomWebLoader(WebBaseLoader):
    """Loader personalizado para carregar conteúdo de páginas web"""
    
    def __init__(self, web_path):
        super().__init__(web_path)
        self.session = get_session()

    def scrape(self):
        """Faz o scraping da página web"""
        response = self.session.get(self.web_path, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remover scripts e estilos
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        # Processar o texto para remover linhas em branco extras
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def load(self):
        """Carrega o conteúdo da página"""
        text = self.scrape()
        metadata = {"source": self.web_path}
        return [Document(page_content=text, metadata=metadata)]

# Definir o caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = os.path.join(BASE_DIR, "imagens", "LogoSL.jpg")

# Barra lateral para configuração da API
with st.sidebar:
    st.markdown('<style>div[data-testid="stToolbar"] {display: none;}</style>', unsafe_allow_html=True)
    # Logo no topo da barra lateral
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=320, use_container_width=True)
    else:
        st.error("Logo não encontrada. Verifique se o arquivo 'LogoSL.jpg' está na pasta 'imagens'.")
    
    st.markdown("### Configuração da API OpenAI")
    api_key = st.text_input("API Key OpenAI:", type="password", help="Insira sua chave da API OpenAI")
    registrar_key = st.button("Registrar API Key", use_container_width=False)
    
    if registrar_key and api_key:
        st.session_state['api_registered'] = True
        st.success("✅ API Key foi registrada com sucesso!")
    elif registrar_key and not api_key:
        st.error("⚠️ Por favor, insira uma API Key antes de registrar.")

# Inicialização do estado da sessão
if 'api_registered' not in st.session_state:
    st.session_state['api_registered'] = False
if 'url_processed' not in st.session_state:
    st.session_state['url_processed'] = False
if 'qa_chain' not in st.session_state:
    st.session_state['qa_chain'] = None

# Processamento da URL
if carregar_url:
    if not url_input:
        st.warning("Por favor, insira uma URL.")
    else:
        if not api_key:
            st.error("⚠️ ATENÇÃO: Para usar este app, você precisa PRIMEIRO registrar sua API Key OpenAI!")
            st.warning("👉 Por favor, insira sua API Key OpenAI na barra lateral e clique em 'Registrar API Key' antes de continuar.")
        else:
            try:
                with st.spinner('Carregando e processando o conteúdo da URL...'):
                    try:
                        # Usar o loader customizado
                        loader = CustomWebLoader(url_input)
                        documents = loader.load()
                        
                        if not documents:
                            st.error("Não foi possível extrair conteúdo da URL.")
                        else:
                            # Dividir o texto em chunks
                            text_splitter = RecursiveCharacterTextSplitter(
                                chunk_size=1000,
                                chunk_overlap=200,
                                separators=["\n\n", "\n", " ", ""]
                            )
                            chunks = text_splitter.split_documents(documents)
                            
                            # Limpar diretório temporário anterior
                            cleanup_temp_dir()
                            
                            # Criar novo diretório temporário
                            temp_dir = get_temp_dir()
                            
                            try:
                                # Criar embeddings e armazenar no Chroma
                                embeddings = HuggingFaceEmbeddings(
                                    model_name="all-MiniLM-L6-v2",
                                    model_kwargs={'device': 'cpu'}
                                )
                                vectorstore = Chroma.from_documents(
                                    documents=chunks,
                                    embedding=embeddings,
                                    persist_directory=temp_dir
                                )
                                
                                # Criar chain de QA
                                qa_chain = RetrievalQA.from_chain_type(
                                    llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
                                    chain_type="stuff",
                                    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                                    return_source_documents=True
                                )
                                
                                # Armazenar o qa_chain no estado da sessão
                                st.session_state['qa_chain'] = qa_chain
                                st.session_state['url_processed'] = True
                                
                            finally:
                                # Garantir que o vectorstore seja fechado
                                if 'vectorstore' in locals():
                                    try:
                                        vectorstore._client.close()
                                    except:
                                        pass
                            
                    except Exception as e:
                        st.error(f"Erro ao carregar a URL: {str(e)}")
                        cleanup_temp_dir()
            except Exception as e:
                st.error(f"Erro ao configurar o modelo de linguagem: {str(e)}")

# Interface para perguntas
if st.session_state.get('url_processed', False):
    st.markdown("### Faça sua pergunta")
    query_input = st.text_input("Digite sua pergunta:", key="query")
    perguntar = st.button("Enviar Pergunta", key="ask", use_container_width=False)
    
    if perguntar and query_input:
        with st.spinner('Processando sua pergunta...'):
            try:
                # Usar o qa_chain armazenado no estado da sessão
                qa_chain = st.session_state.get('qa_chain')
                if qa_chain:
                    result = qa_chain({"query": query_input})
                    
                    # Exibir a resposta
                    st.write("### Resposta:")
                    st.write(result["result"])
                    
                    # Exibir fontes
                    with st.expander("Ver fontes utilizadas"):
                        for doc in result["source_documents"]:
                            st.write("- " + doc.page_content[:200] + "...")
                else:
                    st.error("Erro: Sistema não está pronto para responder perguntas.")
            except Exception as e:
                if not handle_openai_error(e):
                    st.error(f"Erro ao processar a pergunta: {str(e)}")

# Sidebar com instruções
with st.sidebar:
    st.markdown("## Guia de Uso")
    st.markdown("""
    1. Insira sua API Key da OpenAI
    2. Cole a URL do site que deseja analisar
    3. Clique em "Carregar URL"
    4. Faça perguntas sobre o conteúdo
    
    ### Recursos
    - Extração de texto de sites
    - Processamento de conteúdo
    - Perguntas e respostas sobre o conteúdo
    
    ### Observações
    - A qualidade das respostas depende do conteúdo extraído
    - Alguns sites podem bloquear a extração
    - Requisições seguras via HTTPS
    """)

def handle_openai_error(error):
    """Trata erros específicos da API OpenAI"""
    error_msg = str(error).lower()
    if "rate limit" in error_msg:
        st.error("⚠️ Limite de requisições da API OpenAI atingido.")
        st.info("💡 Por favor, aguarde alguns minutos antes de tentar novamente.")
        st.markdown("""
        **Dicas para evitar este erro:**
        1. Faça menos requisições por minuto
        2. Considere usar uma API key com limite maior
        3. Aguarde um pouco entre as requisições
        """)
        return True
    return False

# Fechar o wrapper do conteúdo principal
st.markdown('</div>', unsafe_allow_html=True)
