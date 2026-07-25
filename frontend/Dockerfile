# frontend/Dockerfile

# Step 1: Build the React app
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./

# --- FIX: Force installation of Linux-specific Rollup dependencies ---
RUN npm install --include=optional --platform=linux --arch=x64

COPY . .
RUN npm run build

# Step 2: Serve the app with Nginx
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]