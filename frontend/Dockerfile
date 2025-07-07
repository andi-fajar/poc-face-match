# Multi-stage build
# Stage 1: Build React app
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (remove --only=production for build dependencies)
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Verify build output
RUN ls -la /app/build && \
    test -f /app/build/index.html && \
    echo "Build verification successful" || (echo "Build verification failed" && exit 1)

# Stage 2: Serve with nginx
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built React app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Verify copied files
RUN ls -la /usr/share/nginx/html && \
    test -f /usr/share/nginx/html/index.html && \
    echo "Static files copied successfully" || (echo "Static files copy failed" && exit 1)

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]