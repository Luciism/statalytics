import unittest


loader = unittest.TestLoader()

failures = {"count": 0}

def run_test_suite(start_dir: str) -> None:
    suite = loader.discover(start_dir)
    print(f"Running: {start_dir}")
    test_result = unittest.TextTestRunner().run(suite)

    failures["count"] += len(test_result.failures)

run_test_suite("tests/test_statalib")
run_test_suite("tests/test_statalib/test_rotational")

if failures["count"] > 0:
    exit(1)
