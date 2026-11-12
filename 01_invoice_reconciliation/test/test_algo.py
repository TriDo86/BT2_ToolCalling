from unittest import TestCase

from app.algorithm import two_sum

# Vibe code testcases
# py -m unittest discover -s test -p "test_algo.py" -v
class TwoSumTests(TestCase):
    def test_finds_pair_including_index_zero(self):
        result = two_sum(1_500_000, [900_000, 600_000])
        self.assertEqual(result, (0, 1))

    def test_one_transfer_cannot_match_itself(self):
        result = two_sum(1_500_000, [750_000])
        self.assertEqual(result, (None, None))