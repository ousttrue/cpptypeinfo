import unittest
import cpptypeinfo
SOURCE = '''
struct B;
struct B;
struct B
{
    int value;
};

struct {
    int a;
};
struct {
    int a;
} end;
typedef struct tag {
    int a;
} A;

void func ();
void func ()
{

}
'''


class StructTests(unittest.TestCase):
    def test_struct(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 SOURCE,
                                 debug=True)


if __name__ == '__main__':
    unittest.main()
