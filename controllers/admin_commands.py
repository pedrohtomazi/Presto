import requests
from services.db_service import get_conn
from state.usuarios import usuarios, definir_etapa
from utils.whatsapp import enviar_mensagem
import json
import os

# Carrega comandos e mensagens de admin
with open("admincommands.json", "r", encoding="utf-8") as f:
    admincmds = json.load(f)
    admin_msgs = admincmds["mensagens"]

def is_admin(numero):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT cargo FROM usuarios WHERE numero = %s", (numero,))
        result = cursor.fetchone()
    conn.close()
    return result and result.get("cargo") == "admin"

def buscar_grupos_do_bot():
    token_env = os.getenv("WPP_TOKEN")
    session, token = token_env.split(":", 1)
    url = f"http://localhost:21465/api/{session}/list-chats"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {}  # vazio retorna tudo

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        try:
            resp_json = resp.json()
        except Exception as e:
            print("[DEBUG ERRO JSON]", resp.text)
            return []

        chats = resp_json.get("response", []) if "response" in resp_json else resp_json
        grupos = []
        for chat in chats:
            _id = chat.get("id")
            # Pode vir dict ou string
            if isinstance(_id, dict):
                wid = _id.get("_serialized", "")
                server = _id.get("server", "")
            else:
                wid = _id or ""
                server = wid.split("@")[-1] if "@" in wid else ""

            if server == "g.us" or wid.endswith("@g.us"):
                nome = (
                    chat.get("name")
                    or chat.get("formattedTitle")
                    or chat.get("contact", {}).get("name")
                    or chat.get("contact", {}).get("formattedName")
                    or "Grupo sem nome"
                )
                grupos.append({"id": wid, "name": nome})

        print("[DEBUG grupos]", grupos)
        return grupos
    except Exception as e:
        print("Erro ao buscar grupos:", e)
        return []


     
def enviar_mensagem_grupo(grupo_id, texto):
    if not grupo_id.endswith("@g.us"):
        print(f"[ERRO] grupo_id não é grupo: {grupo_id}")
    token_env = os.getenv("WPP_TOKEN")
    session, token = token_env.split(":", 1)
    url = f"http://localhost:21465/api/{session}/send-message"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
    "phone": "120363417070448420@g.us",
    "isGroup": True,
    "isNewsletter": False,
    "isListId": False,
    "message": texto
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"[admin_commands] Enviando mensagem para grupo: {grupo_id} - Status {resp.status_code}")
    except Exception as e:
        print(f"[admin_commands] Erro ao enviar mensagem no grupo: {e}")

def handle_admin_command(numero, msg):
    if not is_admin(numero):
        enviar_mensagem(numero, admin_msgs["acesso_negado"])
        return "", 200

    # Garante que o dicionário desse número existe
    if numero not in usuarios:
        usuarios[numero] = {}

    # Listar grupos
    if msg.lower().startswith("/grupos"):
        grupos = buscar_grupos_do_bot()
        if not grupos:
            enviar_mensagem(numero, admin_msgs["sem_grupos"])
            return "", 200
        texto = admin_msgs["lista_grupos"]
        for i, g in enumerate(grupos, start=1):
            texto += f"{i}. {g['name']} ({g['id']})\n"
        texto += "\n" + admin_msgs["instrucao_envio"]
        usuarios[numero]["grupos"] = grupos
        definir_etapa(numero, "aguardando_mensagem_grupo")
        enviar_mensagem(numero, texto)
        return "", 200

    # Enviar mensagem para grupo após lista
    if usuarios[numero].get("etapa") == "aguardando_mensagem_grupo":
        partes = msg.split(" ", 1)
        if len(partes) == 2 and partes[0].isdigit():
            idx = int(partes[0]) - 1
            grupos = usuarios[numero].get("grupos", [])
            if 0 <= idx < len(grupos):
                grupo_id = grupos[idx]["id"]
                texto = partes[1]
                enviar_mensagem_grupo(grupo_id, texto)
                enviar_mensagem(numero, admin_msgs["mensagem_enviada"])
                definir_etapa(numero, "menu")
                return "", 200
        enviar_mensagem(numero, admin_msgs["formato_invalido"])
        return "", 200

    # Fallback para qualquer outro comando admin
    enviar_mensagem(numero, "Comando admin não reconhecido.")
    return "", 200
