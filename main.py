"""
CLI entry point for the Photoshop Design Agent.

Usage examples:
  python main.py
  python main.py "Create a 1080x1080 Instagram post for a coffee brand"
  python main.py --doc-id 1BxiM... --reference-psd "C:/Designs/brand.psd"
  python main.py "Create a banner" --reference-psd "refs/style.psd" --quiet
"""

import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Photoshop Design Agent — AI-powered Photoshop automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "request",
        nargs="?",
        help="Design request in natural language",
    )
    parser.add_argument(
        "--doc-id",
        metavar="GOOGLE_DOC_ID",
        help="Google Document ID containing the content plan",
    )
    parser.add_argument(
        "--reference-psd",
        metavar="PATH",
        help="Path to a reference PSD file for brand style extraction",
    )
    parser.add_argument(
        "--analyze-folder",
        metavar="PATH",
        help="Folder of PSD files to analyze as a client style guide",
    )
    parser.add_argument(
        "--save-client",
        metavar="CLIENT_NAME",
        help="Save the analysis under this client name (use with --analyze-folder)",
    )
    parser.add_argument(
        "--load-client",
        metavar="CLIENT_NAME",
        help="Load a saved client style guide before creating a design",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("OUTPUT_DIR", "output"),
        metavar="DIR",
        help="Directory where designs will be saved (default: output/)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress step-by-step output",
    )

    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Error: ANTHROPIC_API_KEY is not set. Copy .env.example → .env and fill it in.")

    os.makedirs(args.output_dir, exist_ok=True)
    output_abs = os.path.abspath(args.output_dir)

    # Short-circuit: folder analysis mode
    if args.analyze_folder:
        folder_abs = os.path.abspath(args.analyze_folder)
        client = args.save_client or ""
        parts: list[str] = [
            f"Analyze all PSD files in the folder: {folder_abs}",
        ]
        if client:
            parts.append(
                f"Then save the aggregated style guide under the client name: '{client}'"
            )
        else:
            parts.append(
                "Summarize the design style you found (colors, fonts, composition patterns)."
            )
        from agent import run_agent
        result = run_agent("\n".join(parts), verbose=not args.quiet)
        print("\n" + "=" * 60)
        print("COMPLETED")
        print("=" * 60)
        print(result)
        return

    # Build the request interactively if not provided
    if not args.request and not args.doc_id:
        print("Photoshop Design Agent")
        print("=" * 40)
        args.request = input("Describe the design you want to create:\n> ").strip()
        if not args.request:
            sys.exit("No request provided.")

        if not args.doc_id:
            doc_id = input("\nGoogle Doc ID with content plan (press Enter to skip): ").strip()
            if doc_id:
                args.doc_id = doc_id

        if not args.reference_psd:
            ref = input("\nReference PSD path for style analysis (press Enter to skip): ").strip()
            if ref:
                args.reference_psd = ref

    # Assemble the full prompt
    parts: list[str] = []

    if args.request:
        parts.append(args.request)

    if args.doc_id:
        parts.append(f"The content plan is in Google Doc ID: {args.doc_id}")

    if args.load_client:
        parts.append(
            f"Load the saved style guide for client '{args.load_client}' and use it for this design."
        )

    if args.reference_psd:
        ref_abs = os.path.abspath(args.reference_psd)
        parts.append(
            f"Analyze the reference PSD at '{ref_abs}' to extract the brand style "
            "(colors, typography, composition) and apply it to the new design."
        )

    parts.append(f"Save all output files to the directory: {output_abs}")

    user_request = "\n".join(parts)

    # Run the agent
    from agent import run_agent

    result = run_agent(user_request, verbose=not args.quiet)

    print("\n" + "=" * 60)
    print("COMPLETED")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
