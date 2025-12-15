from unittest import TestCase

from src.common.font_style import FontStyle, StyleTuple


class TestFontStyle(TestCase):
    def setUp(self) -> None:
        self.reset_style()

    def reset_style(self) -> None:
        self.font_style = FontStyle()

    def test_font_style_init(self):
        self.assertEqual(self.font_style.style.bold, False)
        self.assertEqual(self.font_style.style.italic, False)
        self.assertEqual(self.font_style.style.opacity, 1.0)
        self.assertEqual(self.font_style.style.underline, False)
        self.assertEqual(self.font_style.style.background_color, '#FFFFFF')
        self.assertEqual(self.font_style.style.foreground_color, '#000000')

    def test_update_style(self):
        test_cases = [
            ('', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('0', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('1', False, StyleTuple(bold=True, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('01', False, StyleTuple(bold=True, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('2', False, StyleTuple(bold=False, italic=False, opacity=0.5, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('02', False, StyleTuple(bold=False, italic=False, opacity=0.5, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('3', False, StyleTuple(bold=False, italic=True, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('03', False, StyleTuple(bold=False, italic=True, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('4', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=True, background_color='#FFFFFF', foreground_color='#000000')),
            ('04', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=True, background_color='#FFFFFF', foreground_color='#000000')),
            ('7', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#000000', foreground_color='#FFFFFF')),
            ('07', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#000000', foreground_color='#FFFFFF')),
            ('8', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=False, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('08', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=False, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('22', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('24', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('27', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')), # Reset foreground and background
            ('28', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),

            ('30', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('31', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#800000')),
            ('32', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#008000')),
            ('33', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#808000')),
            ('34', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000080')),
            ('35', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#800080')),
            ('36', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#008080')),
            ('37', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#C0C0C0')),
            ('39', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),  # Reset foreground color
            ('90', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#808080')),
            ('91', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#FF0000')),
            ('92', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#00FF00')),
            ('93', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#FFFF00')),
            ('94', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#0000FF')),
            ('95', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#FF00FF')),
            ('96', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#00FFFF')),
            ('97', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#FFFFFF')),

            ('40', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#000000', foreground_color='#000000')),
            ('41', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#800000', foreground_color='#000000')),
            ('42', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#008000', foreground_color='#000000')),
            ('43', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#808000', foreground_color='#000000')),
            ('44', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#000080', foreground_color='#000000')),
            ('45', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#800080', foreground_color='#000000')),
            ('46', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#008080', foreground_color='#000000')),
            ('47', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#C0C0C0', foreground_color='#000000')),
            ('49', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
            ('100', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#808080', foreground_color='#000000')),
            ('101', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FF0000', foreground_color='#000000')),
            ('102', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#00FF00', foreground_color='#000000')),
            ('103', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFF00', foreground_color='#000000')),
            ('104', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#0000FF', foreground_color='#000000')),
            ('105', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FF00FF', foreground_color='#000000')),
            ('106', False, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#00FFFF', foreground_color='#000000')),
            ('107', True, StyleTuple(bold=False, italic=False, opacity=1.0, visible=True, underline=False, background_color='#FFFFFF', foreground_color='#000000')),
        ]

        for csi_params, expected_is_default, expected_style in test_cases:
            with self.subTest(csi_params=csi_params):
                self.reset_style()
                self.font_style.update(csi_params)
                self.assertTrue(self.font_style.style.is_equal(expected_style))
