import unittest
import logging
from process_emails import query_builder

# Configure logging
logger = logging.getLogger("tests")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class Tests(unittest.TestCase):

    def test_query_builder_contains(self):
        rules = {
            "conditions_to_check": "All",
            "conditions": [
                {"field": "from", "type": "contains", "value": "test@example.com"}
            ],
            "actions": []
        }

        expected_snippet = "from_email LIKE '%test@example.com%'"
        logger.info("Testing query_builder with 'contains' condition")
        logger.debug("Input rules: %s", rules)

        query = query_builder(rules)
        logger.debug("Generated query: %s", query)

        self.assertIn(expected_snippet, query)
        logger.info("Test passed: 'contains' condition is correctly handled.")

if __name__ == "__main__":
    unittest.main()


