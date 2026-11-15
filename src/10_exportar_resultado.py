
from pathlib import Path
import pandas as pd


def exportar_resultado() -> None:
    raiz = Path(__file__).resolve().parent.parent

    arquivo_entrada = (
        raiz / "data" / "processed" / "clima_com_metricas.parquet"
    )

    pasta_saida = raiz / "output" / "clima_final"

    dados = pd.read_parquet(arquivo_entrada)

    dados["data_hora"] = pd.to_datetime(dados["data_hora"])
    dados["ano"] = dados["data_hora"].dt.year
    dados["mes"] = dados["data_hora"].dt.month

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
