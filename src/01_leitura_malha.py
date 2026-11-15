
import time
import requests
from pathlib import Path
import pandas as pd
import geopandas as gpd


def consultar_api_ibge(url: str, tentativas: int = 3) -> list:
    """
    Consulta a API do IBGE com tentativas automáticas.
    """

    for tentativa in range(1, tentativas + 1):
        try:
            print(f"Consultando IBGE - tentativa {tentativa}")

            resposta = requests.get(url, timeout=60)
            resposta.raise_for_status()

            return resposta.json()

        except requests.exceptions.RequestException as erro:
            print(f"Erro na consulta: {erro}")

            if tentativa == tentativas:
                raise

            tempo_espera = tentativa * 5
            print(f"Aguardando {tempo_espera} segundos...")
            time.sleep(tempo_espera)

    raise RuntimeError("Não foi possível consultar a API do IBGE.")


def executar_ingestao_ibge():
    projeto = Path(__file__).resolve().parent.parent
    pasta_referencia = projeto / "data" / "reference"

    arquivos_shp = list(pasta_referencia.rglob("*.shp"))

    if arquivos_shp:
        print("Utilizando malha geográfica do IBGE.")

        municipios = gpd.read_file(arquivos_shp[0])

        municipios = municipios[
            municipios["CD_MUN"].astype(str).str.fullmatch(r"\d{7}")
        ].copy()

        municipios_proj = municipios.to_crs(epsg=5880)
        centroides = municipios_proj.geometry.centroid.to_crs(epsg=4326)

        municipios["longitude"] = centroides.x
        municipios["latitude"] = centroides.y

        base_municipios = municipios[
            [
                "CD_MUN",
                "NM_MUN",
                "SIGLA_UF",
                "NM_REGIAO",
                "latitude",
                "longitude"
            ]
        ].copy()

        base_municipios = base_municipios.rename(columns={
            "CD_MUN": "codigo_ibge",
            "NM_MUN": "municipio",
            "SIGLA_UF": "uf",
            "NM_REGIAO": "regiao"
        })

    else:
        print("Malha geográfica não encontrada.")
        print("Utilizando municipios.parquet como referência.")

        arquivo_referencia = pasta_referencia / "municipios.parquet"

        if not arquivo_referencia.exists():
            raise FileNotFoundError(
                "municipios.parquet não encontrado na pasta data/reference."
            )

        base_municipios = pd.read_parquet(arquivo_referencia)

    print("Total de municípios na base:", len(base_municipios))

    # Consultar API do IBGE
    url = (
        "https://servicodados.ibge.gov.br/"
        "api/v1/localidades/municipios"
    )

    dados_ibge = consultar_api_ibge(url)

    codigos_oficiais = {
        str(item["id"]) for item in dados_ibge
    }

    base_municipios["codigo_ibge"] = (
        base_municipios["codigo_ibge"].astype(str)
    )

    base_municipios = base_municipios[
        base_municipios["codigo_ibge"].isin(codigos_oficiais)
    ].copy()

    print("Total de municípios na API:", len(codigos_oficiais))
    print("Total após cruzamento:", len(base_municipios))

    # Salvar arquivos
    pasta_referencia.mkdir(parents=True, exist_ok=True)

    base_municipios.to_csv(
        pasta_referencia / "municipios.csv",
        index=False,
        encoding="utf-8-sig"
    )

    base_municipios.to_parquet(
        pasta_referencia / "municipios.parquet",
        index=False,
        compression="snappy"
    )

    print("Ingestão do IBGE concluída!")
    print("Total de municípios:", len(base_municipios))


if __name__ == "__main__":
    executar_ingestao_ibge()
