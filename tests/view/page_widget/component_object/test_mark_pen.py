from unittest import TestCase

from src.common.font_style import StyleTuple, FontStyle
from src.controller.mark_pen import MarkPen, CharCell


class TestMarkPen(TestCase):
    def setUp(self) -> None:
        self.mark_pen = MarkPen()

    def test_update_style(self) -> None:
        rendered = self.mark_pen.render('abc')
        self.assertEqual(rendered, [
            CharCell(style=FontStyle.DEFAULT_STYLE_TUPLE, char='a'),
            CharCell(style=FontStyle.DEFAULT_STYLE_TUPLE, char='b'),
            CharCell(style=FontStyle.DEFAULT_STYLE_TUPLE, char='c')
        ])

        self.mark_pen.update_style('1;31')
        rendered = self.mark_pen.render('abc')
        self.assertEqual(len(rendered), 3)
        self.assertEqual(rendered[0].char, 'a')
        self.assertTrue(
            rendered[0].style.is_equal(
                StyleTuple(
                    bold=True, italic=False, opacity=1.0, visible=True, underline=False,
                    background_color='#FFFFFF', foreground_color='#800000'
                )
            )
        )
        self.assertEqual(rendered[1].char, 'b')
        self.assertTrue(
            rendered[1].style.is_equal(
                StyleTuple(
                    bold=True, italic=False, opacity=1.0, visible=True, underline=False,
                    background_color='#FFFFFF', foreground_color='#800000'
                )
            )
        )
        self.assertEqual(rendered[2].char, 'c')
        self.assertTrue(
            rendered[2].style.is_equal(
                StyleTuple(
                    bold=True, italic=False, opacity=1.0, visible=True, underline=False,
                    background_color='#FFFFFF', foreground_color='#800000'
                )
            )
        )
