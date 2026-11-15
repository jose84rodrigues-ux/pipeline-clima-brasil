
from pathlib import Path
import pandas as pd
import shutil


def exportar_resultado() -> None:
    raiz = Path(__file__).resolve().parent.parent

    arquivo_entrada = (
        raiz / "data" / "processed" / "clima_com_metricas.parquet"
    )

    pasta_saida = raiz / "output" / "clima_final"

    # Limpar arquivos da execução anterior
    if pasta_saida.exists():
        shutil.rmtree(pasta_saida)

    # Verificar se o arquivo de entrada existe
    if not arquivo_entrada.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo_entrada}"
        )

    # Carregar dados processados
    dados = pd.read_parquet(arquivo_entrada)

    # Criar partições de ano e mês
    dados["data_hora"] = pd.to_datetime(dados["data_hora"])
    dados["ano"] = dados["data_hora"].dt.year
    dados["mes"] = dados["data_hora"].dt.month

    # Exportar Parquet com compressão Snappy
    dados.to_parquet(
        pasta_saida,
        engine="pyarrow",
        compression="snappy",
        partition_cols=["ano", "mes"],
        index=False
    )

    print("Exportação final concluída!")
    print("Total de registros:", len(dados))
    print("Arquivo salvo em:", pasta_saida)


if __name__ == "__main__":
    exportar_resultado()
