FROM node:18-alpine

WORKDIR /app

# Copiar package.json e instalar dependencias
COPY package*.json ./
RUN npm install

# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 5173

# Comando por defecto
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
