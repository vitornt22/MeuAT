# Estágio de Build e Desenvolvimento
FROM node:18-alpine

WORKDIR /app

# Copia os arquivos de dependências
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o restante do código
COPY . .

# Expõe a porta que o React usa internamente
EXPOSE 3000

# Comando para rodar em modo desenvolvimento
CMD ["npm", "start"]