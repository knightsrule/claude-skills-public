#!/usr/bin/env python3
"""
FastAPI Project Initialization Script

This script initializes a new FastAPI project from the template,
replacing placeholders with user-provided values.
"""

import os
import shutil
import argparse
from pathlib import Path


def replace_placeholders(content: str, replacements: dict) -> str:
    """Replace template placeholders in content."""
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def process_file(file_path: Path, replacements: dict) -> None:
    """Process a single file, replacing placeholders."""
    try:
        content = file_path.read_text()
        new_content = replace_placeholders(content, replacements)
        file_path.write_text(new_content)
    except UnicodeDecodeError:
        # Skip binary files
        pass


def init_project(
    project_name: str,
    project_description: str,
    output_dir: Path,
    template_dir: Path,
) -> None:
    """Initialize a new FastAPI project from template."""

    # Create output directory
    project_path = output_dir / project_name
    if project_path.exists():
        raise ValueError(f"Directory {project_path} already exists")

    print(f"🚀 Initializing FastAPI project: {project_name}")
    print(f"   Location: {project_path}")

    # Copy template
    shutil.copytree(template_dir, project_path)

    # Prepare replacements
    replacements = {
        "PROJECT_NAME": project_name,
        "PROJECT_DESCRIPTION": project_description,
    }

    # Process all files
    for root, _, files in os.walk(project_path):
        for filename in files:
            file_path = Path(root) / filename
            process_file(file_path, replacements)

    # Copy .env.example to .env
    env_example = project_path / ".env.example"
    env_file = project_path / ".env"
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env from .env.example")

    print(f"\n✅ Project '{project_name}' created successfully!")
    print("\nNext steps:")
    print(f"1. cd {project_name}")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("4. pip install -r requirements.txt")
    print("5. Edit .env with your configuration")
    print("6. python -m src.main --reload")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new FastAPI project from template"
    )
    parser.add_argument(
        "project_name",
        help="Name of the project (e.g., 'my-api-server')"
    )
    parser.add_argument(
        "--description",
        default="FastAPI Server",
        help="Project description"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        required=True,
        help="Path to template directory"
    )

    args = parser.parse_args()

    try:
        init_project(
            project_name=args.project_name,
            project_description=args.description,
            output_dir=args.output_dir,
            template_dir=args.template_dir,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
