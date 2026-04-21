from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Inicializar almacenamiento en memoria para persistencia de estados del grafo
memory = MemorySaver()

# Configurar herramienta Tavily para búsquedas web en tiempo real
tavily_tool = TavilySearch(max_results=2)
tools = [tavily_tool]

# Inicializar modelo LLM con capacidad de usar herramientas
llm = init_chat_model(model="nvidia/nemotron-3-super-120b-a12b:free", model_provider="openrouter")
llm_with_tools = llm.bind_tools(tools)

# Configuración del grafo con identificador de conversación para persistencia
graph_config = {"configurable": {"thread_id": "1"}}