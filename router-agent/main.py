from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from IPython.display import Image, display


# Cargar variables de entorno desde archivo .env
load_dotenv()

# LLM: modelo usado para clasificar y responder mensajes
llm = init_chat_model(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    model_provider="openrouter",
)

# Esquema de clasificación: define la salida estructurada del clasificador
class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional (therapist) or logical response"
    )

# Estado: estructura de datos compartida entre nodos del grafo
class State(TypedDict):
    messages: Annotated[list, add_messages]  # Historial de conversación
    message_type: str | None  # Tipo clasificado: "emotional" o "logical"

# Nodo clasificador: analiza el mensaje y determina si es emocional o lógico
def classify_message(state: State):
    last_message = state["messages"][-1]
    # LLM con salida estructurada: garantiza respuesta en formato MessageClassifier
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional suport, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}  # Retorna la clasificación

def router(state: State):
    # Nodo enrutador: dirige el mensaje hacia terapeuta o agente lógico
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {"next": "therapist"}  # Va al agente terapeuta
    
    return {"next": "logical"}  # Va al agente lógico

def therapist_agent(state: State):
    # Nodo terapeuta: responde con empatía y apoyo emocional
    last_message = state["messages"][-1]
    messages = [
        {
            "role": "system",
            "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)  # Genera respuesta empática
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def logical_agent(state: State):
    # Nodo lógico: responde con análisis objetivo y basado en hechos
    last_message = state["messages"][-1]
    messages = [
        {
            "role": "system",
            "content": """You are a purely logical assistant. Focus only on facts and information.
                        Provide clear, concise answers based on logic and evidence.
                        Do not address emotions or provide emotional support.
                        Be direct and straightforward in your responses."""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)  # Genera respuesta lógica
    return {"messages": [{"role": "assistant", "content": reply.content}]}

# Construcción del grafo: define nodos y flujo de ejecución
graph_builder = StateGraph(State)

# Agregar todos los nodos del grafo
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)

# Flujo inicial: START -> classifier -> router
graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

# Enrutamiento condicional: router decide entre dos rutas
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"therapist": "therapist", "logical": "logical"}
)

# Ambas rutas terminan el grafo
graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)

graph = graph_builder.compile()  # Grafo compilado y listo para usar

# Generar diagrama
# png_data = graph.get_graph().draw_mermaid_png()
# with open("graph_diagram.png", "wb") as f:
#     f.write(png_data)

def run_chatbot():
    # Loop interactivo: mantiene conversación hasta que usuario salga
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        # Detectar comandos de salida
        if user_input in ["exit", "salir", "q"]:
            print("Adios!")
            break

        # Agregar mensaje del usuario al historial
        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        # Ejecutar grafo: clasifica, enruta y genera respuesta
        state = graph.invoke(state)

        # Mostrar respuesta del agente
        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()