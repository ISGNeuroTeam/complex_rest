from django.test import TestCase
from core.settings.ini_config import merge_ini_config_with_defaults


class TestMergeIniConfig(TestCase):
    def test_empty_section(self):
        settings = {}
        default_settings = {
            'section1': {
                'subsection': 'test'
            }
        }

        result_conf = merge_ini_config_with_defaults(settings, default_settings)
        self.assertDictEqual(
            result_conf,
            {
                'section1': {
                    'subsection': 'test'
                }
            }
        )

    def test_partialy_empty_section(self):
        settings = {
            'section1': {
                'subsection1': 'override',
            },
        }
        default_settings = {
            'section1': {
                'subsection1': 'test',
                'subsection2': 'test2'
            }
        }

        result_conf = merge_ini_config_with_defaults(settings, default_settings)
        self.assertDictEqual(
            result_conf,
            {
                'section1': {
                    'subsection1': 'override',
                    'subsection2': 'test2'
                }
            }
        )

    def test_empty_default_section(self):
        settings = {
            'section1': {
                'subsection1': 'test',
                'subsection2': 'test2'
            }
        }
        default_settings = {
        }
        result_conf = merge_ini_config_with_defaults(settings, default_settings)
        self.assertDictEqual(
            result_conf,
            {
                'section1': {
                    'subsection1': 'test',
                    'subsection2': 'test2'
                }
            }
        )

    def test_partialy_empty_default_section(self):
        settings = {
            'section1': {
                'subsection1': 'test',
                'subsection2': 'test2'
            }
        }
        default_settings = {
            'section1': {
                'subsection1': 'not_override',
            },
        }

        result_conf = merge_ini_config_with_defaults(settings, default_settings)

        self.assertDictEqual(
            result_conf,
            {
                'section1': {
                    'subsection1': 'test',
                    'subsection2': 'test2'
                }
            }
        )
