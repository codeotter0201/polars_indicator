#!/usr/bin/env python3
"""
Build and publish polars-indicator package to PyPI.
This script handles the complete build and publishing process.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path = None) -> int:
    """Run a command and return exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def clean_previous_builds(project_root: Path) -> None:
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous builds...")

    # Clean dist directory
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        import shutil

        shutil.rmtree(dist_dir)

    # Clean target/wheels directory
    wheels_dir = project_root / "target" / "wheels"
    if wheels_dir.exists():
        import shutil

        shutil.rmtree(wheels_dir)


def build_wheel(project_root: Path) -> int:
    """Build wheel package."""
    print("📦 Building wheel...")
    exit_code = run_command(
        [sys.executable, "-m", "maturin", "build", "--release"],
        cwd=project_root,
    )

    if exit_code != 0:
        print("❌ Build failed!")
        return exit_code

    print("✅ Build completed successfully!")
    return 0


def list_built_wheels(project_root: Path) -> list[Path]:
    """List and display built wheels."""
    wheels = []

    # Check target/wheels directory (maturin output)
    wheels_dir = project_root / "target" / "wheels"
    if wheels_dir.exists():
        wheels.extend(list(wheels_dir.glob("*.whl")))

    # Check dist directory (fallback)
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        wheels.extend(list(dist_dir.glob("*.whl")))

    if wheels:
        print("📦 Built wheels:")
        for wheel in wheels:
            print(f"  - {wheel.name}")
    else:
        print("⚠️  No wheels found!")

    return wheels


def publish_to_pypi(wheels: list[Path], project_root: Path) -> int:
    """Publish wheels to PyPI using twine."""
    if not wheels:
        print("❌ No wheel files found to publish!")
        return 1

    print("🚀 Publishing to PyPI...")

    # Convert wheel paths to strings for twine
    wheel_paths = [str(wheel) for wheel in wheels]

    exit_code = run_command(
        [
            sys.executable,
            "-m",
            "twine",
            "upload",
            *wheel_paths,
            "--verbose",
        ],
        cwd=project_root,
    )

    if exit_code != 0:
        print("❌ Publishing failed!")
        return exit_code

    print("✅ Successfully published to PyPI!")
    print("📋 Users can now install with: pip install polars-indicator")
    return 0


def main():
    """Main build and publish process."""
    project_root = Path(__file__).parent

    print("🚀 Building and publishing polars-indicator to PyPI...")

    # Clean previous builds
    clean_previous_builds(project_root)

    # Build wheel
    exit_code = build_wheel(project_root)
    if exit_code != 0:
        return exit_code

    # List built wheels
    wheels = list_built_wheels(project_root)

    # Publish to PyPI
    exit_code = publish_to_pypi(wheels, project_root)
    return exit_code


def build_only():
    """Build wheel only (without publishing)."""
    project_root = Path(__file__).parent

    print("🔨 Building polars-indicator wheel...")

    # Clean previous builds
    clean_previous_builds(project_root)

    # Build wheel
    exit_code = build_wheel(project_root)
    if exit_code != 0:
        return exit_code

    # List built wheels
    list_built_wheels(project_root)
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Build and/or publish polars-indicator package"
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Only build the wheel without publishing",
    )

    args = parser.parse_args()

    if args.build_only:
        sys.exit(build_only())
    else:
        sys.exit(main())
