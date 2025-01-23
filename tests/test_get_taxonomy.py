"""
Tests  get_reports/get_taxonomy.py
"""

import json
import unittest
from unittest import mock
import get_reports.get_taxonomy


class TestGetTaxonomy(unittest.TestCase):
    def test_ebird_taxonomy(self):
        """tests the function with that name"""
        test_json = {"comName": "value"}
        with mock.patch(
            "get_reports.get_taxonomy.get_taxonomy"
        ) as mock_get_taxonomy:
            mock_get_taxonomy.return_value = test_json
            taxonomy = get_reports.get_taxonomy.ebird_taxonomy()
            self.assertEqual(taxonomy, test_json)
