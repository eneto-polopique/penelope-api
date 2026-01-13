# Docker Deployment Guide

## Quick Start

### Build and Run with Docker

```bash
# Build the image
docker build -t penelope-api .

# Run the container
docker run -d \
  --name penelope-api \
  -p 8000:8000 \
  --env-file .env \
  penelope-api
```

### Using Docker Compose (Recommended)

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop the service
docker-compose down
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with your configuration:

```env
DB_HOST=db.polopique.local
DB_PORT=5432
DB_NAME=penelope_db
DB_USER=penelope
DB_PASSWORD=DchMUt7nbr

API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

DEFAULT_PAGE_SIZE=50
MAX_PAGE_SIZE=100
```

### Docker Compose Environment

You can also set environment variables directly in `docker-compose.yml` or use a `.env` file for docker-compose.

## Docker Commands

### Build

```bash
# Build the image
docker build -t penelope-api .

# Build with no cache
docker build --no-cache -t penelope-api .
```

### Run

```bash
# Run in detached mode
docker run -d -p 8000:8000 --env-file .env --name penelope-api penelope-api

# Run with custom port
docker run -d -p 9000:8000 --env-file .env --name penelope-api penelope-api

# Run in interactive mode (for debugging)
docker run -it --rm -p 8000:8000 --env-file .env penelope-api
```

### Manage

```bash
# View logs
docker logs penelope-api
docker logs -f penelope-api  # Follow logs

# Stop container
docker stop penelope-api

# Start container
docker start penelope-api

# Restart container
docker restart penelope-api

# Remove container
docker rm penelope-api

# Execute command in running container
docker exec -it penelope-api /bin/bash
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# Start and rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers, volumes
docker-compose down -v

# Scale service (if needed)
docker-compose up -d --scale api=3
```

## Production Deployment

### 1. Build Production Image

```bash
docker build -t penelope-api:1.0.0 .
```

### 2. Tag for Registry

```bash
# For Docker Hub
docker tag penelope-api:1.0.0 yourusername/penelope-api:1.0.0
docker tag penelope-api:1.0.0 yourusername/penelope-api:latest

# For private registry
docker tag penelope-api:1.0.0 registry.example.com/penelope-api:1.0.0
```

### 3. Push to Registry

```bash
# Login to Docker Hub
docker login

# Push image
docker push yourusername/penelope-api:1.0.0
docker push yourusername/penelope-api:latest
```

### 4. Deploy on Server

```bash
# Pull image on production server
docker pull yourusername/penelope-api:1.0.0

# Run container
docker run -d \
  --name penelope-api \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  yourusername/penelope-api:1.0.0
```

## Advanced Configuration

### Resource Limits

```bash
docker run -d \
  --name penelope-api \
  -p 8000:8000 \
  --env-file .env \
  --memory="512m" \
  --cpus="1.0" \
  penelope-api
```

### Volume Mounts (for development)

```bash
docker run -d \
  --name penelope-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/api:/app/api \
  penelope-api
```

### Custom Network

```bash
# Create network
docker network create penelope-network

# Run container on network
docker run -d \
  --name penelope-api \
  -p 8000:8000 \
  --env-file .env \
  --network penelope-network \
  penelope-api
```

## Health Check

The container includes a health check that runs every 30 seconds:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' penelope-api
```

## Troubleshooting

### View Container Logs

```bash
docker logs penelope-api
docker logs -f penelope-api --tail 100
```

### Access Container Shell

```bash
docker exec -it penelope-api /bin/bash
```

### Check Container Stats

```bash
docker stats penelope-api
```

### Inspect Container

```bash
docker inspect penelope-api
```

### Test API Inside Container

```bash
docker exec penelope-api curl http://localhost:8000/health
```

## Security Best Practices

The Dockerfile implements several security practices:

1. **Non-root user**: Application runs as `appuser` (UID 1000)
2. **Multi-stage build**: Smaller final image with fewer attack vectors
3. **No cache**: Pip packages installed without cache to reduce image size
4. **Health check**: Built-in health monitoring
5. **Minimal base image**: Uses slim Python image

## Performance Optimization

### Image Size

Current image size should be around 200-300MB. To check:

```bash
docker images penelope-api
```

### Startup Time

The container should be ready in 5-10 seconds. Monitor with:

```bash
docker-compose logs -f api
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Build Docker image
  run: docker build -t penelope-api .

- name: Push to registry
  run: |
    docker tag penelope-api ${{ secrets.REGISTRY }}/penelope-api:${{ github.sha }}
    docker push ${{ secrets.REGISTRY }}/penelope-api:${{ github.sha }}
```

## Access the API

Once running, access the API at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
