import re
from typing import Optional, List, Union
from cpptypeinfo.basictype import (Type, TypeRef, primitive_type_map, Void)
from cpptypeinfo.usertype import (Typedef, Namespace, Pointer, Array, Field,
                                  Struct, Param, Function)

SPLIT_PATTERN = re.compile(r'[*&]')
# void (const Im3d::DrawList &)
NAMED_FUNC_PATTERN = re.compile(r'^(.*)\(.*\)\((.*)\)$')
FUNC_PATTERN = re.compile(r'^(.*)\((.*)\)$')


class TypeParser:
    """
    Namespaceのツリーを保持し、文字列をパースして適切なNamespaceに型登録する
    """
    def __init__(self) -> None:
        self.root_namespace = Namespace()
        self.stack: List[Namespace] = [self.root_namespace]

    def push_namespace(self, namespace: Union[str, Namespace]) -> None:
        if isinstance(namespace, str):
            namespace = Namespace(namespace)
        if not isinstance(namespace, Namespace):
            raise Exception(f'{namespace} is not namespace')
        if self.stack:
            self.stack[-1].add_child(namespace)
        self.stack.append(namespace)

    def pop_namespace(self) -> None:
        self.stack.pop()

    def get_current_namespace(self) -> Namespace:
        return self.stack[-1] if self.stack else self.root_namespace

    def resolve(self, target: Typedef, replace: Optional[Type]):
        if not replace:
            replace = target.typeref.ref
        for ns in self.root_namespace.traverse():
            for k, v in ns.user_type_map.items():
                v.replace(target, replace)
            for v in ns.functions:
                v.replace(target, replace)

        for ns in self.root_namespace.traverse():
            keys = []
            for k, v in ns.user_type_map.items():
                if v == target:
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

    def typedef(self, name: str, src: Union[str, TypeRef]) -> Typedef:
        '''
        現在のnamespaceに型をTypedefを登録する
        '''
        if isinstance(src, str):
            decl = self.parse(src)
        else:
            decl = src
        typedef = Typedef(decl)
        namespace = self.get_current_namespace()
        namespace.register_type(name, typedef)
        typedef.parent = namespace
        return typedef

    def struct(self, name: str, fields: List[Field]) -> Struct:
        decl = Struct(name, fields)
        namespace = self.get_current_namespace()
        namespace.register_type(name, decl)
        decl.parent = namespace
        return decl

    def parse(self,
              src: str,
              is_const=False,
              namespace: Optional[Namespace] = None) -> TypeRef:
        src = src.strip()

        if not namespace:
            namespace = self.get_current_namespace()
            if not isinstance(namespace, Namespace):
                raise Exception(f'{namespace} is not Namespace')

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

                    ns = self.get_from_ns(ns_list[0])
                    if ns and isinstance(ns, Struct):
                        decl = ns.namespace.get(ns_list[1])
                        if decl:
                            return TypeRef(decl, is_const)
                        else:
                            raise Exception()

                    for ns in namespace.ancestors():
                        for child in ns.traverse():
                            if child.name == ns_list[0]:
                                decl = child.get(ns_list[1])
                                if decl:
                                    return TypeRef(decl, is_const)
                                else:
                                    raise Exception(f'{src} not found')

                    raise Exception(f'{src} is not found')

                decl = self.get_from_ns(src)
                if decl:
                    return TypeRef(decl, is_const)

                raise Exception(f'not found: {src}')
