
from pathlib import Path
import pandas as pd


def gerar_metricas() -> pd.DataFrame:
    raiz = Path(__file__).resolve().parent.parent

    arquivo_entrada = (
        raiz / "data" / "processed" / "clima_enriquecido.parquet"
    )

    df = pd.read_parquet(arquivo_entrada)

    # Padronizar data
    df["data_hora"] = pd.to_datetime(df["data_hora"])

    # Criar colunas de calendário
    df["ano"] = df["data_hora"].dt.year
    df["mes"] = df["data_hora"].dt.month
    df["dia"] = df["data_hora"].dt.day

    # Classificar temperatura
    df["faixa_temperatura"] = pd.cut(
        df["temperatura"],
        bins=[-float("inf"), 18, 25, 30, float("inf")],
        labels=["Fria", "Agradável", "Quente", "Muito quente"]
    )

    # Identificar ocorrência de chuva
    df["ocorrencia_chuva"] = df["precipitacao"] > 0

    # Classificar umidade
    df["faixa_umidade"] = pd.cut(
        df["umidade"],
        bins=[-1, 30, 60, 100],
        labels=["Baixa", "Moderada", "Alta"]
    )

    return df


if __name__ == "__main__":
    df = gerar_metricas()

    caminho_saida = (
        Path(__file__).resolve().parent.parent
        / "data" / "processed"
    )

    arquivo_saida = caminho_saida / "clima_com_metricas.parquet"

    df.to_parquet(
        arquivo_saida,
        engine="pyarrow",
        compression="snappy",
        index=False
    )

    print("Métricas climáticas geradas!")
    print(f"Total de registros: {len(df)}")
    print(f"Total de municípios: {df['codigo_ibge'].nunique()}")
    print("\nOcorrências de chuva:")
    print(df["ocorrencia_chuva"].value_counts())
    print("\nFaixas de temperatura:")
    print(df["faixa_temperatura"].value_counts())
    print(f"\nArquivo salvo em: {arquivo_saida}")
