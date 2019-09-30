import unittest
import cpptypeinfo
SOURCE = '''
typedef enum {
    UNSPECIFIED_COMPARTMENT_ID = 0,
    DEFAULT_COMPARTMENT_ID
} COMPARTMENT_ID, *PCOMPARTMENT_ID
'''


class EnumTests(unittest.TestCase):
    def test_enum(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 SOURCE,
                                 debug=True)


if __name__ == '__main__':
    unittest.main()
