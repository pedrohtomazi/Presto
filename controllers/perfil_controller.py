from services.db_service import get_conn
from utils.whatsapp import enviar_mensagem
from state.usuarios import definir_etapa 

def exibir_perfil(numero, mensagens):
    conn = get_conn()
    user = None 
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT membro_pagante, resumos_restantes, cargo FROM usuarios WHERE numero = %s", (numero,))
            user = cursor.fetchone()
    except Exception as e:
        print(f"Erro ao buscar perfil do usuário: {e}")
    finally:
        conn.close()

    if not user:
        texto = mensagens["perfil_inexistente"]
    else:
        tipo = "Membro Pagante" if user['membro_pagante'] else "Usuário Gratuito"
        qtd = user['resumos_restantes']
        texto = mensagens["perfil_info"]
        texto = texto.replace("{{tipo}}", tipo).replace("{{quantidade}}", str(qtd))
        texto += mensagens["perfil_voltar"]

    definir_etapa(numero, "menu") 
    enviar_mensagem(numero, texto)
    return "", 200

