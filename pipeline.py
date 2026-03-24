#!/usr/bin/env python3
"""
Finland Job Market Visualizer - Complete Pipeline

This script documents and executes the complete data pipeline for analyzing
AI exposure of the Finnish job market. It follows the adapted methodology
from the original karpathy/jobs project.

Pipeline steps:
1. Fetch StatFin data (employment, wages, outlook)
2. Optional: Fetch Occupational Barometer outlook data
3. Infer missing pay data
4. Score AI exposure with LLM (Gemini Flash via OpenRouter)
5. Build site data for visualization
6. Optional: Generate prompt.md for LLM analysis

Usage:
    uv run python pipeline.py              # Run all steps
    uv run python pipeline.py --step 1     # Run specific step only
    uv run python pipeline.py --list       # List all steps
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_step(step_num, description, command, required=True):
    """Run a pipeline step and return success status."""
    print(f"\n{'=' * 60}")
    print(f"Step {step_num}: {description}")
    print(f"{'=' * 60}")
    print(f"Command: {command}")

    try:
        result = subprocess.run(command, shell=True, check=required)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error in step {step_num}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Finland Job Market pipeline")
    parser.add_argument("--step", type=int, help="Run specific step only (1-6)")
    parser.add_argument("--list", action="store_true", help="List all pipeline steps")
    args = parser.parse_args()

    pipeline_steps = [
        (
            1,
            "Fetch StatFin data",
            "uv run python src/fetch_statfin.py --config data/statfin_config.json",
        ),
        (
            2,
            "Fetch Barometer outlook (optional)",
            "uv run python src/fetch_barometer.py --input barometer.csv --output data/barometer_outlook.csv --code-column isco_code --outlook-desc-column balance_label",
        ),
        (3, "Infer missing pay data", "uv run python infer_missing_pay.py"),
        (
            4,
            "Score AI exposure with LLM (Gemini Flash) - requires OPENROUTER_API_KEY",
            "uv run python src/score.py --model google/gemini-3-flash-preview",
        ),
        (5, "Build site data", "uv run python src/build_site_data.py"),
        (6, "Generate LLM prompt (optional)", "uv run python make_prompt.py"),
    ]

    if args.list:
        print("Finland Job Market Pipeline Steps:")
        print("-" * 60)
        for num, desc, cmd in pipeline_steps:
            print(f"{num}. {desc}")
            print(f"   {cmd}")
        return 0

    if args.step:
        # Run single step
        step = next((s for s in pipeline_steps if s[0] == args.step), None)
        if not step:
            print(f"Invalid step number: {args.step}")
            return 1
        success = run_step(step[0], step[1], step[2])
        return 0 if success else 1

    # Run all steps
    print("Finland Job Market Visualizer - Complete Pipeline")
    print("This pipeline processes Finnish occupation data for AI exposure analysis")
    print("\nBased on methodology from: https://github.com/karpathy/jobs")
    print("Adapted for Finnish data sources: StatFin PxWeb + Occupational Barometer")

    results = []
    for num, desc, cmd in pipeline_steps:
        # Skip optional barometer step if no file exists
        if num == 2 and not os.path.exists("barometer.csv"):
            print(f"\n{'=' * 60}")
            print(f"Step {num}: {desc}")
            print(f"{'=' * 60}")
            print("Skipping: barometer.csv not found")
            print(
                "Barometer data is optional. The pipeline will use extras.csv for outlook."
            )
            results.append(True)
            continue

        success = run_step(num, desc, cmd, required=(num != 2))  # Barometer is optional
        results.append(success)

        if not success and num != 2:  # Stop if required step fails
            print(f"\nPipeline failed at step {num}. Stopping.")
            break

    # Summary
    print(f"\n{'=' * 60}")
    print("PIPELINE SUMMARY")
    print(f"{'=' * 60}")
    for i, (num, desc, _) in enumerate(pipeline_steps):
        status = "✓" if i < len(results) and results[i] else "✗"
        print(f"{status} Step {num}: {desc}")

    if all(results):
        print("\n✓ All steps completed successfully!")
        print("\nNext steps:")
        print("1. View the visualization: cd site && python -m http.server 8000")
        print("2. Or run the CLI: finlandjobs build")
        return 0
    else:
        print("\n✗ Pipeline completed with errors.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
