from dotenv import load_dotenv

load_dotenv()
import os

import psycopg2

print("Testando conexão com Supabase...")

try:
    conn = psycopg2.connect(os.getenv("SUPABASEDB_URI"))
    cur = conn.cursor()

    # Verificar se tabela existe e tem dados
    cur.execute("SELECT COUNT(*) FROM pluviometria")
    print("✅ Conexão OK!")
    print("Total de registros:", cur.fetchone()[0])

    # Ver municípios disponíveis
    cur.execute("SELECT DISTINCT municipio FROM pluviometria LIMIT 5")
    print("Municípios:", [m[0] for m in cur.fetchall()])

    # Ver período dos dados
    cur.execute("SELECT MIN(ano), MAX(ano) FROM pluviometria")
    print("Período (anos):", cur.fetchone())

    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
