import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

def get_universidades():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM universidades")
        result = cursor.fetchall()
    conn.close()
    return result

def get_cursos(universidade_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos WHERE universidade_id = %s", (universidade_id,))
        result = cursor.fetchall()
    conn.close()
    return result

def get_disciplinas(curso_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM disciplinas WHERE curso_id = %s", (curso_id,))
        result = cursor.fetchall()
    conn.close()
    return result

def get_resumos(disciplina_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, materia, data
            FROM resumos
            WHERE disciplina_id = %s
            ORDER BY data DESC
            LIMIT 5
        """, (disciplina_id,))
        result = cursor.fetchall()
    conn.close()
    return result

def get_resumo_por_id(resumo_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT resumo FROM resumos WHERE id = %s", (resumo_id,))
        result = cursor.fetchone()
    conn.close()
    return result

def update_user_cargo(numero_usuario, novo_cargo):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO usuarios (numero, cargo) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE cargo = VALUES(cargo)
            """
            cursor.execute(sql, (numero_usuario, novo_cargo))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar cargo do usuário {numero_usuario}: {e}")
        return False
    finally:
        conn.close()

def get_user_cargo(numero):
    conn = get_conn()
    cargo = "user" 
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT cargo FROM usuarios WHERE numero = %s", (numero,))
            result = cursor.fetchone()
            if result and result.get("cargo"):
                cargo = result["cargo"]
    except Exception as e:
        print(f"Erro ao obter cargo do usuário {numero}: {e}")
    finally:
        conn.close()
    return cargo