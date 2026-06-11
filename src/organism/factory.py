"""
SaaS Factory - Project/solution generation factory.
Port of autonomous-organism/factory/index.js to Python with Pydantic v2.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.organism.factory")


class ProjectSpec(BaseModel):
    """Specification for a generated project."""
    name: str
    problem: str
    status: str = "BUILDING"  # BUILDING, READY, FAILED
    created: str = Field(default_factory=lambda: datetime.now().isoformat())
    files: list[str] = Field(default_factory=list)


class SaasFactory:
    """Generates project scaffolds from problem descriptions.

    Creates a basic project structure with:
    - package.json
    - API route stub
    - Database schema
    - Dockerfile
    - docker-compose.yml
    """

    def __init__(self, output_dir: str | Path | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "factory_output"

    def _ensure_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_project_name(self, text: str) -> str:
        """Generate a project name from problem text."""
        words = text.split()[:3]
        return "-".join(w.lower() for w in words)

    def _generate_package_json(self, name: str) -> str:
        """Generate package.json content."""
        import json
        return json.dumps({
            "name": name,
            "version": "0.1.0",
            "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
            "dependencies": {"next": "^14.0.0", "react": "^18.0.0", "react-dom": "^18.0.0"},
        }, indent=2)

    def _generate_api_route(self) -> str:
        """Generate API route stub."""
        return '''import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    message: 'API working!'
  });
}
'''

    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile content."""
        return """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
"""

    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml content."""
        return """version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data
    environment:
      - NODE_ENV=development
"""

    def build(self, problem_text: str) -> ProjectSpec:
        """Build a project scaffold from a problem description.

        Args:
            problem_text: Description of the problem to solve.

        Returns:
            ProjectSpec with build status and file list.
        """
        self._ensure_dir()
        project_name = self.generate_project_name(problem_text)
        project_dir = self.output_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        files: dict[str, str] = {
            "package.json": self._generate_package_json(project_name),
            "app/api/route.js": self._generate_api_route(),
            "Dockerfile": self._generate_dockerfile(),
            "docker-compose.yml": self._generate_docker_compose(),
        }

        created_files: list[str] = []
        for rel_path, content in files.items():
            file_path = project_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            created_files.append(rel_path)

        logger.info("Built project: %s (%d files)", project_name, len(created_files))

        return ProjectSpec(
            name=project_name,
            problem=problem_text,
            status="READY",
            files=created_files,
        )

    def get_status(self) -> dict:
        """Get factory status."""
        projects: list[str] = []
        if self.output_dir.exists():
            projects = [d.name for d in self.output_dir.iterdir() if d.is_dir()]

        return {
            "output_dir": str(self.output_dir),
            "projects_built": len(projects),
            "project_names": projects,
        }
