#!/usr/bin/env python3
"""
Main CLI for Finland Job Market Visualizer data pipeline.
Orchestrates core data processing scripts.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

# Get the root directory (where this script is located)
ROOT_DIR = Path(__file__).parent.resolve()
SRC_DIR = ROOT_DIR / "src"


def run_script(script_path, args=None):
    """Run a Python script as a subprocess."""
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    return result.returncode


def cmd_fetch(args):
    """Fetch data from StatFin and optionally Barometer."""
    print("=== Fetching StatFin data ===")
    statfin_args = ["--config", "data/statfin_config.json"]
    if args.config:
        statfin_args = ["--config", args.config]

    returncode = run_script(SRC_DIR / "fetch_statfin.py", statfin_args)
    if returncode != 0:
        print(f"Error: fetch_statfin.py failed with code {returncode}")
        return returncode

    if args.barometer_input:
        if not os.path.exists(args.barometer_input):
            print(f"Warning: Barometer CSV file not found: {args.barometer_input}")
            print("Barometer data is optional. Skipping barometer processing.")
            print("The pipeline will use existing extras.csv for outlook data.")
            # Skip barometer processing but continue with pipeline
        else:
            print("\n=== Fetching Barometer outlook ===")
            barometer_args = [
                "--input",
                args.barometer_input,
                "--output",
                args.barometer_output or "data/barometer_outlook.csv",
                "--code-column",
                args.code_column or "isco_code",
                "--outlook-desc-column",
                args.outlook_desc_column or "balance_label",
            ]
            if args.outlook_pct_column:
                barometer_args.extend(["--outlook-pct-column", args.outlook_pct_column])

            returncode = run_script(SRC_DIR / "fetch_barometer.py", barometer_args)
            if returncode != 0:
                print(f"Error: fetch_barometer.py failed with code {returncode}")
                return returncode

    return 0


def cmd_infer(args):
    """Infer missing pay and AI exposure."""
    print("=== Inferring missing pay data ===")
    returncode = run_script(ROOT_DIR / "infer_missing_pay.py")
    if returncode != 0:
        print(f"Error: infer_missing_pay.py failed with code {returncode}")
        return returncode

    print("\n=== Inferring AI exposure ===")
    returncode = run_script(ROOT_DIR / "infer_ai_exposure.py")
    if returncode != 0:
        print(f"Error: infer_ai_exposure.py failed with code {returncode}")
        return returncode

    return 0


def cmd_build(args):
    """Build site data."""
    print("=== Building site data ===")
    build_args = []
    if args.tree_level:
        os.environ["TREE_LEVEL"] = str(args.tree_level)

    returncode = run_script(SRC_DIR / "build_site_data.py", build_args)
    return returncode


def cmd_process(args):
    """Process HTML files and generate prompts (deprecated US data)."""
    print("=== Processing HTML files to Markdown ===")
    process_args = []
    if args.force:
        process_args.append("--force")

    returncode = run_script(ROOT_DIR / "process.py", process_args)
    if returncode != 0:
        print(f"Error: process.py failed with code {returncode}")
        return returncode

    print("\n=== Generating LLM prompt ===")
    returncode = run_script(ROOT_DIR / "make_prompt.py")
    return returncode


def cmd_all(args):
    """Run the complete pipeline."""
    print("Running complete data pipeline...")

    # Step 1: Fetch
    fetch_parser = argparse.ArgumentParser()
    fetch_args = fetch_parser.parse_args([])
    fetch_args.config = args.config
    fetch_args.barometer_input = args.barometer_input
    fetch_args.barometer_output = args.barometer_output
    fetch_args.code_column = args.code_column
    fetch_args.outlook_desc_column = args.outlook_desc_column
    fetch_args.outlook_pct_column = args.outlook_pct_column

    returncode = cmd_fetch(fetch_args)
    if returncode != 0:
        return returncode

    # Step 2: Build initial (for statistics)
    print("\n=== Building initial site data (for statistics) ===")
    build_parser = argparse.ArgumentParser()
    build_args = build_parser.parse_args([])
    build_args.tree_level = args.tree_level
    returncode = cmd_build(build_args)
    if returncode != 0:
        return returncode

    # Step 3: Infer
    infer_parser = argparse.ArgumentParser()
    infer_args = infer_parser.parse_args([])
    returncode = cmd_infer(infer_args)
    if returncode != 0:
        return returncode

    # Step 4: Build final (with inferred data)
    print("\n=== Building final site data ===")
    returncode = cmd_build(build_args)
    if returncode != 0:
        return returncode

    print("Pipeline completed successfully!")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Finland Job Market Visualizer - Data Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch StatFin data only
  finlandjobs fetch
  
  # Fetch with Barometer outlook
  finlandjobs fetch --barometer-input barometer.csv
  
  # Infer missing data
  finlandjobs infer
  
  # Build site data
  finlandjobs build
  
  # Run complete pipeline
  finlandjobs all --barometer-input barometer.csv
  
  (Note: The finlandjobs script automatically detects and uses the project's virtual environment. Run from the project directory. To use 'jobs' as a command, create an alias: alias jobs=finlandjobs. Note that the shell builtin 'jobs' may interfere; use 'command jobs' to bypass.)
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Fetch command
    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch data from StatFin and optionally Barometer"
    )
    fetch_parser.add_argument(
        "--config",
        help="Path to StatFin config JSON (default: data/statfin_config.json)",
    )
    fetch_parser.add_argument("--barometer-input", help="Path to Barometer CSV file")
    fetch_parser.add_argument(
        "--barometer-output", help="Output path for Barometer outlook CSV"
    )
    fetch_parser.add_argument(
        "--code-column", help="Column name for occupation codes in Barometer CSV"
    )
    fetch_parser.add_argument(
        "--outlook-desc-column", help="Column name for outlook description"
    )
    fetch_parser.add_argument(
        "--outlook-pct-column", help="Column name for outlook percentage"
    )
    fetch_parser.set_defaults(func=cmd_fetch)

    # Infer command
    infer_parser = subparsers.add_parser(
        "infer", help="Infer missing pay and AI exposure"
    )
    infer_parser.set_defaults(func=cmd_infer)

    # Build command
    build_parser = subparsers.add_parser("build", help="Build site data")
    build_parser.add_argument(
        "--tree-level",
        type=int,
        default=4,
        help="Hierarchy level for treemap (default: 4)",
    )
    build_parser.set_defaults(func=cmd_build)

    # Process command (deprecated US data)
    process_parser = subparsers.add_parser(
        "process", help="Process HTML files and generate prompts (deprecated US data)"
    )
    process_parser.add_argument(
        "--force", action="store_true", help="Re-process even if .md exists"
    )
    process_parser.set_defaults(func=cmd_process)

    # All command
    all_parser = subparsers.add_parser(
        "all",
        help="Run complete pipeline (fetch + initial build + infer + final build)",
    )
    all_parser.add_argument("--config", help="Path to StatFin config JSON")
    all_parser.add_argument("--barometer-input", help="Path to Barometer CSV file")
    all_parser.add_argument(
        "--barometer-output", help="Output path for Barometer outlook CSV"
    )
    all_parser.add_argument("--code-column", help="Column name for occupation codes")
    all_parser.add_argument(
        "--outlook-desc-column", help="Column name for outlook description"
    )
    all_parser.add_argument(
        "--outlook-pct-column", help="Column name for outlook percentage"
    )
    all_parser.add_argument(
        "--tree-level", type=int, default=4, help="Hierarchy level for treemap"
    )
    all_parser.set_defaults(func=cmd_all)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
