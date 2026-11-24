"""Standalone tests. Run: python -m unittest discover -s tests -v"""
import importlib.util
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "lambda" / "lambda_function.py"
spec = importlib.util.spec_from_file_location("presignup", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def event(email=None):
    attrs = {} if email is None else {"email": email}
    return {"triggerSource": "PreSignUp_SignUp",
            "request": {"userAttributes": attrs}, "response": {}}


class TestCognitoPreSignUp(unittest.TestCase):
    def test_allow(self):
        e = event("student@example.com")
        self.assertIs(module.lambda_handler(e, None), e)

    def test_block(self):
        with self.assertRaisesRegex(ValueError, "Registration is not permitted"):
            module.lambda_handler(event("attacker@blocked.example"), None)

    def test_block_case_insensitive(self):
        with self.assertRaisesRegex(ValueError, "Registration is not permitted"):
            module.lambda_handler(event(" Attacker@BLOCKED.Example "), None)

    def test_missing_email(self):
        with self.assertRaisesRegex(ValueError, "Email address is required"):
            module.lambda_handler(event(), None)


if __name__ == "__main__":
    unittest.main()
