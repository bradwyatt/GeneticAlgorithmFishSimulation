import os
import sys
import time


def adjust_to_correct_appdir() -> None:
    try:
        app_path = sys.argv[0]
        if not app_path:
            raise ValueError("Missing app path.")

        appdir = os.path.abspath(os.path.dirname(app_path))
        os.chdir(appdir)

        if appdir not in sys.path:
            sys.path.insert(0, appdir)
    except Exception:
        print("Please run from an OS console.")
        time.sleep(10)
        sys.exit(1)
