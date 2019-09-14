import unittest
import pathlib
from clang import cindex
import cpptypeinfo


class CIndexTest(unittest.TestCase):
    def test_cindex(self) -> None:
        tu = cpptypeinfo.get_tu_from_source('int x=123')
        c = tu.cursor
        children = [child for child in c.get_children()]
        self.assertEqual(1, len(children))

        c = children[0]
        self.assertEqual(c.kind, cindex.CursorKind.VAR_DECL)
        children = [child for child in c.get_children()]
        self.assertEqual(1, len(children))

        c = children[0]
        self.assertEqual(c.kind, cindex.CursorKind.INTEGER_LITERAL)
        tokens = [t.spelling for t in c.get_tokens()]
        self.assertEqual(1, len(tokens))
        self.assertEqual('123', tokens[0])
        children = [child for child in c.get_children()]
        self.assertEqual(0, len(children))


if __name__ == '__main__':
    unittest.main()
