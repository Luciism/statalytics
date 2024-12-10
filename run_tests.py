import unittest

from statalib.common import REL_PATH

from dotenv import load_dotenv
load_dotenv(f"{REL_PATH}/.env.test")

loader = unittest.TestLoader()

failures = 0

def run_test_suite(start_dir: str) -> int:
    suite = loader.discover(start_dir)
    print(f"Running: {start_dir}")
    test_result = unittest.TextTestRunner().run(suite)

    return len(test_result.failures)

failures += run_test_suite("tests/test_statalib")
# failures += run_test_suite("tests/test_statalib/test_rotational")
# failures += run_test_suite("tests/test_statalib/test_accounts")

if failures > 0:
    exit(1)
