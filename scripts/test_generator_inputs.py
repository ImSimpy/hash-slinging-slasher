"""Regression coverage for promoted helpers without private state/an seed exports."""
import struct
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import generator_inputs as inputs
import snapshot


class GeneratorInputsTests(unittest.TestCase):
    def tearDown(self):
        inputs.capture.cache_clear()
        inputs.seeds.cache_clear()
        inputs.named_names.cache_clear()

    def test_seed_name_must_rehash_into_the_requested_game_and_type(self):
        names = ['image_one', 'alias_one', 'outside_capture']
        image = snapshot.fnv1a(names[0], 'BLACKOP6', 'image') & snapshot.ID_MASK
        alias = snapshot.fnv1a(names[1], 'BLACKOP6', 'sound_alias') & snapshot.ID_MASK
        shot = SimpleNamespace(by_pool=lambda: {'image': [image], 'sound_alias': [alias]})
        with patch.object(inputs, 'capture', return_value=shot), patch.object(snapshot, 'table_names', return_value=names), patch.object(snapshot, 'confirmed_names', return_value=[]):
            self.assertEqual(inputs.named_names('BLACKOP6', 'image'), frozenset(['image_one']))
            self.assertEqual(inputs.named_names('BLACKOP6', 'sound_alias'), frozenset(['alias_one']))

    def test_select_capture_by_internal_game_and_reject_ambiguous_versions(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = []
            for game in ('BLACKOP6', 'BLACKOP7'):
                path = Path(folder) / (game + '.ids')
                path.write_bytes(b'CODIDS' + struct.pack('<HH', 1, len(game)) + game.encode() + struct.pack('<Q', 0))
                paths.append(str(path))
            with patch.object(snapshot, 'snapshots', return_value=paths), patch.object(snapshot, 'read', side_effect=lambda p: SimpleNamespace(game=Path(p).stem)) as read:
                self.assertEqual(inputs.capture('BLACKOP6').game, 'BLACKOP6')
                self.assertEqual(read.call_count, 1)
            inputs.capture.cache_clear()
            with patch.object(snapshot, 'snapshots', return_value=[paths[0], paths[0]]), patch.object(snapshot, 'read', return_value=SimpleNamespace(game='BLACKOP6')):
                with self.assertRaises(ValueError):
                    inputs.capture('BLACKOP6')

    def test_tails_are_measured_from_target_not_borrowed_from_another_title(self):
        def named(game, kind):
            if game == 'BLACKOP6':
                return {f'dir/take_{n}.sn.75.48000.all' for n in range(3)}
            return {'other.file.ln.10.24000.english'}
        with patch.object(inputs, 'named_names', side_effect=named):
            heads, tails = inputs.sound_lists('BLACKOP6')
            self.assertIn('other/file', heads)
            self.assertEqual(tails, ['.sn.75.48000.all'])
            with self.assertRaises(ValueError):
                inputs.sound_lists('MODWAR7')

    def test_general_generators_keep_legacy_and_configured_findings_seeds(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'fnv1a_xmodels.csv').write_text('')
            with patch.object(snapshot.settings, 'tables_csv', return_value=folder), patch.object(snapshot, 'table_names', return_value=['legacy_t9_model']) as reader, patch.object(snapshot, 'confirmed_names', return_value=['local_new_name']):
                self.assertEqual(inputs.all_known_names(), ['legacy_t9_model', 'local_new_name'])
                reader.assert_called_once_with('fnv1a_xmodels')


if __name__ == '__main__':
    unittest.main()
