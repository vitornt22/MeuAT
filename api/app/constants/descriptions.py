# Descriptios to organize Swagger documentation

DESC_GET_BY_ID = """
Busca os detalhes completos de um imóvel rural utilizando o seu código oficial (CAR).

* **Validação**: O ID não pode ser apenas espaços em branco.
* **Retorno**: Objeto contendo dados cadastrais e a geometria em formato GeoJSON.
"""

DESC_BUSCA_PONTO = """
Identifica quais fazendas englobam geograficamente o ponto (Latitude/Longitude) informado.

* **Geoprocessamento**: Utiliza a função `ST_Contains` do PostGIS.
* **Paginação**: Suporta os parâmetros `page` e `size` no corpo da requisição.
* **Filtro Extra**: É possível filtrar por nome da cidade.
"""

DESC_BUSCA_RAIO = """
Localiza todas as fazendas que possuem qualquer parte de seu território dentro do raio informado.

* **Geoprocessamento**: Utiliza `ST_DWithin` para performance otimizada com índices GiST.
* **Limites**: O raio máximo permitido é de **500km** para evitar sobrecarga do servidor.
"""


INITIAL_DESCRIPTION = """
    API para consulta e análise de imóveis rurais do Estado de São Paulo.
    
    ### Funcionalidades:
    * **Busca por Ponto**: Verifica se uma coordenada está dentro de uma fazenda.
    * **Busca por Raio**: Lista fazendas em um raio de distância (em km).
    * **Health Check**: Monitoramento de saúde da API e Banco de Dados.
    
    **Diferenciais Técnicos:** Paginação, Logs estruturados e Índices Espaciais.
    """,
