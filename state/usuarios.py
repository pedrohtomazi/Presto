# Dicionário global para armazenar estado de cada usuário
usuarios = {}

def iniciar_usuario(numero):
    if numero not in usuarios:
        usuarios[numero] = {"etapa": "menu"}

def resetar_estado(numero):
    usuarios[numero] = {"etapa": "menu"}

def definir_etapa(numero, etapa):
    if numero in usuarios:
        usuarios[numero]["etapa"] = etapa

def obter_etapa(numero):
    return usuarios.get(numero, {}).get("etapa")
