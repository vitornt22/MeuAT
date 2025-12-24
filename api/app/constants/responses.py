# Responses to organize Swagger documentation

FARM_BY_ID = responses = {
    200: {"description": "Fazenda encontrada com sucesso."},
    400: {"description": "ID inválido ou mal formatado."},
    404: {"description": "Nenhum imóvel encontrado com o ID fornecido."},
    500: {"description": "Erro interno no processamento espacial."}
}

FARMS_BY_POINTS = {
    200: {"description": "Lista de fazendas que contêm o ponto (pode ser vazia)."},
    400: {"description": "Coordenadas fora dos limites geográficos aceitáveis."}
}


FARMS_BY_RADIUS = {
    200: {"description": "Lista de fazendas encontradas no raio de busca."},
    400: {"description": "Valor de raio negativo ou coordenadas inválidas."},
    413: {"description": "Raio de busca excede o limite de 500km."}
}
