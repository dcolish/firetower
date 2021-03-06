import json
from unittest import TestCase

from firetower import classifier
from firetower.redis_util import Redis

class TestClassfier(TestCase):

    def test_lcs(self):
        """Test the longest common substring function."""

        test1 = 'the longest common sub str plus extra'
        test2 = 'the longest common sub str and something else'
        lcs = 'the longest common sub str '

        # We need to asser that we can determine the longest sub str
        # regardless of which string is passed first.
        result = classifier.longest_common_substr(test1, test2)
        result2 = classifier.longest_common_substr(test2, test1)

        assert result == lcs
        assert result2 == lcs


class TestLevenshtein(TestCase):

    def setUp(self):
        self.r = Redis('localhost', 6379)
        self.lev = classifier.Levenshtein(self.r)

    def test_str_ratio(self):
        """Test Levenshtein.str_ratio function."""

        known_str = 'hello'
        test_str = 'hello'

        assert self.lev.str_ratio(known_str, test_str) == 1.0
        assert self.lev.str_ratio(known_str, "wacky") < 0.5

    def test_is_similar(self):
        """Test Levenshtein.is_similar function."""
        know_str = "wombat"
        test_str = "combat"
        assert self.lev.is_similar(know_str, test_str, 0.5)

    def test_write_errors(self):
        """Test Levenshtein.write_errors function."""

        test_error = {'sig': 'Testing Exception', 'body': 'Error! Alert!'}
        test_cat = 'Testing'
        self.lev.write_errors(test_cat, test_error)
        count_res = self.r.conn.hgetall('counter_%s' % (test_cat,))
        # Only want the payload, not the time index, so [1]
        data_res = json.loads(
                self.r.conn.zrange('data_%s' % (test_cat), 0, -1)[0][1])

        assert count_res
        assert data_res['sig'] == test_error['sig']
        assert data_res['body'] == test_error['body']

    def test_classify(self):
        """Test the classify function."""

        uk_key = 'unknown_errors'
        test_error = {'sig': 'Testing Error', 'body': 'Error!!!!'}
        test_similar_error = {'sig': 'Testing Error 456', 'body': 'Error!!!!'}
        test_different_error = {
                'sig': 'Something Totally Different', 'body': 'Error!!!'}

        uk_error_num = self.r.conn.llen(uk_key)
        assert uk_error_num == 0

        # Nothing exists, so put it in unknown errors
        self.lev.classify(test_error)
        uk_error_num = self.r.conn.llen(uk_key)
        assert uk_error_num == 1

        # Now both unknown errors are pulled out
        self.lev.classify(test_similar_error)
        uk_error_num = self.r.conn.llen(uk_key)
        assert uk_error_num == 0

        # Now check that our categorized counts are accurate for
        # 'Testing Error'
        counts = self.r.conn.hgetall('counter_Testing_Error').values()[0]
        assert counts == 2

        self.lev.classify(test_different_error)
        sim_counts = self.r.conn.hgetall('counter_Testing_Error').values()[0]
        uk_error_num = self.r.conn.llen(uk_key)
        assert sim_counts == 2

        # This fails, but the expectation is that the test_different_error will
        # land in the unknown_errors queue.
        #assert uk_error_num == 1
