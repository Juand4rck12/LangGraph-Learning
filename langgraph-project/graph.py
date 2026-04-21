from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from config import tools, memory, llm_with_tools
from state import State
from IPython.display import Image, display

def build_graph() -> StateGraph:
    # Crear grafo de estado basado en la estructura de State
    graph_builder = StateGraph(State)

    # Nodo chatbot: procesa mensajes y genera respuestas con capacidad de usar herramientas
    def chatbot(state: State):
        message = llm_with_tools.invoke(state["messages"])  # LLM procesa el historial de mensajes
        return {"messages": [message]}  # Retorna nueva respuesta al estado
    
    graph_builder.add_node("chatbot", chatbot)

    # Nodo tools: ejecuta las herramientas seleccionadas por el LLM
    tool_node = ToolNode(tools)
    graph_builder.add_node("tools", tool_node)

    # Decisión condicional: si LLM usa herramientas, ir a nodo tools; si no, terminar
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    
    # Flujo: después de ejecutar herramientas, volver a chatbot para procesar resultados
    graph_builder.add_edge("tools", "chatbot")
    # Punto de inicio: siempre comienza en el nodo chatbot
    graph_builder.add_edge(START, "chatbot")

    # Compilar el grafo con almacenamiento en memoria para persistencia
    graph = graph_builder.compile(checkpointer=memory)
    
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open("grah_diagram.png", "wb") as f:
            f.write(png_data)
    except:
        pass

    return graph