import os
import requests
import threading
import time
from dotenv import load_dotenv
from state.usuarios import usuarios

load_dotenv()

COOLDOWN_MENSAGEM_FINAL = 5

def enviar_mensagem(numero, texto):
    token_env = os.getenv("WPP_TOKEN")
    session, token = token_env.split(":", 1)
    url = f"http://localhost:21465/api/{session}/send-message"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "phone": numero.replace("@c.us", ""),
        "message": texto
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📤 Resposta enviada: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

def iniciar_timer_inatividade(numero, mensagem, cooldown=30):
    def timeout():
        time.sleep(cooldown)
        if usuarios.get(numero, {}).get("aguardando_resposta"):
            enviar_mensagem(numero, mensagem)
            usuarios[numero]["aguardando_resposta"] = False

    if numero not in usuarios:
        usuarios[numero] = {}
    usuarios[numero]["aguardando_resposta"] = True
    threading.Thread(target=timeout).start()

def iniciar_timer_final(numero, mensagem_final):
    def enviar():
        if usuarios.get(numero, {}).get("mensagem_final_pendente"):
            enviar_mensagem(numero, mensagem_final)
            usuarios[numero]["mensagem_final_pendente"] = False

    if numero not in usuarios:
        usuarios[numero] = {}
    usuarios[numero]["mensagem_final_pendente"] = True
    t = threading.Timer(COOLDOWN_MENSAGEM_FINAL, enviar)
    usuarios[numero]["timer_mensagem_final"] = t
    t.start()

def cancelar_timer_final(numero):
    if usuarios.get(numero, {}).get("timer_mensagem_final"):
        usuarios[numero]["timer_mensagem_final"].cancel()
        usuarios[numero]["mensagem_final_pendente"] = False
