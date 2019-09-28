'''
Type
    + PrimitiveType
        + Int8
        + Int16
        + Int32
        + Int64
        + UInt8
        + UInt16
        + UInt32
        + UInt64
        + Float
        + Double
        + Bool(Int8)
        + Void
        + VaList
    + UserType: 名前が付いてExport対象になり得る
        + Enum(Int32)
        + SingleReferenceType
            + Typedef
            + Pointer
                + Array
        + Function(extern "C", __declspec(dllexport))
        + Struct(Class, Union, Template...)

TypeRef
    + is_const
    + type: Type

Field: for Struct
    + ref: TypeRef
    + name

Param: for Function
    + ref: TypeRef
    + name
'''
from .typeparser import *
from .get_tu import get_tu, get_tu_from_source, tmp_from_source
from .cursor import parse_namespace

VERSION = '0.2.0'

__all__ = []
