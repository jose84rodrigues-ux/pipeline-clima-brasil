
from pathlib import Path
import subprocess
import sys


def executar_etapa(nome: str, arquivo: str) -> None:
    raiz = Path(__file__).resolve().parent.parent
    caminho_script = raiz / "src" / arquivo

    print("\n" + "=" * 55)
    print(f"EXECUTANDO: {nome}")
    print("=" * 55)

    subprocess.run(
        [sys.executable, str(caminho_script)],
        check=True,
        cwd=raiz
    )

    print(f"Etapa concluída: {nome}")


if __name__ == "__main__":

    etapas = [
        ("Ingestão de municípios - IBGE", "01_leitura_malha.py"),
        ("Ingestão climática - Open-Meteo", "03_ingestao_clima.py"),
        ("Enriquecimento com IBGE", "05_enriquecimento.py"),
        ("Transformações SQL DuckDB", "06_transformacoes_sql.py"),
        ("Geração de métricas climáticas", "07_metricas_climaticas.py"),
        ("Testes de qualidade", "04_qualidade_dados.py"),
        ("Exportação final - Parquet particionado", "10_exportar_resultado.py")
    ]

    try:
        for nome, arquivo in etapas:
            executar_etapa(nome, arquivo)

        print("\nPIPELINE EXECUTADO COM SUCESSO!")

    except subprocess.CalledProcessError as erro:
        print("\nERRO NA EXECUÇÃO DO PIPELINE!")
        print(f"Código de saída: {erro.returncode}")
        sys.exit(1)
