# Container Notes

This folder is reserved for container-related setup and runtime assets for the Miransas Voice Agent project.

At the moment, the repository is using a lightweight local-first backend flow with Ollama and FastAPI, so no container configuration has been added yet. This space is intentionally left ready for future Docker, devcontainer, or deployment packaging work.

Suggested future usage:

- Dockerfile for the backend service
- docker-compose configuration for local orchestration
- environment variable templates
- optional service containers for audio or inference dependencies

This folder can be used to keep infrastructure and runtime files separate from the main source code.
