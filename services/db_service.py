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
