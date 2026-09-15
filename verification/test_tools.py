"""Resolve independent-test tools on the workstation and macOS CI runners."""
import os
from pathlib import Path
import shutil

NODE = os.environ.get('TRACKER_TEST_NODE') or shutil.which('node') or '/opt/homebrew/opt/node@22/bin/node'
_chrome = os.environ.get('TRACKER_TEST_CHROME') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROME = _chrome if Path(_chrome).is_file() else None
