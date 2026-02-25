from datetime import datetime, timezone, timedelta
import sys

KST = timezone(timedelta(hours=9))  # 한국 표준시 UTC+9

class PipelineLogger:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def log_event(self, stage: str, message: str):
        if not self.verbose:
            return

        # 한국 표준시 기준 시간
        timestamp = datetime.now(KST).isoformat()
        print(f"[{timestamp}] [{stage}] {message}")
        sys.stdout.flush()