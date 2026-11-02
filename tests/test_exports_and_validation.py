"""Exercise CSV validation and isolated historical exports."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import analyze


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = analyze.load_data()

    def assert_rejected(self, message):
        def read_csv(path):
            return self.data[Path(path).stem].copy()
        with patch.object(analyze.pd, 'read_csv', side_effect=read_csv):
            with self.assertRaisesRegex(ValueError, message):
                analyze.load_data()

    def test_duplicate_stock_id(self):
        self.data['vehicles'].loc[1, 'stock_id'] = self.data['vehicles'].loc[0, 'stock_id']
        self.assert_rejected('duplicate IDs')

    def test_missing_value(self):
        self.data['vehicles'].loc[0, 'location'] = None
        self.assert_rejected('missing values')

    def test_mismatched_purchase_keys(self):
        self.data['purchases'].loc[0, 'stock_id'] = 'UNKNOWN'
        self.assert_rejected('Vehicle/purchase keys differ')

    def test_unknown_sale(self):
        self.data['sales'].loc[0, 'stock_id'] = 'UNKNOWN'
        self.assert_rejected('Unknown sold vehicle')

    def test_nonpositive_prices(self):
        for table, column in [('purchases', 'acquisition_cost_cad'),
                              ('purchases', 'asking_price_cad'),
                              ('sales', 'sale_price_cad')]:
            original = self.data[table].loc[0, column]
            for value in [0, -1]:
                with self.subTest(table=table, column=column, value=value):
                    self.data[table].loc[0, column] = value
                    self.assert_rejected('Nonpositive price')
            self.data[table].loc[0, column] = original

    def test_sale_before_acquisition(self):
        self.data['sales'].loc[0, 'sold_date'] = '2025-01-01'
        self.assert_rejected('Sale before acquisition')

    def test_invalid_date(self):
        self.data['purchases'].loc[0, 'acquired_date'] = '2026-02-30'
        self.assert_rejected('.*')

    def test_noncanonical_dates(self):
        for table, column in [('purchases', 'acquired_date'), ('sales', 'sold_date')]:
            original = self.data[table].loc[0, column]
            for value in ['2026-1-2', '2026-01-02 00:00:00', '2026/01/02']:
                with self.subTest(table=table, value=value):
                    self.data[table].loc[0, column] = value
                    self.assert_rejected('YYYY-MM-DD')
            self.data[table].loc[0, column] = original

    def test_nonfinite_and_nonnumeric_prices(self):
        for table, column in [('purchases', 'acquisition_cost_cad'),
                              ('purchases', 'asking_price_cad'),
                              ('sales', 'sale_price_cad')]:
            original = self.data[table][column].copy()
            self.data[table][column] = self.data[table][column].astype(object)
            for value in [float('inf'), float('-inf'), 'unknown']:
                with self.subTest(table=table, column=column, value=value):
                    self.data[table].loc[0, column] = value
                    self.assert_rejected('finite numeric')
            self.data[table][column] = original

    def test_snapshot_rejects_noncanonical_or_impossible_date(self):
        for value in ['2026-1-2', '2026-02-30', '2026-10-20 00:00:00', None]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'YYYY-MM-DD'):
                    analyze.snapshot(self.data, value)


class ExportTests(unittest.TestCase):
    def test_cli_historical_export_preserves_published_results(self):
        published = analyze.ROOT / 'results'
        before = {p.name: p.read_bytes() for p in published.glob('*') if p.is_file()}
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run(
                [sys.executable, str(analyze.ROOT / 'analyze.py'),
                 '--as-of', '2026-06-30', '--output-dir', 'nested/history'],
                cwd=temp, check=True, capture_output=True, text=True)
            out = Path(temp) / 'nested/history'
            self.assertEqual({p.name for p in out.iterdir()}, {
                'snapshot.csv', 'review_queue.csv', 'aging_summary.csv',
                'segment_summary.csv', 'summary.json'})
            summary = json.loads((out / 'summary.json').read_text())
            snapshot = pd.read_csv(out / 'snapshot.csv')
            active = snapshot[snapshot.is_open == 1]
            self.assertEqual(summary['as_of'], '2026-06-30')
            self.assertEqual(summary['open_vehicles'], len(active))
            self.assertEqual(summary['open_cost_cad'], active.acquisition_cost_cad.sum())
            self.assertTrue((snapshot.acquired_date <= '2026-06-30').all())
        after = {p.name: p.read_bytes() for p in published.glob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_empty_snapshot_exports_null_metrics_and_headers(self):
        with tempfile.TemporaryDirectory() as temp:
            with contextlib.redirect_stdout(io.StringIO()):
                summary = analyze.main('2025-01-01', output_dir=temp)
            self.assertEqual(summary['vehicles_acquired'], 0)
            self.assertIsNone(summary['median_open_age_days'])
            self.assertIsNone(summary['over_90_share_pct'])
            self.assertTrue(pd.read_csv(Path(temp) / 'snapshot.csv').empty)
            aging = pd.read_csv(Path(temp) / 'aging_summary.csv')
            self.assertEqual(len(aging), 4)
            self.assertEqual(aging.units.sum(), 0)
            self.assertEqual(json.loads((Path(temp) / 'summary.json').read_text()), summary)


if __name__ == '__main__':
    unittest.main()

