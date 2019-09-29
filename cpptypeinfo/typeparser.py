import re
import pathlib
from typing import Optional
from cpptypeinfo.basictype import (Type, TypeRef, primitive_type_map)
from cpptypeinfo.usertype import (Typedef, Namespace, Pointer, Array, Field,
                                  Struct, Param, Function)


class TypeParser:
    """
    Namespaceのツリーを保持し、文字列をパースして適切なNamespaceに型登録する
    """
    def __init__(self) -> None:
        self.root_namespace = Namespace()

    def resolve(self, found: Typedef, replace: Optional[Type]):
        if not replace:
            replace = found.typeref.ref
        for ns in self.root_namespace.traverse():
            for k, v in ns.user_type_map.items():
                v.resolve(found, replace)
            for v in ns.functions:
                v.resolve(found, replace)

        for ns in self.root_namespace.traverse():
            keys = []
            for k, v in ns.user_type_map.items():
                if v == found:
                    keys.append(k)
            for k in keys:
                print(f'remove {k}')
                ns.user_type_map.pop(k)
                break

    def resolve_typedef_by_name(self, name: str, replace: Type = None):
        '''
        typedefを削除する。
        型を破壊的に変更する
        '''
        while True:
            found = None
            for ns in self.root_namespace.traverse():
                decl = ns.user_type_map.get(name)
                if decl:
                    if isinstance(decl, Typedef):
                        found = decl
                        break
            if found:
                # remove
                self.resolve(found, replace)
            else:
                break

    def resolve_typedef_void_p(self):
        while True:
            targets = []
            for ns in self.traverse():
                for k, v in ns.user_type_map.items():
                    if isinstance(v, Typedef):
                        if v.typeref.ref == Pointer(Void()):
                            targets.append(v)
            if not targets:
                return

            for target in targets:
                # remove
                self.resolve(target, target.typeref.ref)

    def resolve_typedef_struct_tag(self):
        '''
        remove
        typedef struct Some Some;
        '''
        targets = []
        for ns in self.traverse():
            for k, v in ns.user_type_map.items():
                if isinstance(v, Typedef):
                    if isinstance(v.typeref.ref, Struct):
                        if k == v.typeref.ref.type_name:
                            targets.append(v)

        for target in targets:
            # remove
            self.resolve(target, target.typeref.ref)

    def get_from_ns(self, src: str) -> Optional[Type]:
        primitive = primitive_type_map.get(src)
        if primitive:
            return primitive

        for namespace in self.root_namespace.traverse():
            decl = namespace.get(src)
            if decl:
                return decl

        return None

    def typedef(self, name: str, src: str) -> Typedef:
        decl = self.parse(src)
        typedef = Typedef(self.root_namespace, decl)
        self.root_namespace.user_type_map[name] = typedef
        return typedef

    def parse(self,
              src: str,
              is_const=False,
              namespace: Optional[Namespace] = None) -> TypeRef:
        src = src.strip()
        if not namespace:
            namespace = self.root_namespace

        m = NAMED_FUNC_PATTERN.match(src)
        if m:
            result = m.group(1)
            params = m.group(2).split(',') if m.group(2).strip() else []
            func = Function(self.parse(result),
                            [Param(typeref=self.parse(x)) for x in params])
            func.parent = namespace
            namespace.functions.append(func)
            return TypeRef(func)

        m = FUNC_PATTERN.match(src)
        if m:
            result = m.group(1)
            params = m.group(2).split(',') if m.group(2).strip() else []
            func = Function(self.parse(result),
                            [Param(typeref=self.parse(x)) for x in params])
            namespace.functions.append(func)
            return TypeRef(func)

        if src[-1] == '>':
            # template
            pos = src.rfind('<')
            if pos == -1:
                raise Exception('< not found')
            template_name = src[:pos].strip()
            template = self.parse(template_name, is_const).ref
            if not template:
                raise Exception(f'{template_name} not found')
            if isinstance(template, Struct):
                template_params = []
                for splitted in src[pos + 1:-1].strip().split(','):
                    try:
                        num = int(splitted)
                        template_params.append(num)
                    except Exception:
                        template_params.append(self.parse(splitted))
                decl = template.instantiate(template_params)
                return TypeRef(decl, is_const)
            else:
                raise Exception(f'{template_name} is not struct')

            # std::array<float, 16>
            raise Exception()

        if src[-1] == ']':
            # array
            pos = src.rfind('[')
            if pos == -1:
                raise Exception('"[" not found')
            length_str = src[pos + 1:-1].strip()
            length = None
            if length_str:
                length = int(length_str)
            return TypeRef(Array(self.parse(src[0:pos]), length), is_const)

        found = [x for x in SPLIT_PATTERN.finditer(src)]
        if found:
            # pointer or reference
            last = found[-1].start()
            head, tail = src[0:last].strip(), src[last + 1:].strip()
            return TypeRef(Pointer(self.parse(head)), tail == 'const')

        else:
            splitted = src.split()
            if splitted[0] == 'const':
                return self.parse(' '.join(splitted[1:]), True)
            elif splitted[-1] == 'const':
                return self.parse(' '.join(splitted[:-1]), True)
            elif splitted[0] == 'struct' or splitted[0] == 'union':
                if len(splitted) != 2:
                    raise Exception()

                decl = self.get_from_ns(splitted[1])
                if decl:
                    return TypeRef(decl, is_const)

                struct = Struct(splitted[1])
                struct.parent = namespace
                namespace.user_type_map[struct.type_name] = struct

                return TypeRef(struct, is_const)
            else:
                # get struct local type
                ns_list = src.split('::')
                if len(ns_list) > 1:
                    # if len(ns_list) != 2:
                    #     raise NotImplementedError()
                    ns_list = ns_list[-2:]
                    current = STACK[-1]
                    if isinstance(current, Struct):
                        if current.type_name == ns_list[0]:
                            return self.parse(ns_list[1], is_const)

                    ns = self.get_from_ns(ns_list[0])
                    if not ns:
                        raise Exception(f'not found {ns_list[0]}')

                    if isinstance(ns, Struct) or isinstance(ns, Namespace):
                        decl = ns.get(ns_list[1])
                        if decl:
                            return TypeRef(decl, is_const)

                        for ns in reversed(STACK):
                            for child in ns.children:
                                if child.name == ns_list[0]:
                                    decl = child.get(ns_list[1])
                                    if decl:
                                        return TypeRef(decl, is_const)
                                    else:
                                        raise Exception(f'{src} not found')

                        raise Exception(f'{src} is not found')
                    else:
                        raise Exception(f'{ns} is not Struct or Namespace')

                decl = self.get_from_ns(src)
                if decl:
                    return TypeRef(decl, is_const)

                raise Exception(f'not found: {src}')

    def parse_headers(self,
                      *paths: pathlib.Path,
                      cpp_flags=None,
                      before=None,
                      root_namespace: Optional[Namespace] = None):
        root_ns = push_namespace(root_namespace)
        if before:
            before(root_ns)
        if not cpp_flags:
            cpp_flags = []
        cpp_flags += [f'-I{x.parent}' for x in paths]
        with tmp_from_source(''.join([f'#include <{x.name}>\n'
                                      for x in paths])) as path:
            tu = get_tu(path, cpp_flags=cpp_flags)
            include_path_list = [x for x in paths]
            include_path_list.append(path)
            parse_namespace(tu.cursor, include_path_list)

        pop_namespace()
        return root_ns


SPLIT_PATTERN = re.compile(r'[*&]')
# void (const Im3d::DrawList &)
NAMED_FUNC_PATTERN = re.compile(r'^(.*)\(.*\)\((.*)\)$')
FUNC_PATTERN = re.compile(r'^(.*)\((.*)\)$')
