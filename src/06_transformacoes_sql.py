
from pathlib import Path
import duckdb


def transformar_dados():
    raiz = Path(__file__).resolve().parent.parent

    arquivo_entrada = (
        raiz / "data" / "processed" / "clima_enriquecido.parquet"
    )

    arquivo_saida = (
        raiz / "data" / "processed" / "clima_indicadores.parquet"
    )

    if not arquivo_entrada.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo_entrada}"
        )

    conexao = duckdb.connect()

    consulta = """
        SELECT
            codigo_ibge,
            municipio,
            uf,
            regiao,
            data_hora,
            indicador.nome AS indicador,
            indicador.valor AS valor
        FROM read_parquet(?),
        UNNEST([
            struct_pack(nome := 'temperatura',
                        valor := CAST(temperatura AS DOUBLE)),
            struct_pack(nome := 'umidade',
                        valor := CAST(umidade AS DOUBLE)),
            struct_pack(nome := 'precipitacao',
                        valor := CAST(precipitacao AS DOUBLE)),
            struct_pack(nome := 'velocidade_vento',
                        valor := CAST(velocidade_vento AS DOUBLE))
        ]) AS t(indicador)
    """

    df = conexao.execute(
        consulta,
        [str(arquivo_entrada)]
    ).fetchdf()

    df.to_parquet(
        arquivo_saida,
        compression="snappy",
        index=False
    )

    print("Transformação SQL concluída!")
    print(f"Total de registros: {len(df)}")
    print(f"Total de indicadores: {df['indicador'].nunique()}")
    print(f"Arquivo salvo em: {arquivo_saida}")
    print("\nAmostra:")
    print(df.head(10))

    conexao.close()


if __name__ == "__main__":
    transformar_dados()
