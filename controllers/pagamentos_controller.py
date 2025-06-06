from utils.whatsapp import enviar_mensagem
from state.usuarios import definir_etapa

def avisar_manutencao(numero, mensagens):
    texto = mensagens["pagamento_manutencao"]
    definir_etapa(numero, "menu")
    enviar_mensagem(numero, texto)
    return "", 200
