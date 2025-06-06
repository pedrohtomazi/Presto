from services.db_service import get_universidades, get_cursos, get_disciplinas, get_resumos, get_resumo_por_id
from utils.whatsapp import enviar_mensagem, iniciar_timer_final
from state.usuarios import definir_etapa, obter_etapa
from state.usuarios import salvar_dados_sessao, obter_dados_sessao

def iniciar_biblioteca(numero, mensagens):
    universidades = get_universidades()

    if not universidades:
        resposta = mensagens["universidade_vazia"]
        definir_etapa(numero, "menu")
        enviar_mensagem(numero, resposta)
        return "", 200

    resposta = mensagens["universidades"]
    for i, uni in enumerate(universidades, start=1):
        resposta += f"{i}. {uni['nome']}\n"
    resposta += mensagens["universidade_instrucao"]

    definir_etapa(numero, "biblioteca_universidade")
    salvar_dados_sessao(numero, "temp_universidades", [uni['id'] for uni in universidades])
    enviar_mensagem(numero, resposta)
    return "", 200


def continuar_biblioteca(numero, msg, mensagens):
    etapa_atual = obter_etapa(numero)

    if etapa_atual == "biblioteca_universidade":
        temp_universidades_ids = obter_dados_sessao(numero, "temp_universidades") or []
        idx = int(msg) - 1 if msg.isdigit() else -1
        
        if 0 <= idx < len(temp_universidades_ids):
            universidade_id = temp_universidades_ids[idx]
            salvar_dados_sessao(numero, "universidade_id", universidade_id)
            
            cursos = get_cursos(universidade_id)
            if not cursos:
                resposta = mensagens["curso_vazio"]
                definir_etapa(numero, "menu")
                enviar_mensagem(numero, resposta)
                return "", 200
            
            resposta = mensagens["cursos"]
            for i, curso in enumerate(cursos, start=1):
                resposta += f"{i}. {curso['nome']}\n"
            resposta += mensagens["curso_instrucao"]
            definir_etapa(numero, "biblioteca_curso")
            salvar_dados_sessao(numero, "temp_cursos", [curso['id'] for curso in cursos])
        else:
            resposta = mensagens["erro_numero_invalido"]
        enviar_mensagem(numero, resposta)
        return "", 200

    elif etapa_atual == "biblioteca_curso":
        temp_cursos_ids = obter_dados_sessao(numero, "temp_cursos") or []
        idx = int(msg) - 1 if msg.isdigit() else -1
        
        if 0 <= idx < len(temp_cursos_ids):
            curso_id = temp_cursos_ids[idx]
            salvar_dados_sessao(numero, "curso_id", curso_id)

            disciplinas = get_disciplinas(curso_id)
            if not disciplinas:
                resposta = mensagens["disciplina_vazia"]
                definir_etapa(numero, "menu")
                enviar_mensagem(numero, resposta)
                return "", 200
            
            resposta = mensagens["disciplinas"]
            for i, d in enumerate(disciplinas, start=1):
                resposta += f"{i}. {d['nome']}\n"
            resposta += mensagens["disciplina_instrucao"]
            definir_etapa(numero, "biblioteca_disciplina")
            salvar_dados_sessao(numero, "temp_disciplinas", [d['id'] for d in disciplinas])
        else:
            resposta = mensagens["erro_numero_invalido"]
        enviar_mensagem(numero, resposta)
        return "", 200

    elif etapa_atual == "biblioteca_disciplina":
        temp_disciplinas_ids = obter_dados_sessao(numero, "temp_disciplinas") or []
        idx = int(msg) - 1 if msg.isdigit() else -1
        
        if 0 <= idx < len(temp_disciplinas_ids):
            disciplina_id = temp_disciplinas_ids[idx]
            salvar_dados_sessao(numero, "disciplina_id", disciplina_id)

            resumos = get_resumos(disciplina_id)
            if not resumos:
                resposta = mensagens["resumo_vazio"]
                definir_etapa(numero, "menu")
                enviar_mensagem(numero, resposta)
                return "", 200
            
            resposta = mensagens["resumos"]
            for i, r in enumerate(resumos, start=1):
                resposta += f"{i}. 📅 {r['data']} - {r['materia']}\n"
            resposta += mensagens["resumo_instrucao"]
            definir_etapa(numero, "biblioteca_resumo")
            salvar_dados_sessao(numero, "temp_resumos", [r['id'] for r in resumos])
        else:
            resposta = mensagens["erro_numero_invalido"]
        enviar_mensagem(numero, resposta)
        return "", 200

    elif etapa_atual == "biblioteca_resumo":
        temp_resumos_ids = obter_dados_sessao(numero, "temp_resumos") or []
        idx = int(msg) - 1 if msg.isdigit() else -1
        
        if 0 <= idx < len(temp_resumos_ids):
            resumo_id = temp_resumos_ids[idx]
            resumo = get_resumo_por_id(resumo_id)
            
            if resumo and 'resumo' in resumo:
                enviar_mensagem(numero, mensagens["resumo_completo"] + resumo['resumo'][:3000])
                
                cooldown = mensagens.get("cooldown_mensagem_final", 5)
                iniciar_timer_final(numero, mensagens["mensagem_final"], cooldown)
                definir_etapa(numero, "menu")
                salvar_dados_sessao(numero, "temp_universidades", None)
                salvar_dados_sessao(numero, "temp_cursos", None)
                salvar_dados_sessao(numero, "temp_disciplinas", None)
                salvar_dados_sessao(numero, "temp_resumos", None)
                salvar_dados_sessao(numero, "universidade_id", None)
                salvar_dados_sessao(numero, "curso_id", None)
                salvar_dados_sessao(numero, "disciplina_id", None)
            else:
                enviar_mensagem(numero, mensagens["resumo_nao_encontrado"])
                definir_etapa(numero, "menu")
        else:
            enviar_mensagem(numero, mensagens["erro_numero_invalido"])
        return "", 200
    
    enviar_mensagem(numero, mensagens["comando_menu"])
    definir_etapa(numero, "menu")
    return "", 200