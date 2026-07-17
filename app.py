"""
Public HTTP wrapper around org_tracking.py

Exposes:
  GET/POST /run-tracking?key=YOUR_SECRET   -> runs the shipment sync
  GET       /                              -> health check

Deploy this anywhere (Render, Railway, PythonAnywhere, Cloud Run, etc.)
and point your external scheduler (cron-job.org, GitHub Actions cron, etc.)
at the /run-tracking URL.

IMPORTANT: Set RUN_SECRET as an environment variable on your host — this is
what stops random people on the internet from triggering your sync and
burning your API quota. Do NOT hardcode it in this file.
"""

import os
import logging
import threading
from flask import Flask, request, jsonify

import org_tracking  # your existing script, unmodified

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("tracking")

app = Flask(__name__)

# Set this in your hosting platform's environment variables, not here.
RUN_SECRET = os.environ.get("RUN_SECRET", "")

# Prevents two overlapping runs if your scheduler fires twice
_run_lock = threading.Lock()


class _LogProxy:
    """Mimics Zoho's context.log.INFO(...) by printing to stdout/logs."""
    def INFO(self, msg):
        logger.info(msg)


class _ContextStub:
    """Mimics Zoho's context object. Only .log.INFO(...) is ever used
    by org_tracking.py, so this is all we need."""
    def __init__(self):
        self.log = _LogProxy()


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/run-tracking", methods=["GET", "POST"])
def run_tracking():
    if not RUN_SECRET:
        return jsonify({"error": "RUN_SECRET not configured on server"}), 500

    key = request.args.get("key") or request.headers.get("X-Run-Key")
    if key != RUN_SECRET:
        return jsonify({"error": "unauthorized"}), 401

    if _run_lock.locked():
        return jsonify({"status": "already running, skipped"}), 429

    def _background_job():
        with _run_lock:
            try:
                ctx = _ContextStub()
                # dry_run=False means it will actually update Zoho Books.
                # Switch to True any time you want to test without writing changes.
                org_tracking.main(ctx, dry_run=False)
                logger.info("Run completed successfully")
            except Exception:
                logger.exception("Run failed")

    threading.Thread(target=_background_job, daemon=True).start()

    # Respond immediately so the caller (Deluge/invokeurl) never times out.
    # Check the Render logs to see actual progress/completion.
    return jsonify({"status": "started"}), 202


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)