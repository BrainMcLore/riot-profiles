import ast
from pathlib import Path
import re
import string
import tempfile
import unittest

from app import core, i18n


class LocalizationTests(unittest.TestCase):
    def test_all_four_catalogs_have_matching_placeholders(self):
        self.assertEqual(set(i18n.LANGUAGES), {'ru', 'en', 'uk', 'pt-PT'})
        self.assertEqual(len(i18n.ROWS), len(i18n.CATALOGS['ru']))
        formatter = string.Formatter()
        for row in i18n.ROWS:
            self.assertEqual(len(row), 4)
            fields = [{name for _, name, _, _ in formatter.parse(text) if name} for text in row]
            self.assertTrue(all(value == fields[0] for value in fields), row[0])
            self.assertTrue(all(text.strip() for text in row))

    def test_english_and_portuguese_do_not_leak_cyrillic(self):
        for language in ('en', 'pt-PT'):
            for translated in i18n.CATALOGS[language].values():
                self.assertIsNone(re.search('[А-Яа-яІіЇїЄє]', translated), translated)

    def test_profile_name_is_preserved_in_translated_status(self):
        name = 'My profile — Україна {special}'
        template = 'Открыт профиль «{name}». Для переключения выбери другой слева и нажми «Запустить».'
        for language in i18n.LANGUAGES:
            self.assertIn(name, i18n.Translator(language)(template, name=name))

    def test_language_is_saved_separately_from_profiles(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = core.Paths(Path(temporary))
            profile = core.Profiles(paths).create('Unchanged')
            before = paths.index.read_bytes()
            i18n.save_preferences(paths, 'pt-PT', False)
            settings = i18n.preferences(paths)
            self.assertEqual(settings['language'], 'pt-PT')
            self.assertFalse(settings['show_language_picker'])
            self.assertEqual(paths.index.read_bytes(), before)
            self.assertEqual(core.Profiles(paths).get(profile['id']), profile)

    def test_corrupt_settings_and_unsupported_language(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = core.Paths(Path(temporary))
            paths.data.mkdir()
            (paths.data / 'settings.json').write_text('not json')
            self.assertEqual(i18n.preferences(paths), {})
            self.assertEqual(i18n.Translator('bad').language, 'en')
            with self.assertRaises(ValueError):
                i18n.save_preferences(paths, '../../bad')

    def test_progress_and_dynamic_errors_are_localized(self):
        pt = i18n.Translator('pt-PT')
        self.assertEqual(pt.message('Распаковка: emulator'), 'A extrair: emulator')
        self.assertEqual(pt.message('emulator: 5 / 10 МБ'), 'emulator: 5 / 10 MB')
        self.assertEqual(pt.message('Google не предлагает нужный стабильный пакет: emulator'),
                         'A Google não disponibiliza o pacote estável necessário: emulator')

    def test_all_backend_russian_messages_have_translations(self):
        root = Path(__file__).resolve().parent.parent
        for module in ('core', 'install', 'windows'):
            tree = ast.parse((root / 'app' / (module + '.py')).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.search('[А-Яа-я]', node.value):
                    self.assertTrue(node.value in i18n.CATALOGS['en'] or node.value.strip() in i18n.CATALOGS['en'], (module, node.value))
