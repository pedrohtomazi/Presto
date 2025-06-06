from services.db_service import get_universidades, get_cursos, get_disciplinas, get_resumos, get_resumo_por_id
from utils.whatsapp import enviar_mensagem, iniciar_timer_final
from state.usuarios import usuarios, definir_etapa


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
    usuarios[numero]["universidades"] = universidades
    enviar_mensagem(numero, resposta)
    return "", 200


def continuar_biblioteca(numero, msg, mensagens):
    estado = usuarios[numero]

    if estado["etapa"] == "biblioteca_universidade":
        universidades = estado.get("universidades", [])
        idx = int(msg) - 1 if msg.isdigit() else -1
        if 0 <= idx < len(universidades):
            universidade_id = universidades[idx]['id']
            estado["universidade_id"] = universidade_id
            cursos = get_cursos(universidade_id)
            if not cursos:
                resposta = mensagens["curso_vazio"]
                estado["etapa"] = "menu"
                enviar_mensagem(numero, resposta)
                return "", 200
            resposta = mensagens["cursos"]
            for i, curso in enumerate(cursos, start=1):
                resposta += f"{i}. {curso['nome']}\n"
            resposta += mensagens["curso_instrucao"]
            estado["etapa"] = "biblioteca_curso"
            estado["cursos"] = cursos
        else:
            resposta = mensagens["erro_numero_invalido"]
        enviar_mensagem(numero, resposta)
        return "", 200

    elif estado["etapa"] == "biblioteca_curso":
        cursos = estado.get("cursos", [])
        idx = int(msg) - 1 if msg.isdigit() else -1
        if 0 <= idx < len(cursos):
            curso_id = cursos[idx]['id']
            estado["curso_id"] = curso_id
            disciplinas = get_disciplinas(curso_id)
            if not disciplinas:
                resposta = mensagens["disciplina_vazia"]
                estado["etapa"] = "menu"
                enviar_mensagem(numero, resposta)
                return "", 200
            resposta = mensagens["disciplinas"]
            for i, d in enumerate(disciplinas, start=1):
                resposta += f"{i}. {d['nome']}\n"
            resposta += mensagens["disciplina_instrucao"]
            estado["etapa"] = "biblioteca_disciplina"
            estado["disciplinas"] = disciplinas
        else:
            resposta = mensagens["erro_numero_invalido"]
        enviar_mensagem(numero, resposta)
        return "", 200

    elif estado["etapa"] == "biblioteca_disciplina":
        disciplinas = estado.get("disciplinas", [])
        idx = int(msg) - 1 if msg.isdigit() else -1
        if 0 <= idx < len(disciplinas):
            disciplina_id = disciplinas[idx]['id']
            estado["disciplina_id"] = disciplina_id
            resumos = get_resumos(disciplina_id)
            if not resumos:
                resposta = mensagens["resumo_vazio"]
                estado["etapa"] = "menu"
                enviar_mensagem(numero, resposta)
                return "", 200
            resposta = mensagens["resumos"]
            for i, r in enumerate(resumos, start=1):
                resposta += f"{i}. \ud83d\udcc5 {r['data']} - {r['materia']}\n"
            resposta += mensagens["resumo_instrucao"]
            estado["etapa"] = "biblioteca_resumo"
            estado["resumos"] = resumos
        else:
            resposta = mensagens["erro_numero_invalido"]
        enviar_mensagem(numero, resposta)
        return "", 200

    elif estado["etapa"] == "biblioteca_resumo":
        resumos = estado.get("resumos", [])
        idx = int(msg) - 1 if msg.isdigit() else -1
        if 0 <= idx < len(resumos):
            resumo_id = resumos[idx]['id']
            resumo = get_resumo_por_id(resumo_id)
            enviar_mensagem(numero, mensagens["resumo_completo"] + resumo['resumo'][:3000])
            cooldown = mensagens.get("cooldown_mensagem_final", 5)
            iniciar_timer_final(numero, mensagens["mensagem_final"], cooldown)
            estado["etapa"] = "menu"
        else:
            enviar_mensagem(numero, mensagens["erro_numero_invalido"])
        return "", 200
