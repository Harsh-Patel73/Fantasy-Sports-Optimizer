"""
BetterBets - Sports Betting Line Comparison Tool

Usage:
    python main.py              # Fetch data, then start web server
    python main.py --no-fetch   # Start web server only (skip data fetch)
    python main.py --fetch-only # Fetch data only (no server)
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


def fetch_data():
    """Fetch data from all configured API sources."""
    from app.db import setup_database
    from app.data_sources import sync_all_data

    print("=" * 50)
    print("SETTING UP DATABASE")
    print("=" * 50)
    setup_database()

    print("\n" + "=" * 50)
    print("FETCHING DATA FROM APIs")
    print("=" * 50)
    sync_all_data()
    print("\nData fetch complete.")


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
  python main.py              Fetch data and start server
  python main.py --no-fetch   Start server only (use existing data)
  python main.py --fetch-only Fetch data only (no server)

Legacy flags (still supported):
  python main.py --no-scrape  Same as --no-fetch
  python main.py --scrape-only Same as --fetch-only
        """
    )
    parser.add_argument(
        '--no-fetch',
        action='store_true',
        help='Skip data fetching, just start the web server'
    )
    parser.add_argument(
        '--fetch-only',
        action='store_true',
        help='Only fetch data, do not start the server'
    )
    # Legacy support
    parser.add_argument(
        '--no-scrape',
        action='store_true',
        help=argparse.SUPPRESS  # Hidden, for backwards compatibility
    )
    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help=argparse.SUPPRESS  # Hidden, for backwards compatibility
    )
    args = parser.parse_args()

    # Handle legacy flags
    skip_fetch = args.no_fetch or args.no_scrape
    fetch_only = args.fetch_only or args.scrape_only

    print("\n" + "=" * 50)
    print("BETTERBETS")
    print("=" * 50 + "\n")

    # Fetch data unless --no-fetch flag is set
    if not skip_fetch:
        fetch_data()

    # Start server unless --fetch-only flag is set
    if not fetch_only:
        build_frontend()
        start_server()


if __name__ == '__main__':
    main()
