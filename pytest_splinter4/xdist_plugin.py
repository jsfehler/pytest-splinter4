import logging
import os


LOGGER = logging.getLogger(__name__)


class SplinterXdistPlugin:
    """Plugin to defer pytest-xdist hook handler."""

    def __init__(self, screenshot_dir: str):
        self.screenshot_dir = screenshot_dir

    def pytest_testnodedown(self, node, error):
        """Copy screenshots back from remote nodes to have them on the master."""
        workeroutput = getattr(node, "workeroutput", {})

        for screenshot in workeroutput.get("screenshots", []):
            screenshot_dir = os.path.join(
                self.screenshot_dir,
                screenshot["class_name"],
            )

            os.makedirs(screenshot_dir, exist_ok=True)

            for filename in screenshot["files"]:
                encoding = filename.get("encoding")
                filepath = os.path.join(screenshot_dir, filename["file_name"])

                LOGGER.info(f"Saving screenshot to: {filepath}")

                mode = 'wb'
                if encoding:
                    mode = 'w'

                with open(filepath, mode, **dict(encoding=encoding) if encoding else {}) as fd: # NOQA C408
                    fd.write(filename["content"])
