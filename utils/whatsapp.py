import os
import requests
import threading
import time
from dotenv import load_dotenv
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

from state.usuarios import salvar_dados_sessao, obter_dados_sessao 

def iniciar_timer_inatividade(numero, mensagem, cooldown=30):
    def timeout():
        time.sleep(cooldown)
 
        aguardando_resposta_db = obter_dados_sessao(numero, "aguardando_resposta_timer")
        if aguardando_resposta_db:
            enviar_mensagem(numero, mensagem)
            salvar_dados_sessao(numero, "aguardando_resposta_timer", False) 

    salvar_dados_sessao(numero, "aguardando_resposta_timer", True) 

    threading.Thread(target=timeout).start()


_timer_pool = {} 

def iniciar_timer_final(numero, mensagem_final, cooldown=COOLDOWN_MENSAGEM_FINAL):

    def enviar():
        enviar_mensagem(numero, mensagem_final)
        if numero in _timer_pool:
            del _timer_pool[numero] 

    cancelar_timer_final(numero) 

    t = threading.Timer(cooldown, enviar)
    _timer_pool[numero] = t 
    t.start()

def cancelar_timer_final(numero):
    if numero in _timer_pool and _timer_pool[numero].is_alive():
        _timer_pool[numero].cancel()
        del _timer_pool[numero]
    elif numero in _timer_pool:
        del _timer_pool[numero]

