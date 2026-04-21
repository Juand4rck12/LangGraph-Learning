from graph import build_graph
from config import graph_config

def stream_graph_updates(user_input: str):
    # Construir el grafo LangGraph
    graph = build_graph()
    # Stream ejecuta el grafo y obtiene eventos en tiempo real (stream_mode="values" retorna estado completo)
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},  # Entrada: mensaje del usuario
        config=graph_config,  # Configuración con identificador de conversación
        stream_mode="values"  # Retorna el estado completo en cada actualización
    ):
        event["messages"][-1].pretty_print()  # Imprime el último mensaje de forma legible


def run_chat_loop():
    # Loop interactivo: captura entrada del usuario y ejecuta el grafo
    while True:
        try:
            user_input = input("User: ")
            # Permitir salida con múltiples comandos
            if user_input.lower() in ["quit", "exit", "salir", "q"]:
                print("Goodbye!")
                break
            # Procesar y mostrar respuesta del agente
            stream_graph_updates(user_input)
        except:
            # En caso de error, enviar despedida y salir gracefully
            print("Error!")
            stream_graph_updates(user_input="Tell goodbye!")
            break