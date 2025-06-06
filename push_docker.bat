@echo off

:: Docker image'i GitHub'a push et
set /p DOCKER_USERNAME="GitHub Username: "
set /p DOCKER_PASSWORD="GitHub Password: "
docker tag mcp-server:latest ghcr.io/%DOCKER_USERNAME%/mcp-server:latest
docker login ghcr.io -u %DOCKER_USERNAME% -p %DOCKER_PASSWORD%
docker push ghcr.io/%DOCKER_USERNAME%/mcp-server:latest

:: Sonucu goster
echo Docker image'i GitHub'a push edildi.
echo URL: ghcr.io/%DOCKER_USERNAME%/mcp-server:latest
