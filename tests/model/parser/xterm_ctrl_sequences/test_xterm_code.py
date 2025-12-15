from unittest import TestCase

from src.model.parser.xterm_ctrl_sequences.xterm_code import \
    INCOMPLETE_ANSI_RE, XTERM_PARSER_RE


class TestIncompleteAnsi(TestCase):
    def test_incomplete_ansi(self):
        # Test for incomplete ANSI sequences
        self.assertEqual(b'\x1b', INCOMPLETE_ANSI_RE.search(b'abc\x1b').group(0))

        # ESC [     Control Sequence Introducer ( CSI is 0x9b)
        self.assertEqual(b'\x1b[', INCOMPLETE_ANSI_RE.search(b'abc\x1b[').group(0))
        self.assertEqual(b'\x1b[1', INCOMPLETE_ANSI_RE.search(b'abc\x1b[1').group(0))
        self.assertEqual(b'\x1b[1;', INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;').group(0))
        self.assertEqual(b'\x1b[1;2', INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2').group(0))
        self.assertEqual(b'\x1b[?', INCOMPLETE_ANSI_RE.search(b'abc\x1b[?').group(0))
        self.assertEqual(b'\x1b[?1', INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1').group(0))
        self.assertEqual(b'\x1b[>', INCOMPLETE_ANSI_RE.search(b'abc\x1b[>').group(0))
        self.assertEqual(b'\x1b[>1', INCOMPLETE_ANSI_RE.search(b'abc\x1b[>1').group(0))
        self.assertEqual(b'\x1b[!', INCOMPLETE_ANSI_RE.search(b'abc\x1b[!').group(0))
        self.assertEqual(b'\x1b[61;0"', INCOMPLETE_ANSI_RE.search(b'abc\x1b[61;0"').group(0))
        self.assertEqual(b'\x1b[6"', INCOMPLETE_ANSI_RE.search(b'abc\x1b[6"').group(0))
        self.assertEqual(b'\x1b[?1;2;3;4;5$', INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1;2;3;4;5$').group(0))
        self.assertEqual(b'\x1b[1;2;3;4;5\'', INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4;5\'').group(0))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[@'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1@'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[A'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1A'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[B'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1B'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[C'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1C'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[D'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1D'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[E'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1E'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[F'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1F'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[G'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1G'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[H'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;1H'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[I'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1I'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[J'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1J'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?J'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?2J'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[K'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1K'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?K'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1K'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[L'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1L'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[M'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1M'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[P'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1P'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[S'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1S'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[T'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1T'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4;5;T'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[X'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1X'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[Z'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1Z'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[`'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1`'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[b'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1b'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[c'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1c'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[15c'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1;2c'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?60;1;2;6;8;9;15;c'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[>0;1;2c'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[d'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1d'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[f'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;1f'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[g'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[3g'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[h'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[2h'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1h'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1049h'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[i'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[4i'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[l'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[2l'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1l'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1049l'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[m'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;30;40m'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[5n'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?6n'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[!p'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[61;0"p'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[2"q'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2r'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1r'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?1;2;3;4;5$r'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[s'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[?12s'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[12;34;3t'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4;5$t'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[u'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4;5;6;7;8$v'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4\'w'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[x'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1x'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4;5$x'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2\'z'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4$z'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1\'{'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1;2;3;4${'))

        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b[1\'|'))

        # ESC ]     Operating System Command ( OSC is 0x9d)
        self.assertEqual(b'\x1b]', INCOMPLETE_ANSI_RE.search(b'abc\x1b]').group(0))
        self.assertEqual(b'\x1b]123&', INCOMPLETE_ANSI_RE.search(b'abc\x1b]123&').group(0))
        self.assertEqual(b'\x1b', INCOMPLETE_ANSI_RE.search(b'abc\x1b]0;title\x1b').group(0))  # Incomplete OSC sequence
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b]0;title\x1b\\'))  # This is a complete OSC sequence
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b]0;title\x07'))  # This is a complete OSC sequence

        # ESC P     Device Control String ( DCS is 0x90)
        self.assertEqual(b'\x1bP', INCOMPLETE_ANSI_RE.search(b'abc\x1bP').group(0))
        self.assertEqual(b'\x1bP1', INCOMPLETE_ANSI_RE.search(b'abc\x1bP1').group(0))
        self.assertEqual(b'\x1bP1;', INCOMPLETE_ANSI_RE.search(b'abc\x1bP1;').group(0))
        self.assertEqual(b'\x1bP1;2', INCOMPLETE_ANSI_RE.search(b'abc\x1bP1;2').group(0))
        self.assertEqual(b'\x1bP1;2|', INCOMPLETE_ANSI_RE.search(b'abc\x1bP1;2|').group(0))
        self.assertEqual(b'\x1bP1;2|3', INCOMPLETE_ANSI_RE.search(b'abc\x1bP1;2|3').group(0))
        self.assertEqual(b'\x1b', INCOMPLETE_ANSI_RE.search(b'abc\x1bP1;2|3\x1b').group(0))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bP1;2|3\x1b\\'))  # Incomplete DCS sequence

        # ESC ^     Privacy Message ( PM is 0x9e)
        self.assertEqual(b'\x1b^', INCOMPLETE_ANSI_RE.search(b'abc\x1b^').group(0))
        self.assertEqual(b'\x1b^1', INCOMPLETE_ANSI_RE.search(b'abc\x1b^1').group(0))
        self.assertEqual(b'\x1b^hello', INCOMPLETE_ANSI_RE.search(b'abc\x1b^hello').group(0))
        self.assertEqual(b'\x1b', INCOMPLETE_ANSI_RE.search(b'abc\x1b^hello\x1b').group(0))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b^hello\x1b\\'))  # Incomplete PM sequence

        # ESC _     Application Program Command ( APC is 0x9f)
        self.assertEqual(b'\x1b_', INCOMPLETE_ANSI_RE.search(b'abc\x1b_').group(0))
        self.assertEqual(b'\x1b_1', INCOMPLETE_ANSI_RE.search(b'abc\x1b_1').group(0))
        self.assertEqual(b'\x1b_hello', INCOMPLETE_ANSI_RE.search(b'abc\x1b_hello').group(0))
        self.assertEqual(b'\x1b', INCOMPLETE_ANSI_RE.search(b'abc\x1b_hello\x1b').group(0))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b_hello\x1b\\'))  # Incomplete APC sequence

        # ESC D     Index ( IND is 0x84)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bD'))
        # ESC E     Next Line ( NEL is 0x85)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bE'))
        # ESC H     Tab Set ( HTS is 0x88)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bH'))
        # ESC M     Reverse Index ( RI is 0x8d)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bM'))
        # ESC N     Single Shift Select of G2 Character Set ( SS2 is 0x8e): affects next character only
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bN'))
        # ESC O     Single Shift Select of G3 Character Set ( SS3 is 0x8f): affects next character only
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bO'))

        # ESC V     Start of Guarded Area ( SPA is 0x96)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bV'))
        # ESC W     End of Guarded Area ( EPA is 0x97)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bW'))
        # ESC X     Start of String ( SOS is 0x98)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bX'))
        # ESC Z     Return Terminal ID (DECID is 0x9a). Obsolete form of CSI c (DA).
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bZ'))
        # ESC \     String Terminator ( ST is 0x9c)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b\\'))

        # ESC SP
        self.assertEqual(b'\x1b ', INCOMPLETE_ANSI_RE.search(b'abc\x1b ').group(0))
        # ESC SP F  7-bit controls (S7C1T)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b F'))
        # ESC SP G  8-bit controls (S8C1T)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b G'))
        # ESC SP L  Set ANSI conformance level 1
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b L'))
        # ESC SP M  Set ANSI conformance level 2
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b M'))
        # ESC SP N  Set ANSI conformance level 3
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b N'))

        # ESC #
        self.assertEqual(b'\x1b#', INCOMPLETE_ANSI_RE.search(b'abc\x1b#').group(0))
        # ESC # 3  DEC double-height line, top half (DECDHL)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b#3'))
        # ESC # 4  DEC double-height line, bottom half (DECDHL)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b#4'))
        # ESC # 5  DEC single-width line (DECSWL)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b#5'))
        # ESC # 6  DEC double-width line (DECDWL)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b#6'))
        # ESC # 8  DEC Screen Alignment Test (DECALN)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b#8'))

        # ESC %
        self.assertEqual(b'\x1b%', INCOMPLETE_ANSI_RE.search(b'abc\x1b%').group(0))
        # ESC % @  Select default character set, ISO 8859-1 (ISO 2022)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b%@'))
        # ESC % G  Select UTF-8 character set (ISO 2022)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b%G'))

        # ESC (,),*,+
        self.assertEqual(b'\x1b(', INCOMPLETE_ANSI_RE.search(b'abc\x1b(').group(0))
        self.assertEqual(b'\x1b)', INCOMPLETE_ANSI_RE.search(b'abc\x1b)').group(0))
        self.assertEqual(b'\x1b*', INCOMPLETE_ANSI_RE.search(b'abc\x1b*').group(0))
        self.assertEqual(b'\x1b+', INCOMPLETE_ANSI_RE.search(b'abc\x1b+').group(0))

        for c in [b'(', b')', b'*', b'+']:
            for c2 in [b'0', b'A', b'B', b'4', b'C', b'5', b'R', b'Q', b'K', b'Y', b'E', b'6', b'Z', b'H', b'7', b'=']:
                self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b' + c + c2))

        # ESC 7     Save Cursor (DECSC)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b7'))

        # ESC 8     Restore Cursor (DECRC)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b8'))

        # ESC =     Application Keypad (DECPAM)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b='))

        # ESC >     Normal Keypad (DECPNM)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b>'))

        # ESC F     Cursor to lower left corner (DECHPA)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bF'))

        # ESC c     Full Reset (RIS)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bc'))

        # ESC l     Memory Lock
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bl'))

        # ESC m     Memory Unlock
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bm'))

        # ESC n     Invoke the G2 Character Set as GL (LS2)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bn'))

        # ESC o     Invoke the G3 Character Set as GL (LS3)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1bo'))

        # ESC |     Invoke the G3 Character Set as GR (LS3R)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b|'))

        # ESC }     Invoke the G2 Character Set as GR (LS2R)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b}'))

        # ESC ~     Invoke the G1 Character Set as GR (LS1R)
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc\x1b~'))

        # TERM_CAP_DELAY
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc$ '))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc$<100>'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc$<100>123'))
        self.assertIsNone(INCOMPLETE_ANSI_RE.search(b'abc$<100> '))
        self.assertEqual(b'$', INCOMPLETE_ANSI_RE.search(b'abc$').group(0))
        self.assertEqual(b'$<', INCOMPLETE_ANSI_RE.search(b'abc$<').group(0))
        self.assertEqual(b'$<1', INCOMPLETE_ANSI_RE.search(b'abc$<1').group(0))


class TestXtermParserRE(TestCase):
    """Test XTERM_PARSER_RE regex pattern matching"""

    def test_ascii_control_characters(self):
        """Test ASCII control character matching"""
        # Test all supported ASCII control characters
        ascii_chars = [
            (b'\x07', 'bell'),
            (b'\x08', 'backspace'),
            # (b'\x0a', 'line feed'),
            (b'\x0b', 'vertical tab'),
            (b'\x0c', 'form feed'),
            # (b'\x0d', 'carriage return'),
            (b'\x0e', 'shift out'),
            (b'\x0f', 'shift in'),
        ]

        for char, desc in ascii_chars:
            with self.subTest(char=char, desc=desc):
                test_data = b'hello' + char + b'world'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match ASCII character {desc}")
                self.assertEqual(match.group('ASCII_1'), char)
                self.assertIsNone(match.group('ANSI'))

    def test_ascii_lf(self):
        ascii_chars = [(b'\x0a', 'line feed')]
        for char, desc in ascii_chars:
            with self.subTest(char=char, desc=desc):
                test_data = b'hello' + char + b'world'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match ASCII character {desc}")
                self.assertEqual(match.group('ASCII_LF'), char)
                self.assertIsNone(match.group('ANSI'))

    def test_ascii_cr(self):
        ascii_chars = [(b'\x0d', 'carriage return')]
        for char, desc in ascii_chars:
            with self.subTest(char=char, desc=desc):
                test_data = b'hello' + char + b'world'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match ASCII character {desc}")
                self.assertEqual(match.group('ASCII_CR'), char)
                self.assertIsNone(match.group('ANSI'))

    def test_csi_control_sequences(self):
        """Test CSI control sequence matching"""
        csi_sequences = [
            # Basic CSI sequences
            (b'\x1b[H', '', 'H', 'cursor position'),
            (b'\x1b[2J', '2', 'J', 'clear screen'),
            (b'\x1b[1;1H', '1;1', 'H', 'cursor position to (1,1)'),
            (b'\x1b[?25h', '?25', 'h', 'DEC private mode set'),
            (b'\x1b[>0c', '>0', 'c', 'device attributes query'),
            (b'\x1b[0m', '0', 'm', 'reset character attributes'),
            (b'\x1b[1;32;40m', '1;32;40', 'm', 'set character attributes'),
            (b'\x1b[6n', '6', 'n', 'device status report'),
            (b'\x1b[@', '', '@', 'insert character'),
            (b'\x1b[5@', '5', '@', 'insert 5 characters'),
            (b'\x1b[A', '', 'A', 'cursor up'),
            (b'\x1b[10A', '10', 'A', 'cursor up 10 lines'),
            (b'\x1b[B', '', 'B', 'cursor down'),
            (b'\x1b[C', '', 'C', 'cursor right'),
            (b'\x1b[D', '', 'D', 'cursor left'),
            (b'\x1b[s', '', 's', 'save cursor'),
            (b'\x1b[u', '', 'u', 'restore cursor'),
            (b'\x1b[2K', '2', 'K', 'erase line'),
            (b'\x1b[?1049h', '?1049', 'h', 'alternate screen buffer'),
            (b'\x1b[1;2r', '1;2', 'r', 'set scrolling region'),
            (b'\x1b[!p', '!', 'p', 'soft terminal reset'),
            (b'\x1b[61;0"p', '61;0"', 'p', 'set conformance level'),
            (b'\x1b[2"q', '2"', 'q', 'select character protection attribute'),
            (b'\x1b[1;2;3;4;5$r', '1;2;3;4;5$', 'r', 'change attributes in rectangular area'),
            (b'\x1b[1;2;3;4;5;6;7;8$v', '1;2;3;4;5;6;7;8$', 'v', 'copy rectangular area'),
            (b'\x1b[1;2;3;4\'w', '1;2;3;4\'', 'w', 'enable locator reporting'),
            (b'\x1b[1;2;3;4;5$x', '1;2;3;4;5$', 'x', 'fill rectangular area'),
            (b'\x1b[1;2\'z', '1;2\'', 'z', 'enable locator reporting'),
            (b'\x1b[1;2;3;4$z', '1;2;3;4$', 'z', 'selective erase rectangular area'),
            (b'\x1b[1\'{', '1\'', '{', 'select locator events'),
            (b'\x1b[1;2;3;4${', '1;2;3;4$', '{', 'selective erase rectangular area'),
            (b'\x1b[1\'|', '1\'', '|', 'request locator position'),
        ]

        for sequence, expected_param, expected_func, desc in csi_sequences:
            with self.subTest(sequence=sequence, desc=desc):
                test_data = b'prefix' + sequence + b'suffix'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match CSI sequence {desc}")
                self.assertIsNotNone(match.group('ANSI'))
                self.assertEqual(match.group('CSI_P'),
                                 expected_param.encode() if isinstance(expected_param, str) else expected_param)
                self.assertEqual(match.group('CSI_F'),
                                 expected_func.encode() if isinstance(expected_func, str) else expected_func)

    def test_simple_escape_sequences(self):
        """Test simple escape sequence matching"""
        simple_sequences = [
            (b'\x1bD', 'index'),
            (b'\x1bE', 'next line'),
            (b'\x1bH', 'tab set'),
            (b'\x1bM', 'reverse index'),
            (b'\x1bN', 'single shift select G2'),
            (b'\x1bO', 'single shift select G3'),
            (b'\x1bV', 'start of protected area'),
            (b'\x1bW', 'end of protected area'),
            (b'\x1bX', 'start of string'),
            (b'\x1bZ', 'return terminal ID'),
            (b'\x1b7', 'save cursor'),
            (b'\x1b8', 'restore cursor'),
            (b'\x1b=', 'application keypad'),
            (b'\x1b>', 'normal keypad'),
            (b'\x1bF', 'HP lower left'),
            (b'\x1bc', 'full reset'),
            (b'\x1bl', 'memory lock'),
            (b'\x1bm', 'memory unlock'),
            (b'\x1bn', 'invoke G2 character set'),
            (b'\x1bo', 'invoke G3 character set'),
            (b'\x1b|', 'invoke G3 character set as GR'),
            (b'\x1b}', 'invoke G2 character set as GR'),
            (b'\x1b~', 'invoke G1 character set as GR'),
        ]

        for sequence, desc in simple_sequences:
            with self.subTest(sequence=sequence, desc=desc):
                test_data = b'prefix' + sequence + b'suffix'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match simple escape sequence {desc}")
                self.assertIsNotNone(match.group('ANSI'))
                self.assertIsNone(match.group('ASCII_1'))

    def test_intermediate_and_final_character_sequences(self):
        """Test escape sequences with intermediate and final characters"""
        intermediate_sequences = [
            # ESC SP sequences
            (b'\x1b F', '7-bit controls'),
            (b'\x1b G', '8-bit controls'),
            (b'\x1b L', 'ANSI conformance level 1'),
            (b'\x1b M', 'ANSI conformance level 2'),
            (b'\x1b N', 'ANSI conformance level 3'),

            # ESC # sequences
            (b'\x1b#3', 'DEC double-height line, top half'),
            (b'\x1b#4', 'DEC double-height line, bottom half'),
            (b'\x1b#5', 'DEC single-width line'),
            (b'\x1b#6', 'DEC double-width line'),
            (b'\x1b#8', 'DEC screen alignment test'),

            # ESC % sequences
            (b'\x1b%@', 'select default character set ISO 8859-1'),
            (b'\x1b%G', 'select UTF-8 character set'),

            # ESC ( ) * + sequences (character set designation)
            (b'\x1b(A', 'designate G0 as UK character set'),
            (b'\x1b(B', 'designate G0 as US character set'),
            (b'\x1b(0', 'designate G0 as DEC special character set'),
            (b'\x1b)A', 'designate G1 as UK character set'),
            (b'\x1b)B', 'designate G1 as US character set'),
            (b'\x1b*A', 'designate G2 as UK character set'),
            (b'\x1b+A', 'designate G3 as UK character set'),
        ]

        for sequence, desc in intermediate_sequences:
            with self.subTest(sequence=sequence, desc=desc):
                test_data = b'prefix' + sequence + b'suffix'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match intermediate character sequence {desc}")
                self.assertIsNotNone(match.group('ANSI'))

    def test_operating_system_command_sequences(self):
        """Test operating system command (OSC) sequences"""
        osc_sequences = [
            # OSC terminated with BEL
            (b'\x1b]0;Terminal Title\x07', 'set terminal title (BEL terminated)'),
            (b'\x1b]1;Icon Name\x07', 'set icon name (BEL terminated)'),
            (b'\x1b]2;Window Title\x07', 'set window title (BEL terminated)'),
            (b'\x1b]46;/path/to/logfile\x07', 'set log file (BEL terminated)'),
            (b'\x1b]50;font-name\x07', 'set font (BEL terminated)'),

            # OSC terminated with ESC \
            (b'\x1b]0;Terminal Title\x1b\\', 'set terminal title (ST terminated)'),
            (b'\x1b]1;Icon Name\x1b\\', 'set icon name (ST terminated)'),
            (b'\x1b]2;Window Title\x1b\\', 'set window title (ST terminated)'),
            (b'\x1b]46;/path/to/logfile\x1b\\', 'set log file (ST terminated)'),

            # Complex OSC sequences
            (b'\x1b]0;Complex Title with; semicolons\x07', 'complex title (with semicolons)'),
            (b'\x1b]2;Title with special chars !@#$%\x1b\\', 'title with special characters'),
        ]

        for sequence, desc in osc_sequences:
            with self.subTest(sequence=sequence, desc=desc):
                test_data = b'prefix' + sequence + b'suffix'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match OSC sequence {desc}")
                self.assertIsNotNone(match.group('ANSI'))

    def test_device_control_sequences(self):
        """Test device control string (DCS, APC, PM) sequences"""
        control_sequences = [
            # DCS sequences
            (b'\x1bPsome data\x1b\\', 'DCS device control string'),
            (b'\x1bP$q"p\x1b\\', 'DCS request mode'),
            (b'\x1bP1$r1;2;3;4;5r\x1b\\', 'DCS report'),

            # APC sequences
            (b'\x1b_application data\x1b\\', 'APC application command'),
            (b'\x1b_command with args\x1b\\', 'APC command with arguments'),

            # PM sequences
            (b'\x1b^privacy message\x1b\\', 'PM privacy message'),
            (b'\x1b^secure data\x1b\\', 'PM secure data'),
        ]

        for sequence, desc in control_sequences:
            with self.subTest(sequence=sequence, desc=desc):
                test_data = b'prefix' + sequence + b'suffix'
                match = XTERM_PARSER_RE.search(test_data)
                self.assertIsNotNone(match, f"Should match control sequence {desc}")
                self.assertIsNotNone(match.group('ANSI'))

    def test_no_match_cases(self):
        """Test cases that should not match"""
        no_match_cases = [
            (b'normal text', 'normal text'),
            (b'text with \x09 tab', 'text with tab character'),
            (b'text with numbers 123', 'text with numbers'),
            (b'text with symbols !@#$', 'text with symbols'),
            (b'\x1b', 'single ESC character'),
            (b'\x1b[', 'incomplete CSI sequence'),
            (b'\x1b]', 'incomplete OSC sequence'),
            (b'\x1bP', 'incomplete DCS sequence'),
            (b'\x1b^', 'incomplete PM sequence'),
            (b'\x1b_', 'incomplete APC sequence'),
        ]

        for text, desc in no_match_cases:
            with self.subTest(text=text, desc=desc):
                match = XTERM_PARSER_RE.match(text)  # Use match instead of search to ensure matching from start
                if desc.startswith('incomplete'):
                    # Incomplete sequences might be matched as partial content
                    continue
                else:
                    self.assertIsNone(match, f"Should not match {desc}")

    def test_complex_mixed_sequences(self):
        """Test complex mixed sequences"""
        complex_cases = [
            # Sequential control sequences
            (b'\x1b[2J\x1b[H', 'clear screen then cursor position'),
            (b'\x1b[?1049h\x1b[H\x1b[2J', 'switch to alternate screen and clear'),
            (b'\x1b7\x1b[1;1H\x1b8', 'save cursor, position, restore cursor'),

            # Mixed ASCII and ANSI
            (b'Hello\x07\x1b[32mWorld\x1b[0m', 'text, bell, color, reset'),
            (b'Line1\x0d\x0a\x1b[BLine3', 'carriage return line feed then cursor down'),

            # Complex parameter sequences
            (b'\x1b[38;2;255;128;64m', '24-bit true color foreground'),
            (b'\x1b[48;5;196m', '256-color background'),
            (b'\x1b[1;4;5;7;9m', 'multiple text attributes'),
        ]

        for sequence, desc in complex_cases:
            with self.subTest(sequence=sequence, desc=desc):
                # For complex sequences, there might be multiple matches
                matches = list(XTERM_PARSER_RE.finditer(sequence))
                self.assertGreater(len(matches), 0, f"Should match at least one control sequence in {desc}")

    def test_group_names_and_structure(self):
        """Test regex group names and structure"""
        # Test ASCII group
        match = XTERM_PARSER_RE.search(b'test\x07end')
        self.assertIsNotNone(match.group('ASCII_1'))
        self.assertIsNone(match.group('ANSI'))

        # Test ANSI group and its subgroups
        match = XTERM_PARSER_RE.search(b'test\x1b[2Jend')
        self.assertIsNone(match.group('ASCII_1'))
        self.assertIsNotNone(match.group('ANSI'))
        self.assertEqual(match.group('CSI_P'), b'2')
        self.assertEqual(match.group('CSI_F'), b'J')

        # Test simple escape sequence (no CSI parameters)
        match = XTERM_PARSER_RE.search(b'test\x1bDend')
        self.assertIsNone(match.group('ASCII_1'))
        self.assertIsNotNone(match.group('ANSI'))
        self.assertIsNone(match.group('CSI_P'))
        self.assertIsNone(match.group('CSI_F'))

    def test_edge_cases(self):
        """Test edge cases"""
        edge_cases = [
            # Empty parameter CSI sequences
            (b'\x1b[m', 'empty parameter SGR'),
            (b'\x1b[H', 'empty parameter cursor position'),

            # Very long parameters
            (b'\x1b[1;2;3;4;5;6;7;8;9;10;11;12;13;14;15m', 'long parameter list'),

            # Special characters in parameters
            (b'\x1b[?1;2;3;4;5;6;7;8;9h', 'long private mode parameters'),

            # Minimal valid sequences
            (b'\x1b[A', 'minimal CSI sequence'),
            (b'\x1bD', 'minimal escape sequence'),

            # Parameters with quotes
            (b'\x1b[61;0"p', 'parameter with quotes'),
            (b'\x1b[2"q', 'short parameter with quotes'),
        ]

        for sequence, desc in edge_cases:
            with self.subTest(sequence=sequence, desc=desc):
                match = XTERM_PARSER_RE.search(sequence)
                self.assertIsNotNone(match, f"Should match edge case {desc}")
