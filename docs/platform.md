# Backing Platform — ArchiveBox

`archivebox-api` is a **client** of an [ArchiveBox](https://archivebox.io/)
web-archiving instance. This page provides a Docker recipe for deploying one locally
to serve as the target of `ARCHIVEBOX_BASE_URL`. For production topologies, follow the
upstream [ArchiveBox documentation](https://github.com/ArchiveBox/ArchiveBox/wiki).

!!! note "Backing-system recipe"
    Each connector in the ecosystem follows the same convention — a
    `docs/platform.md` recipe for the system it integrates with, accompanied by a
    sample Compose stack that mirrors [`services/`](https://github.com/Knuckles-Team).
    Systems offered only as a managed service have no local recipe.

## Single-node deployment (Compose)

ArchiveBox publishes the `archivebox/archivebox` image. The following stack runs one
instance on `:8000` with a persistent data volume:

```yaml
# docker/archivebox.compose.yml
services:
  archivebox:
    image: docker.io/archivebox/archivebox:latest
    container_name: archivebox
    hostname: archivebox
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=your-password
      - CSRF_TRUSTED_ORIGINS=http://localhost:8000   # REQUIRED for the REST API / auth
      - ALLOWED_HOSTS=*
      - PUBLIC_INDEX=False
      - PUBLIC_SNAPSHOTS=False
      - PUBLIC_ADD_VIEW=False
    volumes:
      - archivebox_data:/data

volumes:
  archivebox_data:
```

```bash
docker compose -f docker/archivebox.compose.yml up -d

# Confirm the API answers
curl -s http://localhost:8000/api/v1/core/snapshots
```

## Connect archivebox-api

```bash
export ARCHIVEBOX_BASE_URL=http://localhost:8000
export ARCHIVEBOX_USERNAME=admin
export ARCHIVEBOX_PASSWORD=your-password
export ARCHIVEBOX_SSL_VERIFY=False          # self-signed / local cert

archivebox-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Combined deployment

A combined stack places ArchiveBox and the MCP server on one Docker network, so the
server reaches ArchiveBox by container name:

```yaml
# docker/stack.compose.yml
services:
  archivebox:
    image: docker.io/archivebox/archivebox:latest
    hostname: archivebox
    environment:
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=your-password
      - CSRF_TRUSTED_ORIGINS=http://archivebox:8000
      - ALLOWED_HOSTS=*
    volumes:
      - archivebox_data:/data

  archivebox-api-mcp:
    image: knucklessg1/archivebox-api:latest
    depends_on: [archivebox]
    environment:
      - ARCHIVEBOX_BASE_URL=http://archivebox:8000
      - ARCHIVEBOX_USERNAME=admin
      - ARCHIVEBOX_PASSWORD=your-password
      - ARCHIVEBOX_SSL_VERIFY=False
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8001
    ports: ["8001:8001"]

volumes:
  archivebox_data:
```

```bash
docker compose -f docker/stack.compose.yml up -d
```

With the instance running, the [MCP tools and `Api` client](usage.md) read the
snapshot catalog, archive results, and tags, and the CLI tool module adds, updates,
and removes archived URLs.
</content>
