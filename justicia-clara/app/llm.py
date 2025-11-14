import ollama

def llamar_a_ollama(prompt: str) -> str:
    """
    Envía un prompt a Ollama (modelo llama2) y devuelve la respuesta.
    """
    try:
        response = ollama.chat(model='llama2', messages=[
            {'role': 'user', 'content': prompt}
        ])
        
        return response['message']['content']
        
    except Exception as e:
        print(f"Error al contactar con Ollama: {e}")
        # Relanzamos la excepción para que el pipeline y la UI la capturen
        raise Exception(f"Ollama no está disponible: {e}. Asegúrate de que esté ejecutándose.")