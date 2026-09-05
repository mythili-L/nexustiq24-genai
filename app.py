from http.server import BaseHTTPRequestHandler, HTTPServer
import html

from risk_engine import analyze_transactions
from gemini_service import generate_investigation_report


# ==============================
# Configuration
# ==============================

HOST = "0.0.0.0"
PORT = 8000

TRANSACTION_FILE = "data/transactions.csv"


# ==============================
# HTML Page
# ==============================

def build_page(report=None, error=None):

    report_html = ""

    if report:
        report_html = f"""
        <section class="report">
            <h2>Investigation Report</h2>
            <pre>{html.escape(report)}</pre>
        </section>
        """

    error_html = ""

    if error:
        error_html = f"""
        <section class="error">
            <strong>Error:</strong>
            {html.escape(str(error))}
        </section>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>RiskLens</title>

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                color: #1f2937;
            }}

            .container {{
                max-width: 1000px;
                margin: 0 auto;
                padding: 40px 20px;
            }}

            .header {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}

            h1 {{
                margin-top: 0;
                margin-bottom: 8px;
            }}

            .subtitle {{
                color: #6b7280;
                margin-bottom: 25px;
            }}

            button {{
                background: #111827;
                color: white;
                border: none;
                padding: 13px 22px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
            }}

            button:hover {{
                opacity: 0.9;
            }}

            .report {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}

            .report h2 {{
                margin-top: 0;
            }}

            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                line-height: 1.6;
                font-family: Arial, sans-serif;
            }}

            .error {{
                background: #fee2e2;
                color: #991b1b;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}

            .architecture {{
                margin-top: 25px;
                background: white;
                padding: 25px;
                border-radius: 12px;
            }}

            .architecture code {{
                display: block;
                background: #f3f4f6;
                padding: 15px;
                border-radius: 8px;
                line-height: 1.8;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <div class="header">

                <h1>RiskLens</h1>

                <div class="subtitle">
                    Transaction Risk Investigation Assistant
                </div>

                <p>
                    Analyze customer transaction history using
                    deterministic risk rules and grounded Gemini
                    investigation reports.
                </p>

                <form method="POST">

                    <button type="submit">
                        Analyze Transactions
                    </button>

                </form>

            </div>

            {error_html}

            {report_html}

            <div class="architecture">

                <h2>How RiskLens Works</h2>

                <code>
                    Transaction History<br>
                    ↓<br>
                    Deterministic Risk Engine<br>
                    ↓<br>
                    Evidence<br>
                    ↓<br>
                    Gemini Investigation Report<br>
                    ↓<br>
                    Human Investigator
                </code>

            </div>

        </div>

    </body>
    </html>
    """


# ==============================
# Web Server
# ==============================

class RiskLensHandler(BaseHTTPRequestHandler):

    def send_html(self, content):

        encoded_content = content.encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(encoded_content))
        )

        self.end_headers()

        self.wfile.write(encoded_content)


    # --------------------------
    # GET request
    # --------------------------

    def do_GET(self):

        page = build_page()

        self.send_html(page)


    # --------------------------
    # POST request
    # --------------------------

    def do_POST(self):

        try:

            # Step 1:
            # Run deterministic risk analysis

            evidence = analyze_transactions(
                TRANSACTION_FILE
            )

            # Step 2:
            # Send only deterministic evidence to Gemini

            report = generate_investigation_report(
                evidence
            )

            # Step 3:
            # Display Gemini report

            page = build_page(
                report=report
            )

            self.send_html(page)

        except Exception as error:

            page = build_page(
                error=error
            )

            self.send_html(page)


# ==============================
# Start Application
# ==============================

def start_server():

    server = HTTPServer(
        (HOST, PORT),
        RiskLensHandler
    )

    print("=" * 60)
    print("RiskLens Transaction Risk Investigation Assistant")
    print("=" * 60)
    print()
    print(f"Server running at: http://localhost:{PORT}")
    print()
    print("Press Ctrl+C to stop the server.")
    print()

    server.serve_forever()


# ==============================
# Main
# ==============================

if __name__ == "__main__":

    start_server()