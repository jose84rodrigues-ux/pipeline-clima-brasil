
from pathlib import Path
import pandas as pd


def enriquecer_dados() -> pd.DataFrame:
    raiz = Path(__file__).resolve().parent.parent

    # Carregar dados climáticos
    arquivos = [
        raiz / "data" / "raw" / "clima_openmeteo.parquet"
    ]

    df_clima = pd.concat(
        [pd.read_parquet(arquivo) for arquivo in arquivos],
        ignore_index=True
    )

    # Remover registros duplicados
    total_antes = len(df_clima)

    df_clima = df_clima.drop_duplicates(
        subset=["codigo_ibge", "data_hora"]
    )

    total_duplicados = total_antes - len(df_clima)

    # Tratar registros com dados meteorológicos ausentes
    total_antes_nulos = len(df_clima)

    df_clima = df_clima.dropna(
        subset=[
            "temperatura",
            "umidade",
            "precipitacao",
            "velocidade_vento"
        ]
    )

    total_nulos = total_antes_nulos - len(df_clima)

    print(f"Duplicidades removidas: {total_duplicados}")
    print(
        f"Registros com dados meteorológicos ausentes removidos: {total_nulos}"
    )

    # Carregar dados de referência do IBGE
    df_municipios = pd.read_parquet(
        raiz / "data" / "reference" / "municipios.parquet"
    )

    # Garantir o mesmo tipo de chave
    df_clima["codigo_ibge"] = df_clima["codigo_ibge"].astype(str)
    df_municipios["codigo_ibge"] = df_municipios["codigo_ibge"].astype(str)

    # JOIN entre clima e municípios
    df_enriquecido = df_clima.merge(
        df_municipios[
            ["codigo_ibge", "regiao", "latitude", "longitude"]
        ],
        on="codigo_ibge",
        how="left",
        validate="many_to_one"
    )

    # Validar correspondência com o IBGE
    if df_enriquecido["regiao"].isna().any():
        raise ValueError(
            "Existem municípios sem correspondência na base do IBGE."
        )

    return df_enriquecido


if __name__ == "__main__":
    df = enriquecer_dados()

    caminho_saida = (
        Path(__file__).resolve().parent.parent
        / "data" / "processed"
    )

    caminho_saida.mkdir(parents=True, exist_ok=True)

    arquivo_saida = caminho_saida / "clima_enriquecido.parquet"

    df.to_parquet(
        arquivo_saida,
        engine="pyarrow",
        compression="snappy",
        index=False
    )

    print(f"\nArquivo enriquecido salvo em: {arquivo_saida}")

    print("Enriquecimento concluído!")
    print(f"Total de registros: {len(df)}")
    print(f"Total de municípios: {df['codigo_ibge'].nunique()}")
    print(f"Registros sem região: {df['regiao'].isna().sum()}")
    print("\nAmostra:")
    print(df.head())
