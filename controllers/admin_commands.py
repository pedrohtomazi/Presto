import requests
from services.db_service import get_conn, update_user_cargo, get_user_cargo
from state.usuarios import definir_etapa, obter_etapa, salvar_dados_sessao, obter_dados_sessao
from utils.whatsapp import enviar_mensagem
import json
import os

with open("admincommands.json", "r", encoding="utf-8") as f:
    admincmds = json.load(f)
    admin_msgs = admincmds["mensagens"]

def buscar_grupos_do_bot():
    token_env = os.getenv("WPP_TOKEN")
    session, token = token_env.split(":", 1)
    url = f"http://localhost:21465/api/{session}/list-chats"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {}

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
        return

    token_env = os.getenv("WPP_TOKEN")
    session, token = token_env.split(":", 1)
    url = f"http://localhost:21465/api/{session}/send-message"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
    "phone": grupo_id,
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
    print(f"DEBUG ADMIN: Início do handle_admin_command. Mensagem: '{msg}'")
    
    user_cargo = get_user_cargo(numero)
    print(f"DEBUG ADMIN: Cargo do usuário '{numero}': '{user_cargo}'")

    if user_cargo not in ["admin", "manager"]:
        print(f"DEBUG ADMIN: Usuário '{numero}' com cargo '{user_cargo}' não tem acesso geral a comandos admin. Acesso negado.")
        enviar_mensagem(numero, admin_msgs["acesso_negado"])
        return "", 200

    if msg.lower().startswith("/grupos"):
        print("DEBUG ADMIN: Comando /grupos detectado.")
        grupos = buscar_grupos_do_bot()
        if not grupos:
            enviar_mensagem(numero, admin_msgs["sem_grupos"])
            return "", 200
        texto = admin_msgs["lista_grupos"]
        for i, g in enumerate(grupos, start=1):
            texto += f"{i}. {g['name']} ({g['id']})\n"
        texto += "\n" + admin_msgs["instrucao_envio"]
        salvar_dados_sessao(numero, "admin_grupos", grupos)
        definir_etapa(numero, "aguardando_mensagem_grupo")
        enviar_mensagem(numero, texto)
        return "", 200

    elif msg.lower().startswith("/setrole"):
        print("DEBUG ADMIN: Comando /setrole detectado.")
        partes = msg.split() 
  
        if len(partes) != 3:
            print("DEBUG ADMIN: Formato de /setrole inválido. Partes:", partes)
            enviar_mensagem(numero, admin_msgs["setrole_instrucao"])
            return "", 200
        
        target_numero_raw = partes[1]
        novo_cargo = partes[2].lower()

        if not target_numero_raw.endswith("@c.us"):
            target_numero = f"{target_numero_raw}@c.us"
        else:
            target_numero = target_numero_raw

        cargos_validos = ["user", "admin", "manager"]
        if novo_cargo not in cargos_validos:
            print(f"DEBUG ADMIN: Cargo inválido: '{novo_cargo}'. Cargos válidos: {cargos_validos}")
            enviar_mensagem(numero, admin_msgs["setrole_cargo_invalido"].replace("{{cargos_validos}}", ", ".join(cargos_validos)))
            return "", 200
        
        if update_user_cargo(target_numero, novo_cargo):
            print(f"DEBUG ADMIN: Sucesso ao setar cargo '{novo_cargo}' para '{target_numero_raw}'")
            enviar_mensagem(numero, admin_msgs["setrole_sucesso"].replace("{{numero}}", target_numero_raw).replace("{{cargo}}", novo_cargo))
        else:
            print(f"DEBUG ADMIN: Falha ao setar cargo para '{target_numero_raw}'")
            enviar_mensagem(numero, admin_msgs["setrole_invalido"])
        
        definir_etapa(numero, "menu")
        return "", 200

    etapa_do_usuario = obter_etapa(numero)
    if etapa_do_usuario == "aguardando_mensagem_grupo":
        print("DEBUG ADMIN: Etapa 'aguardando_mensagem_grupo'.")
        partes = msg.split(" ", 1)
        if len(partes) == 2 and partes[0].isdigit():
            idx = int(partes[0]) - 1
            grupos_salvos = obter_dados_sessao(numero, "admin_grupos") or []
            if 0 <= idx < len(grupos_salvos):
                grupo_id = grupos_salvos[idx]["id"]
                texto = partes[1]
                enviar_mensagem_grupo(grupo_id, texto)
                enviar_mensagem(numero, admin_msgs["mensagem_enviada"])
                definir_etapa(numero, "menu")
                salvar_dados_sessao(numero, "admin_grupos", None)
                return "", 200
        enviar_mensagem(numero, admin_msgs["formato_invalido"])
        return "", 200

    print(f"DEBUG ADMIN: Comando admin não reconhecido: '{msg}'")
    enviar_mensagem(numero, "Comando admin não reconhecido.")
    return "", 200
