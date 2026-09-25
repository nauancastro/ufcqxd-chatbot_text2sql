"""
Script para importar dados pluviométricos do arquivo TXT para o banco Supabase (PostgreSQL).
Os dados são lidos do arquivo posto121_quixada.txt e inseridos na tabela 'pluviometria'.
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
SUPABASEDB_URI = os.getenv("SUPABASEDB_URI")

# Caminho do arquivo de dados
ARQUIVO_DADOS = Path(__file__).parent / "posto121_quixada.txt"

# Valor que indica dado inválido/não disponível no arquivo original
VALOR_INVALIDO = 888.0


def criar_conexao():
    """Cria e retorna uma conexão com o banco PostgreSQL."""
    if not SUPABASEDB_URI:
        raise ValueError("SUPABASEDB_URI deve estar definida no arquivo .env")
    return psycopg2.connect(SUPABASEDB_URI)


def tratar_valor(valor_str: str) -> float | None:
    """
    Converte string para float, retornando None para valores inválidos.
    O valor 888.0 é usado como indicador de dado não disponível.
    """
    try:
        valor = float(valor_str)
        if valor == VALOR_INVALIDO:
            return None
        return valor
    except (ValueError, TypeError):
        return None


def ler_arquivo_dados(caminho_arquivo: Path) -> list[dict]:
    """
    Lê o arquivo de dados pluviométricos e retorna uma lista de dicionários.
    Cada dicionário representa uma linha (mês/ano) de dados.
    """
    registros = []

    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()

        # Pular a linha de cabeçalho
        for linha in linhas[1:]:
            linha = linha.strip()
            if not linha:
                continue

            campos = linha.split(';')

            if len(campos) < 38:  # Deve ter pelo menos 38 campos
                print(f"Linha ignorada (campos insuficientes): {linha[:50]}...")
                continue

            registro = {
                'municipio': campos[0],
                'posto': campos[1],
                'latitude': tratar_valor(campos[2]),
                'longitude': tratar_valor(campos[3]),
                'ano': int(campos[4]),
                'mes': int(campos[5]),
                'total': tratar_valor(campos[6]),
                'dia01': tratar_valor(campos[7]),
                'dia02': tratar_valor(campos[8]),
                'dia03': tratar_valor(campos[9]),
                'dia04': tratar_valor(campos[10]),
                'dia05': tratar_valor(campos[11]),
                'dia06': tratar_valor(campos[12]),
                'dia07': tratar_valor(campos[13]),
                'dia08': tratar_valor(campos[14]),
                'dia09': tratar_valor(campos[15]),
                'dia10': tratar_valor(campos[16]),
                'dia11': tratar_valor(campos[17]),
                'dia12': tratar_valor(campos[18]),
                'dia13': tratar_valor(campos[19]),
                'dia14': tratar_valor(campos[20]),
                'dia15': tratar_valor(campos[21]),
                'dia16': tratar_valor(campos[22]),
                'dia17': tratar_valor(campos[23]),
                'dia18': tratar_valor(campos[24]),
                'dia19': tratar_valor(campos[25]),
                'dia20': tratar_valor(campos[26]),
                'dia21': tratar_valor(campos[27]),
                'dia22': tratar_valor(campos[28]),
                'dia23': tratar_valor(campos[29]),
                'dia24': tratar_valor(campos[30]),
                'dia25': tratar_valor(campos[31]),
                'dia26': tratar_valor(campos[32]),
                'dia27': tratar_valor(campos[33]),
                'dia28': tratar_valor(campos[34]),
                'dia29': tratar_valor(campos[35]),
                'dia30': tratar_valor(campos[36]),
                'dia31': tratar_valor(campos[37]),
            }

            registros.append(registro)

    return registros


def inserir_dados_banco(conn, registros: list[dict], batch_size: int = 100) -> None:
    """
    Insere os registros na tabela pluviometria do PostgreSQL.
    Usa INSERT ON CONFLICT para evitar duplicatas (baseado na constraint uq_pluviometria).
    """
    total = len(registros)
    inseridos = 0
    erros = 0

    print(f"Iniciando inserção de {total} registros...")

    # Query SQL com ON CONFLICT para upsert
    sql = """
    INSERT INTO pluviometria (
        municipio, posto, latitude, longitude, ano, mes, total,
        dia01, dia02, dia03, dia04, dia05, dia06, dia07, dia08, dia09, dia10,
        dia11, dia12, dia13, dia14, dia15, dia16, dia17, dia18, dia19, dia20,
        dia21, dia22, dia23, dia24, dia25, dia26, dia27, dia28, dia29, dia30, dia31
    ) VALUES %s
    ON CONFLICT (municipio, posto, ano, mes) 
    DO UPDATE SET
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        total = EXCLUDED.total,
        dia01 = EXCLUDED.dia01, dia02 = EXCLUDED.dia02, dia03 = EXCLUDED.dia03,
        dia04 = EXCLUDED.dia04, dia05 = EXCLUDED.dia05, dia06 = EXCLUDED.dia06,
        dia07 = EXCLUDED.dia07, dia08 = EXCLUDED.dia08, dia09 = EXCLUDED.dia09,
        dia10 = EXCLUDED.dia10, dia11 = EXCLUDED.dia11, dia12 = EXCLUDED.dia12,
        dia13 = EXCLUDED.dia13, dia14 = EXCLUDED.dia14, dia15 = EXCLUDED.dia15,
        dia16 = EXCLUDED.dia16, dia17 = EXCLUDED.dia17, dia18 = EXCLUDED.dia18,
        dia19 = EXCLUDED.dia19, dia20 = EXCLUDED.dia20, dia21 = EXCLUDED.dia21,
        dia22 = EXCLUDED.dia22, dia23 = EXCLUDED.dia23, dia24 = EXCLUDED.dia24,
        dia25 = EXCLUDED.dia25, dia26 = EXCLUDED.dia26, dia27 = EXCLUDED.dia27,
        dia28 = EXCLUDED.dia28, dia29 = EXCLUDED.dia29, dia30 = EXCLUDED.dia30,
        dia31 = EXCLUDED.dia31
    """

    cursor = conn.cursor()

    # Inserir em lotes para melhor performance
    for i in range(0, total, batch_size):
        lote = registros[i:i + batch_size]

        try:
            # Converter dicionários para tuplas
            valores = [
                (
                    reg['municipio'], reg['posto'], reg['latitude'], reg['longitude'],
                    reg['ano'], reg['mes'], reg['total'],
                    reg['dia01'], reg['dia02'], reg['dia03'], reg['dia04'], reg['dia05'],
                    reg['dia06'], reg['dia07'], reg['dia08'], reg['dia09'], reg['dia10'],
                    reg['dia11'], reg['dia12'], reg['dia13'], reg['dia14'], reg['dia15'],
                    reg['dia16'], reg['dia17'], reg['dia18'], reg['dia19'], reg['dia20'],
                    reg['dia21'], reg['dia22'], reg['dia23'], reg['dia24'], reg['dia25'],
                    reg['dia26'], reg['dia27'], reg['dia28'], reg['dia29'], reg['dia30'],
                    reg['dia31']
                )
                for reg in lote
            ]

            execute_values(cursor, sql, valores)
            conn.commit()

            inseridos += len(lote)
            print(f"Progresso: {inseridos}/{total} registros processados")

        except Exception as e:
            conn.rollback()
            erros += len(lote)
            print(f"Erro ao inserir lote {i//batch_size + 1}: {e}")

    cursor.close()

    print("\nImportação concluída!")
    print(f"  - Registros processados: {inseridos}")
    print(f"  - Erros: {erros}")


def main():
    """Função principal do script."""
    print("=" * 60)
    print("IMPORTADOR DE DADOS PLUVIOMÉTRICOS - FUNCEME")
    print("=" * 60)

    # Verificar se o arquivo existe
    if not ARQUIVO_DADOS.exists():
        print(f"ERRO: Arquivo não encontrado: {ARQUIVO_DADOS}")
        return

    print(f"\nArquivo de dados: {ARQUIVO_DADOS}")

    # Ler dados do arquivo
    print("\nLendo arquivo de dados...")
    registros = ler_arquivo_dados(ARQUIVO_DADOS)
    print(f"Total de registros lidos: {len(registros)}")

    if not registros:
        print("Nenhum registro encontrado no arquivo.")
        return

    # Mostrar amostra dos dados
    print("\nAmostra do primeiro registro:")
    primeiro = registros[0]
    print(f"  Município: {primeiro['municipio']}")
    print(f"  Posto: {primeiro['posto']}")
    print(f"  Período: {primeiro['mes']:02d}/{primeiro['ano']}")
    print(f"  Total do mês: {primeiro['total']} mm")

    # Conectar ao banco e inserir dados
    print("\nConectando ao banco de dados...")
    try:
        conn = criar_conexao()
        print("Conexão estabelecida!")

        inserir_dados_banco(conn, registros)

        conn.close()
        print("Conexão fechada.")

    except Exception as e:
        print(f"ERRO: {e}")
        return


if __name__ == "__main__":
    main()
