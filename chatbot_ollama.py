import requests
import json
import pyttsx3
import speech_recognition as sr

# URL del servidor Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"

def send_message_to_ollama(messages, model="llama3.2"):
    """
    Envía mensajes al servidor Ollama y muestra la respuesta en tiempo real.
    
    Args:
        messages (list): Lista de mensajes en el chat.
        model (str): El modelo ejecutado en Ollama (por defecto, llama3.2).
    
    Returns:
        str: La respuesta completa generada por el modelo.
    """
    payload = {
        "model": model,
        "messages": messages
    }

    try:
        # Envía la solicitud al servidor y abre un stream para leer la respuesta
        with requests.post(OLLAMA_URL, json=payload, stream=True) as response:
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        # Procesa cada línea como JSON
                        data = json.loads(line.decode("utf-8"))
                        chunk = data.get("message", {}).get("content", "")
                        full_response += chunk
                    except json.JSONDecodeError as e:
                        print(f"\nError decoding JSON: {e}")
            return full_response.strip()
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {e}"

def speak(text):
    """
    Convierte texto en voz usando pyttsx3.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    """
    Reconoce el habla del usuario y lo convierte a texto usando SpeechRecognition.
    
    Returns:
        str: Texto reconocido del audio.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Procesando...")
            return recognizer.recognize_google(audio, language="es-ES")  # Cambia "es-ES" según el idioma deseado
        except sr.WaitTimeoutError:
            return "No se escuchó nada."
        except sr.UnknownValueError:
            return "No entendí lo que dijiste."
        except sr.RequestError as e:
            return f"Error al conectar con el servicio de reconocimiento de voz: {e}"

def chat_with_voice(prompt):
    """
    Un loop de chat interactivo por voz que utiliza Ollama como backend.
    
    Args:
        prompt (str): El prompt inicial para configurar el comportamiento del chatbot.
    """
    print("¡Bienvenido al chatbot por voz! Di 'salir' para terminar.")

    # Inicializar el historial del chat con el prompt inicial
    messages = [{"role": "system", "content": prompt}]

    while True:
        # Reconocer el mensaje del usuario por voz
        user_input = recognize_speech()
        if user_input.lower() in ["salir", "exit"]:
            speak("¡Adiós!")
            print("¡Adiós!")
            break

        print(f"Tú: {user_input}")

        # Agregar el mensaje del usuario al historial
        messages.append({"role": "user", "content": user_input})
        
        # Obtener la respuesta del modelo
        response = send_message_to_ollama(messages)
        print(f"AI: {response}")

        # Leer la respuesta en voz alta
        speak(response)

if __name__ == "__main__":
    # Solicitar el prompt inicial al usuario
    initial_prompt = input("Introduce el prompt inicial para configurar el chatbot: ")
    chat_with_voice(initial_prompt)
