import unittest

import torch

from src.nodes.common import combine_reference_batches


class CombineReferenceBatchesTest(unittest.TestCase):
    def test_resizes_mismatched_references_to_target_size(self):
        first = torch.zeros((477, 434, 3), dtype=torch.float32)
        second = torch.zeros((1424, 750, 3), dtype=torch.float32)

        batch = combine_reference_batches(first, second, target_size=(512, 512))

        self.assertEqual(tuple(batch.shape), (2, 512, 512, 3))
        self.assertEqual(batch.dtype, torch.float32)

    def test_returns_none_without_references(self):
        self.assertIsNone(combine_reference_batches(None, None))


if __name__ == "__main__":
    unittest.main()
