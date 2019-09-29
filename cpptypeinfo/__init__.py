# flake8: noqa: F405
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
        + SingleReferenceType # resolve
            + Typedef
            + Pointer
                + Array
        + Function(extern "C", __declspec(dllexport)) # resolve
        + Struct(Class, Union, Template...) # resolve


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
from .basictype import *
from .typeparser import TypeParser
from .get_tu import *
from .cursor import parse_headers

VERSION = '0.2.0'
