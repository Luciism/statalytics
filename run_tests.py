import unittest

loader = unittest.TestLoader()

def run_test_suite(start_dir: str) -> None:
    suite = loader.discover(start_dir)
    print(f"Running: {start_dir}")
    unittest.TextTestRunner().run(suite)

run_test_suite("tests/test_statalib")
run_test_suite("tests/test_statalib/test_rotational")
