import unittest

from etsyv3.util.auth import AuthHelper


class TestAuthHelper(unittest.TestCase):
    def test__generate_challenge(self):
        code_verifier = "vvkdljkejllufrvbhgeiegrnvufrhvrffnkvcknjvfid"
        code_challenge = AuthHelper._generate_challenge(code_verifier)
        code_challenge_expected = "DSWlW2Abh-cf8CeLL8-g3hQ2WQyYdKyiu83u_s7nRhI"
        self.assertEqual(code_challenge, code_challenge_expected)
