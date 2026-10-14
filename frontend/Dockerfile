# MarketMind AI — Frontend Multi-Stage Dockerfile

# Stage 1: Build React / Vite application
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci || npm install

COPY frontend/ ./
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve production bundle with Nginx
FROM nginx:1.25-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
