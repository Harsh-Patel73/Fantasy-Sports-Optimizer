"""
BetterBets - Sports Betting Line Comparison Tool

Usage:
    python main.py              # Scrape data, then start web server
    python main.py --no-scrape  # Start web server only (skip scraping)
    python main.py --scrape-only # Run scrapers only (no server)
"""
import argparse
import subprocess
import sys
import os


def build_frontend():
    """Build React frontend if not already built or if source is newer."""
    static_dir = os.path.join('app', 'static')
    index_file = os.path.join(static_dir, 'index.html')

    # Check if build exists
    if not os.path.exists(index_file):
        print("Building frontend...")
        try:
            # Install dependencies if node_modules doesn't exist
            node_modules = os.path.join('frontend', 'node_modules')
            if not os.path.exists(node_modules):
                print("Installing frontend dependencies...")
                subprocess.run(['npm', 'install'], cwd='frontend', check=True, shell=True)

            # Build the frontend
            subprocess.run(['npm', 'run', 'build'], cwd='frontend', check=True, shell=True)
            print("Frontend build complete.")
        except subprocess.CalledProcessError as e:
            print(f"Frontend build failed: {e}")
            print("You may need to install Node.js or run 'npm install' in the frontend directory.")
            sys.exit(1)
        except FileNotFoundError:
            print("npm not found. Please install Node.js to build the frontend.")
            print("Alternatively, run the frontend separately with 'npm run dev' in the frontend directory.")
            sys.exit(1)
    else:
        print("Frontend already built. Use 'npm run build' in frontend/ to rebuild.")


def run_scrapers():
    """Run all data scrapers."""
    from app.db import setup_database
    from app.scrapers import run_all_scrapers

    print("=" * 50)
    print("SETTING UP DATABASE")
    print("=" * 50)
    setup_database()

    print("\n" + "=" * 50)
    print("RUNNING SCRAPERS")
    print("=" * 50)
    run_all_scrapers()
    print("\nScraping complete.")


def start_server():
    """Start Flask server serving API + static frontend."""
    from app.api import create_app

    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'

    print("\n" + "=" * 50)
    print("STARTING SERVER")
    print("=" * 50)
    print(f"Server running at http://localhost:{port}")
    print("Press Ctrl+C to stop.\n")

    app.run(host='0.0.0.0', port=port, debug=debug)


def main():
    parser = argparse.ArgumentParser(
        description='BetterBets - Sports Betting Line Comparison Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Run scrapers and start server
  python main.py --no-scrape  Start server only (use existing data)
  python main.py --scrape-only  Run scrapers only (no server)
        """
    )
    parser.add_argument(
        '--no-scrape',
        action='store_true',
        help='Skip scraping, just start the web server'
    )
    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help='Only run scrapers, do not start the server'
    )
    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("BETTERBETS")
    print("=" * 50 + "\n")

    # Run scrapers unless --no-scrape flag is set
    if not args.no_scrape:
        run_scrapers()

    # Start server unless --scrape-only flag is set
    if not args.scrape_only:
        build_frontend()
        start_server()


if __name__ == '__main__':
    main()
