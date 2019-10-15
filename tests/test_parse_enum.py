import unittest
import cpptypeinfo
SOURCE = '''
typedef enum {
    UNSPECIFIED_COMPARTMENT_ID = 0,
    DEFAULT_COMPARTMENT_ID
} COMPARTMENT_ID, *PCOMPARTMENT_ID

int i = 0;
int *x = &i;
int &w = i;
COMPARTMENT_ID y;
COMPARTMENT_ID *z;

void func(void*);
COMPARTMENT_ID func(COMPARTMENT_ID value);

struct A
{
    int value;
};
void funcA(A value);
'''


class EnumTests(unittest.TestCase):
    def test_enum(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 SOURCE,
                                 debug=True)


if __name__ == '__main__':
    unittest.main()
