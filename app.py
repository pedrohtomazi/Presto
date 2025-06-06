from flask import Flask, request
from dotenv import load_dotenv
import os
import json

from utils.whatsapp import enviar_mensagem, iniciar_timer_inatividade, cancelar_timer_final
from state.usuarios import usuarios
from controllers import biblioteca_controller, perfil_controller, pagamentos_controller
from controllers import admin_commands

load_dotenv()

app = Flask(__name__)

# Carrega mensagens
with open("mensagens.json", "r", encoding="utf-8") as f:
    mensagens = json.load(f)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("[🔧 DEBUG - Payload recebido]", data)

    if data.get("event") != "onmessage":
        return "", 200

    msg = data.get("body", "").strip()
    numero = data.get("from", "").strip()

    if msg.startswith("/grupos") or usuarios.get(numero, {}).get("etapa") == "aguardando_mensagem_grupo":
        return admin_commands.handle_admin_command(numero, msg)
    
    if not msg or not numero:
        return "", 200

    print(f"📩 Mensagem de {numero}: {msg}")
    cancelar_timer_final(numero)

    # Se for /menu, reinicia estado
    if msg.lower() == "/menu":
        usuarios[numero] = {"etapa": "menu"}
        resposta = mensagens["menu_principal"]
        enviar_mensagem(numero, resposta)
        return "", 200

    # Recupera estado atual
    estado = usuarios.get(numero, {})

    # Roteia para o controlador conforme a etapa
    etapa = estado.get("etapa")

    if etapa == "menu":
        if msg == "1":
            return biblioteca_controller.iniciar_biblioteca(numero, mensagens)
        elif msg == "2":
            return perfil_controller.exibir_perfil(numero, mensagens)
        elif msg == "3":
            return pagamentos_controller.avisar_manutencao(numero, mensagens)
        else:
            enviar_mensagem(numero, mensagens["comando_menu"])
            return "", 200

    # Continua com outras etapas
    if etapa and etapa.startswith("biblioteca"):
        return biblioteca_controller.continuar_biblioteca(numero, msg, mensagens)

    # Caso contrário, retorna instrução padrão
    enviar_mensagem(numero, mensagens["comando_menu"])
    usuarios[numero] = {"etapa": "menu"}
    return "", 200


if __name__ == "__main__":
    app.run(port=3000)
