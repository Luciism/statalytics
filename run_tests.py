import os
import unittest

from statalib.common import REL_PATH

from dotenv import load_dotenv
load_dotenv(f"{REL_PATH}/.env.test")

failures = 0

def run_test_suite(start_dir: str) -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir)

    print(f"Running: {start_dir}")
    test_result = unittest.TextTestRunner().run(suite)

    return len(test_result.failures)

failures += run_test_suite("tests/test_statalib")
if os.path.exists("apps/website/tests"):
    failures += run_test_suite("apps/website/tests/")

if failures > 0:
    exit(1)
