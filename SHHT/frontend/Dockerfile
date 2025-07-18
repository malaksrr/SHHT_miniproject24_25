# frontend/Dockerfile
FROM node:20

WORKDIR /app

COPY . .

RUN npm install

# Build the React app
RUN npm run build

# Serve using a lightweight static server
RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
