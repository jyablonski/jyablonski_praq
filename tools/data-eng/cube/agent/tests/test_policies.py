import unittest

from policies import PolicyViolation, validate_and_normalize_query


META = {
    "cubes": [
        {
            "name": "orders",
            "public": True,
            "isVisible": True,
            "measures": [
                {
                    "name": "orders.monthly_revenue",
                    "public": True,
                    "isVisible": True,
                }
            ],
            "dimensions": [
                {
                    "name": "orders.order_date",
                    "type": "time",
                    "public": True,
                    "isVisible": True,
                },
                {
                    "name": "orders.status",
                    "type": "string",
                    "public": True,
                    "isVisible": True,
                },
            ],
        }
    ]
}


class QueryPolicyTest(unittest.TestCase):
    def test_accepts_governed_query_and_caps_limit(self):
        query = validate_and_normalize_query(
            {
                "measures": ["orders.monthly_revenue"],
                "dimensions": [],
                "timeDimensions": [
                    {
                        "dimension": "orders.order_date",
                        "granularity": "month",
                    }
                ],
                "order": {"orders.order_date": "asc"},
                "limit": 500,
            },
            META,
            max_rows=100,
        )

        self.assertEqual(query["limit"], 100)
        self.assertEqual(query["timezone"], "UTC")

    def test_rejects_unknown_measure(self):
        with self.assertRaisesRegex(PolicyViolation, "Unknown or non-public measure"):
            validate_and_normalize_query(
                {"measures": ["orders.gross_profit"]},
                META,
                max_rows=100,
            )

    def test_rejects_unselected_order_member(self):
        with self.assertRaisesRegex(PolicyViolation, "must be selected"):
            validate_and_normalize_query(
                {
                    "measures": ["orders.monthly_revenue"],
                    "order": {"orders.status": "asc"},
                },
                META,
                max_rows=100,
            )

    def test_rejects_arbitrary_query_fields(self):
        with self.assertRaisesRegex(PolicyViolation, "Unsupported query fields"):
            validate_and_normalize_query(
                {
                    "measures": ["orders.monthly_revenue"],
                    "sql": "DROP TABLE gold.fct_orders",
                },
                META,
                max_rows=100,
            )


if __name__ == "__main__":
    unittest.main()
