from pathlib import Path
import pandas as pd


def preparar_municipios() -> None:
    raiz = Path(__file__).resolve().parent.parent

    # Ler dados climáticos atuais
    arquivos = list((raiz / "output").rglob("*.parquet"))

    if not arquivos:
        raise FileNotFoundError(
            "Arquivos Parquet não encontrados em output."
        )

    df_clima = pd.concat(
        [pd.read_parquet(arquivo) for arquivo in arquivos],
        ignore_index=True
    )

    # Identificar os municípios da amostra
    codigos = (
        df_clima["codigo_ibge"]
        .astype(str)
        .unique()
    )

    # Ler referência completa do IBGE
    df_municipios = pd.read_parquet(
        raiz / "data" / "reference" / "municipios.parquet"
    )

    df_municipios["codigo_ibge"] = (
        df_municipios["codigo_ibge"].astype(str)
    )

    # Filtrar os municípios da amostra
    df_amostra = df_municipios[
        df_municipios["codigo_ibge"].isin(codigos)
    ].copy()

    # Salvar referência da amostra
    caminho_saida = (
        raiz / "data" / "reference" / "municipios_amostra.parquet"
    )

    df_amostra.to_parquet(
        caminho_saida,
        compression="snappy",
        index=False
    )

    print("Referência de municípios criada!")
    print(f"Total de municípios: {len(df_amostra)}")
    print(f"Arquivo salvo em: {caminho_saida}")


if __name__ == "__main__":
    preparar_municipios()
