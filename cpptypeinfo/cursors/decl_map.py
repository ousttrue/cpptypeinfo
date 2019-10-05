from typing import Dict
from cpptypeinfo.usertype import UserType


class DeclMap:
    def __init__(self):
        self.decl_map: Dict[int, UserType] = {}

    def get(self, hash: int):
        return self.decl_map[hash]

    def add(self, hash: int, usertype: UserType) -> None:
        self.decl_map[hash] = usertype
