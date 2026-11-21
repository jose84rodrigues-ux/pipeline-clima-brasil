
from pathlib import Path
from typing import Any
import time
import requests
import pandas as pd

# Configurações de controle da API

TAMANHO_LOTE = 10
INTERVALO_ENTRE_LOTES = 1
MAX_TENTATIVAS = 3


def consultar_openmeteo(
    lote: pd.DataFrame
) -> list[dict[str, Any]]:
    """
    Consulta a API Open-Meteo para um lote de municípios.
    """

    url = "https://archive-api.open-meteo.com/v1/archive"

    parametros = {
        "latitude": ",".join(lote["latitude"].astype(str)),
        "longitude": ",".join(lote["longitude"].astype(str)),
        "start_date": "2026-10-11",
        "end_date": "2026-11-09",
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "timezone": "America/Sao_Paulo"
    }

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resposta = requests.get(
                url,
                params=parametros,
                timeout=120
            )
            resposta.raise_for_status()

            dados = resposta.json()

            # A API retorna uma lista quando há várias coordenadas
            if isinstance(dados, dict):
                dados = [dados]

            return dados

        except requests.exceptions.RequestException as erro:
            print(f"Falha na tentativa {tentativa}: {erro}")

            if tentativa == MAX_TENTATIVAS:
                raise

            time.sleep(tentativa * 5)

    raise RuntimeError("Falha na consulta Open-Meteo.")


def executar_ingestao() -> None:
    raiz = Path(__file__).resolve().parent.parent

    arquivo_municipios = (
        raiz / "data" / "reference" / "municipios_amostra.parquet"
    )

    municipios = pd.read_parquet(arquivo_municipios)

    registros = []
    tamanho_lote = TAMANHO_LOTE

    total_lotes = (len(municipios) + tamanho_lote - 1) // tamanho_lote

    for inicio in range(0, len(municipios), tamanho_lote):
        lote = municipios.iloc[inicio:inicio + tamanho_lote]

        numero_lote = inicio // tamanho_lote + 1

        print(f"Consultando lote {numero_lote}/{total_lotes}...")

        respostas = consultar_openmeteo(lote)

        for municipio, dados in zip(
            lote.to_dict("records"),
            respostas
        ):
            horario = dados["hourly"]

            df = pd.DataFrame({
                "data_hora": horario["time"],
                "temperatura": horario["temperature_2m"],
                "umidade": horario["relative_humidity_2m"],
                "precipitacao": horario["precipitation"],
                "velocidade_vento": horario["wind_speed_10m"]
            })

            df["codigo_ibge"] = str(municipio["codigo_ibge"])
            df["municipio"] = municipio["municipio"]
            df["uf"] = municipio["uf"]

            registros.append(df)

        # Controle de frequência entre lotes
        time.sleep(INTERVALO_ENTRE_LOTES)

    df_final = pd.concat(registros, ignore_index=True)

    df_final["data_hora"] = pd.to_datetime(df_final["data_hora"])

    pasta_saida = raiz / "data" / "raw"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    arquivo_saida = pasta_saida / "clima_openmeteo.parquet"

    df_final.to_parquet(
        arquivo_saida,
        engine="pyarrow",
        compression="snappy",
        index=False
    )

    print("\nIngestão Open-Meteo concluída!")
    print(f"Total de registros: {len(df_final)}")
    print(f"Total de municípios: {df_final['codigo_ibge'].nunique()}")
    print(f"Arquivo salvo em: {arquivo_saida}")


if __name__ == "__main__":
    executar_ingestao()
