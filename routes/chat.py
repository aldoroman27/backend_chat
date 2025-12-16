import google.generativeai as genai
from flask import Flask, jsonify, Blueprint, request
from dotenv import load_dotenv
import chromadb
import os


load_dotenv()

#Configuramos el blueprint
chat_bp = Blueprint('chat_bp', __name__)

#Configuramos las variables de entorno
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key = GOOGLE_KEY)
#Indicamos el modelo que usaremos
model = genai.GenerativeModel('gemini-2.5-flash')

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(current_dir, 'routes\info_empresa.txt')

print(file_path)

BASE_CONOCIMIENTO = ""

#Cargamos la informacion como la base del conocimiento
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        BASE_CONOCIMIENTO = f.read()
    print("Información cargada correctamente!")
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    BASE_CONOCIMIENTO = "No hay informacion por el momento"

#Definimos el endpoint
@chat_bp.route('/chat',methods=['POST'])
def responder_chat():
    data = request.get_json()

    if not data:
        return jsonify({'error':'JSON invalido'})
    
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error":"Mensaje Vació"}),400

    try:
        prompt_completo = f"""
            Actua como un asistente virtual experto y muy amable de nuestra empresa MIDO GROUP.
            Usa la siguiente información sacada de nuestra web para responder las preguntas que te hagan.
            Tus intrucciones son las siguientes:
            1. Responde preguntas básicas basandote UNICAMENTE en la siguiente informacion de contexto.
            2. Si al inicio de la conversación te brindan un nombre saludalos con ese nombre y usa ese nombre.
            3. No inventes informacion ni datos.
            4. Responde en formato corto y directo.
            ----- TEXTO DE LA EMPRESA --------
            {BASE_CONOCIMIENTO}
            ------ PREGUNTA DEL USUARIO ------
            {user_message}   
            """
        response = model.generate_content(prompt_completo)

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            reply = "La pregunta fue bloqueda por politicas de seguridad"
        elif response.text:
            reply = response.text
        else:
            reply = "Lo siento, mi filtro de seguridad bloqueó la respuesta (o no entendí la pregunta)"
        return jsonify({'reply':reply})
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return jsonify({'message':f'Error durante el proceso:{e}'}), 500