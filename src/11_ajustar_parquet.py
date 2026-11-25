import pandas as pd
from pathlib import Path

raiz = raiz = Path(__file__).resolve().parent.parent

arquivo_entrada = raiz / "data" / "raw" / "clima_openmeteo.parquet"

arquivo_saida = raiz / "data" / "raw" / "clima_openmeteo_databricks.parquet"

# Ler arquivo original
df = pd.read_parquet(arquivo_entrada)

# Ajustar precisão da data para microssegundos
df["data_hora"] = pd.to_datetime(df["data_hora"]).astype("datetime64[us]")

# Gerar novo Parquet compatível
df.to_parquet(
    arquivo_saida,
    engine="pyarrow",
    compression="snappy",
    index=False
)

print("Novo arquivo gerado com sucesso!")
print("Total de registros:", len(df))
print("Arquivo:", arquivo_saida)