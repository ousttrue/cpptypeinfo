import unittest
import cpptypeinfo


class NamespaceTests(unittest.TestCase):
    def test_namespace(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
namespace A
{
    namespace B
    {
        struct C
        {

        }
    }
}
''',
                                 debug=True)

        self.assertEqual(1, len(parser.root_namespace._children))
        a = parser.root_namespace._children[0]

        self.assertEqual('A', a.name)
        self.assertEqual(1, len(a._children))

        b = a._children[0]
        self.assertEqual(1, len(b._children))
        self.assertEqual('B', b.name)

        c = b._children[0]
        self.assertEqual(0, len(c._children))
        self.assertEqual('C', c.name)


if __name__ == '__main__':
    unittest.main()
