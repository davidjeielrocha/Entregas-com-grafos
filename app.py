"""
Servidor web da solução (Flask).

    python app.py                      -> http://127.0.0.1:5000
    python app.py --host 0.0.0.0 --port 8080 --debug
"""

import argparse

from web import criar_app

app = criar_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface web - Transporte de Carlos")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
