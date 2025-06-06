from flask import Flask, request
from dotenv import load_dotenv
import os
import json

from state.usuarios import iniciar_usuario, resetar_estado, definir_etapa, obter_etapa


from utils.whatsapp import enviar_mensagem, iniciar_timer_inatividade, cancelar_timer_final
from controllers import biblioteca_controller, perfil_controller, pagamentos_controller
from controllers import admin_commands

load_dotenv()

app = Flask(__name__)

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

    print(f"DEBUG APP: Mensagem recebida (repr): {repr(msg)}")
    print(f"DEBUG APP: Mensagem recebida (strip): '{msg}'")
    print(f"DEBUG APP: Número do remetente: '{numero}'")

    iniciar_usuario(numero) 

    etapa_do_usuario = obter_etapa(numero) 
    print(f"DEBUG APP: Etapa do usuário obtida do DB: '{etapa_do_usuario}'")


    if msg.lower().startswith("/grupos") or \
       msg.lower().startswith("/setrole"):
        print("DEBUG APP: Comando admin (grupos ou setrole) detectado. Roteando para admin_commands.")
        return admin_commands.handle_admin_command(numero, msg)

    if etapa_do_usuario == "aguardando_mensagem_grupo":
        print("DEBUG APP: Usuário em etapa 'aguardando_mensagem_grupo'. Roteando para admin_commands.")
        return admin_commands.handle_admin_command(numero, msg)


    if msg.lower() == "/menu":
        print("DEBUG APP: Comando /menu detectado.")
        resetar_estado(numero) 
        resposta = mensagens["menu_principal"]
        enviar_mensagem(numero, resposta)
        return "", 200

    if not msg or not numero:
        print("DEBUG APP: Mensagem ou número vazios.")
        return "", 200

    print(f"📩 Mensagem de {numero}: {msg}")
    cancelar_timer_final(numero) 

    if etapa_do_usuario == "menu": 
        print("DEBUG APP: Etapa 'menu'. Verificando opção.")
        if msg == "1":
            print("DEBUG APP: Opção 1 (Biblioteca).")
            return biblioteca_controller.iniciar_biblioteca(numero, mensagens)
        elif msg == "2":
            print("DEBUG APP: Opção 2 (Perfil).")
            return perfil_controller.exibir_perfil(numero, mensagens)
        elif msg == "3":
            print("DEBUG APP: Opção 3 (Pagamentos).")
            return pagamentos_controller.avisar_manutencao(numero, mensagens)
        else:
            print(f"DEBUG APP: Opção inválida no menu. Enviando: '{mensagens['comando_menu']}'")
            enviar_mensagem(numero, mensagens["comando_menu"])
            return "", 200

    if etapa_do_usuario and etapa_do_usuario.startswith("biblioteca"):
        print("DEBUG APP: Etapa 'biblioteca'. Continuando fluxo.")
        return biblioteca_controller.continuar_biblioteca(numero, msg, mensagens)

    print(f"DEBUG APP: Nenhuma etapa ou comando correspondente. Enviando: '{mensagens['comando_menu']}'")
    enviar_mensagem(numero, mensagens["comando_menu"])
    resetar_estado(numero) 
    return "", 200


if __name__ == "__main__":
    app.run(port=3000)
