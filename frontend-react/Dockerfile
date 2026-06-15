FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

ENV VITE_FRIX_API_BASE_URL=http://127.0.0.1:8000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]