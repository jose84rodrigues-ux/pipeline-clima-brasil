
from pathlib import Path
import pandas as pd
import json


def executar_testes(df: pd.DataFrame) -> dict:
    resultados = {}

    # 1. Validar esquema
    colunas_obrigatorias = [
        "codigo_ibge",
        "data_hora",
        "municipio",
        "uf",
        "temperatura",
        "umidade",
        "precipitacao",
        "velocidade_vento"
    ]

    colunas_ausentes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    resultados["esquema_invalido"] = len(colunas_ausentes)

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {colunas_ausentes}"
        )

    # 2. Verificar valores nulos
    resultados["valores_nulos"] = int(df.isnull().sum().sum())

    percentual_nulos = (
        df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
    ) * 100

    resultados["percentual_nulos"] = round(
        float(percentual_nulos), 2
    )

    # 3. Verificar duplicidades
    resultados["duplicados"] = int(
        df.duplicated(
            subset=["codigo_ibge", "data_hora"]
        ).sum()
    )

    # 4. Validar temperatura
    resultados["temperaturas_invalidas"] = int(
        ((df["temperatura"] < -90) |
         (df["temperatura"] > 60)).sum()
    )

    # 5. Validar umidade
    resultados["umidades_invalidas"] = int(
        ((df["umidade"] < 0) |
         (df["umidade"] > 100)).sum()
    )

    # 6. Validar precipitação
    resultados["precipitacoes_invalidas"] = int(
        (df["precipitacao"] < 0).sum()
    )

    # 7. Validar velocidade do vento
    resultados["ventos_invalidos"] = int(
        (df["velocidade_vento"] < 0).sum()
    )

    return resultados


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parent.parent
    caminho_output = raiz / "output"

    arquivos = [
        raiz / "data" / "processed" / "clima_enriquecido.parquet"
    ]

    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo Parquet encontrado.")

    df = pd.concat(
        [pd.read_parquet(arquivo) for arquivo in arquivos],
        ignore_index=True
    )

    resultados = executar_testes(df)

    testes_criticos = {
        chave: valor
        for chave, valor in resultados.items()
        if chave != "percentual_nulos"
    }

    relatorio = {
        "total_registros": len(df),
        "total_municipios": int(df["codigo_ibge"].nunique()),
        "testes": resultados,
        "status_geral": (
            "APROVADO"
            if all(v == 0 for v in testes_criticos.values())
            else "ATENCAO"
        )
    }

    arquivo_json = caminho_output / "relatorio_qualidade.json"

    with open(arquivo_json, "w", encoding="utf-8") as arquivo:
        json.dump(relatorio, arquivo, indent=4, ensure_ascii=False)

    arquivo_csv = caminho_output / "relatorio_qualidade.csv"

    df_relatorio = pd.DataFrame([
        {
            "teste": teste,
            "quantidade": quantidade,
            "status": (
                "APROVADO"
                if quantidade == 0
                else "ATENCAO"
            )
        }
        for teste, quantidade in resultados.items()
    ])

    df_relatorio.to_csv(
        arquivo_csv,
        index=False,
        encoding="utf-8-sig"
    )

    print("Relatório de qualidade gerado!")
    print(f"Total de registros: {len(df)}")
    print(f"Total de municípios: {df['codigo_ibge'].nunique()}")
    print(f"Status geral: {relatorio['status_geral']}")
    print(f"Arquivo JSON: {arquivo_json}")
    print(f"Arquivo CSV: {arquivo_csv}")
    print("\nResultado dos testes:")
    print(df_relatorio.to_string(index=False))
