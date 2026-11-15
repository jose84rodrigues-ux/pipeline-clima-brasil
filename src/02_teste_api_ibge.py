
import requests

url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

resposta = requests.get(url, timeout=60)
resposta.raise_for_status()

municipios = resposta.json()

print("Conexão com IBGE: OK")
print("Total retornado:", len(municipios))
print("Primeiro município:", municipios[0]["nome"])
