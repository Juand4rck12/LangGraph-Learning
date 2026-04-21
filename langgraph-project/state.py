from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

# Definir el estado del grafo con historial de mensajes
# add_messages permite concatenar automáticamente nuevos mensajes al historial
class State(TypedDict):
    messages: Annotated[list, add_messages]  # Almacena el historial de mensajes de la conversación