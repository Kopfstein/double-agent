# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        curl wget procps \
        git git-lfs \
        htop neovim \
    && rm -rf /var/lib/apt/lists/*

# Create user with id 1000
RUN useradd -m -u 1000 user

# Change the working directory to the `app` directory
WORKDIR /app
RUN mkdir -p /app && chown user:user /app

# Set the user to the one created above
USER user

# Copy the lockfile and `pyproject.toml` into the image
COPY --chown=user:user uv.lock /app/uv.lock
COPY --chown=user:user pyproject.toml /app/pyproject.toml

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the project into the image
COPY --chown=user:user . /app

# Sync the project
RUN uv sync --frozen

# Expose the port and run the server
EXPOSE 7860
CMD ["uv", "run", "python", "-m", "http.server", "7860", "-d", "./double_agent/"]
