import json
from services.db_service import get_conn

def iniciar_usuario(numero):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO user_sessions (numero, etapa, estado_data, ultima_interacao)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP())
                ON DUPLICATE KEY UPDATE ultima_interacao = CURRENT_TIMESTAMP()
            """
            cursor.execute(sql, (numero, "menu", json.dumps({}))) 
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao iniciar usuário no DB: {e}")
    finally:
        conn.close()

def resetar_estado(numero):

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE user_sessions SET etapa = %s, estado_data = %s, ultima_interacao = CURRENT_TIMESTAMP WHERE numero = %s"
            cursor.execute(sql, ("menu", json.dumps({}), numero))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao resetar estado do usuário no DB: {e}")
    finally:
        conn.close()

def definir_etapa(numero, etapa):

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE user_sessions SET etapa = %s, ultima_interacao = CURRENT_TIMESTAMP WHERE numero = %s"
            cursor.execute(sql, (etapa, numero))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao definir etapa do usuário no DB: {e}")
    finally:
        conn.close()

def obter_etapa(numero):
    
    conn = get_conn()
    etapa = "menu"
    try:
        with conn.cursor() as cursor:
            sql = "SELECT etapa FROM user_sessions WHERE numero = %s"
            cursor.execute(sql, (numero,))
            result = cursor.fetchone()
            if result:
                etapa = result.get("etapa", "menu")
    except Exception as e:
        print(f"Erro ao obter etapa do usuário do DB: {e}")
    finally:
        conn.close()
    return etapa

def salvar_dados_sessao(numero, chave, valor):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            sql_select = "SELECT estado_data FROM user_sessions WHERE numero = %s"
            cursor.execute(sql_select, (numero,))
            current_data_row = cursor.fetchone()
            
            session_data = json.loads(current_data_row['estado_data']) if current_data_row and current_data_row['estado_data'] else {}
            
            if valor is None:
                session_data.pop(chave, None)
            else:
                session_data[chave] = valor
            
            sql_update = "UPDATE user_sessions SET estado_data = %s, ultima_interacao = CURRENT_TIMESTAMP WHERE numero = %s"
            cursor.execute(sql_update, (json.dumps(session_data), numero))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar dados de sessão para {chave}: {e}")
    finally:
        conn.close()

def obter_dados_sessao(numero, chave=None):
    conn = get_conn()
    data = {}
    try:
        with conn.cursor() as cursor:
            sql = "SELECT estado_data FROM user_sessions WHERE numero = %s"
            cursor.execute(sql, (numero,))
            result = cursor.fetchone()
            if result and result['estado_data']:
                data = json.loads(result['estado_data'])
    except Exception as e:
        print(f"Erro ao obter dados de sessão: {e}")
    finally:
        conn.close()
    
    if chave:
        return data.get(chave)
    return data

