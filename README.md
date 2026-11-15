
# Pipeline de Integração de Dados Climáticos e Geográficos do Brasil

## 1. Visão geral

Projeto de Engenharia de Dados desenvolvido para integrar informações geográficas e climáticas de municípios brasileiros.

O pipeline utiliza duas APIs públicas para coletar, integrar, transformar e validar dados, disponibilizando resultados em arquivos Parquet.

A amostra climática contempla 230 municípios de diferentes regiões brasileiras, com dados horários entre 11/10/2026 e 09/11/2026.

## 2. Objetivos

- Integrar dados de diferentes fontes públicas.
- Automatizar processos de ETL.
- Aplicar transformações utilizando Python e SQL.
- Implementar verificações automatizadas de qualidade.
- Gerar arquivos analíticos em formato Parquet.

## 3. Fontes de dados

| Fonte | Descrição |
|---|---|
| API IBGE | Identificação e informações dos municípios brasileiros |
| API Open-Meteo | Dados climáticos históricos por coordenadas geográficas |

### Variáveis climáticas

- Temperatura (°C)
- Umidade relativa (%)
- Precipitação (mm)
- Velocidade do vento (km/h)

## 4. Tecnologias utilizadas

- Python
- Pandas
- GeoPandas
- Requests
- DuckDB
- PyArrow
- Parquet
- Databricks (ambiente utilizado durante o desenvolvimento)

O pipeline local pode ser executado sem uma conta Databricks.

## 5. Arquitetura do projeto

O pipeline é organizado nas seguintes etapas:

1. **Ingestão IBGE:** consulta a API de localidades e prepara a referência geográfica dos municípios.
2. **Ingestão Open-Meteo:** consulta dados climáticos horários em lotes de municípios.
3. **Enriquecimento:** realiza JOIN entre dados climáticos e geográficos.
4. **Transformação SQL:** utiliza DuckDB e UNNEST para reorganizar os indicadores climáticos.
5. **Geração de métricas:** cria classificações de temperatura, umidade e ocorrência de chuva.
6. **Qualidade de dados:** executa testes automatizados e gera relatórios JSON e CSV.
7. **Exportação final:** gera arquivos Parquet particionados por ano e mês, utilizando compressão Snappy.

## 6. Estrutura de diretórios

```text
pipeline-clima-brasil/
├── data/
│   ├── raw/
│   ├── reference/
│   └── processed/
├── docs/
├── output/
│   ├── clima_final/
│   ├── relatorio_qualidade.json
│   └── relatorio_qualidade.csv
├── src/
│   ├── 01_leitura_malha.py
│   ├── 02_teste_api_ibge.py
│   ├── 03_ingestao_clima.py
│   ├── 04_qualidade_dados.py
│   ├── 05_enriquecimento.py
│   ├── 06_transformacoes_sql.py
│   ├── 07_metricas_climaticas.py
│   ├── 08_executar_pipeline.py
│   ├── 09_preparar_municipios.py
│   └── 10_exportar_resultado.py
├── .gitignore
├── requirements.txt
└── README.md
```

## 7. Tratamento e qualidade dos dados

O projeto implementa:

- Padronização de tipos e datas.
- Remoção de registros duplicados.
- Tratamento de valores meteorológicos ausentes.
- Integração entre fontes por código IBGE.
- Transformação de estruturas com SQL UNNEST.
- Criação de métricas climáticas.
- Validação de esquema, valores nulos e duplicidades.
- Verificação de limites válidos para as variáveis climáticas.

Os resultados dos testes são disponibilizados em relatórios JSON e CSV.

## 8. Resultados obtidos

| Indicador | Resultado |
|---|---:|
| Municípios na referência IBGE | 5.571 |
| Municípios na amostra climática | 230 |
| Período analisado | 11/10/2026 a 09/11/2026 |
| Registros climáticos | 165.600 |
| Registros após transformação SQL | 662.400 |
| Indicadores climáticos | 4 |
| Testes de qualidade aprovados | 8 |

## 9. Como executar o projeto

### Instalar dependências

```bash
pip install -r requirements.txt
```

### Executar o pipeline completo

```bash
python src/08_executar_pipeline.py
```

O pipeline realiza as etapas de ingestão, transformação, validação e exportação final.

## 10. Resultados e arquivos gerados

Principais arquivos:

- `data/raw/clima_openmeteo.parquet`
- `data/processed/clima_enriquecido.parquet`
- `data/processed/clima_indicadores.parquet`
- `data/processed/clima_com_metricas.parquet`
- `output/relatorio_qualidade.json`
- `output/relatorio_qualidade.csv`
- `output/clima_final/`

Os arquivos finais são particionados por ano e mês e utilizam compressão Snappy.

## 11. Considerações finais

O projeto demonstra a aplicação prática de conceitos de Engenharia de Dados, incluindo integração de APIs, ingestão em lotes, tratamento de falhas, processamento com Python e SQL, enriquecimento de dados e validação automatizada da qualidade.

A referência geográfica contempla os 5.571 municípios retornados pela API do IBGE. A amostra climática contempla 230 municípios e não representa a totalidade dos municípios brasileiros.
