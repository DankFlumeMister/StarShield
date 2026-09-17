#!/usr/bin/env python3
"""matrix_schema.py — docs/_generated/matrix.json 的字段白名单校验（Python 侧）

为什么需要它：
上一次事故的根因是「上游生成器静默丢弃了 KLE 的第二轮廓 x2/y2/w2/h2」，
主键区 Enter 的异形轮廓因此丢失，被下游当成完整矩形。上游已经改成遇到未识别属性
直接抛错；这里是第二跳 —— 下游脚本（gen_matrix_sch / gen_matrix_doc）读的是
matrix.json，同样不能对字段视而不见。

白名单本身不写死在本文件，而是读 docs/_tools/field_schema.json，
与 JS 侧（kle_schema.mjs / matrix_schema.mjs）共用一份清单，避免两侧漂移。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "field_schema.json")

with open(SCHEMA_PATH, encoding="utf-8") as _f:
    _SCHEMA = json.load(_f)

TOP_FIELDS = set(_SCHEMA["matrix"]["top"])
KEY_REQUIRED = set(_SCHEMA["matrix"]["keyRequired"])
KEY_OPTIONAL = set(_SCHEMA["matrix"]["keyOptional"])
KEY_ALLOWED = KEY_REQUIRED | KEY_OPTIONAL


def validate(data):
    """校验 matrix.json 的字段集合。不合规时抛 ValueError。"""
    if not isinstance(data, dict):
        raise ValueError("顶层不是 JSON 对象")

    unknown_top = sorted(set(data) - TOP_FIELDS)
    if unknown_top:
        raise ValueError(
            "顶层出现未识别字段：%s\n"
            "已知字段：%s\n"
            "新增字段请先在 docs/_tools/field_schema.json 登记。"
            % (", ".join(unknown_top), ", ".join(sorted(TOP_FIELDS)))
        )

    missing_top = sorted(TOP_FIELDS - set(data))
    if missing_top:
        raise ValueError("顶层缺少字段：%s" % ", ".join(missing_top))

    matrix = data.get("matrix")
    if not isinstance(matrix, list):
        raise ValueError("matrix 字段不是数组")

    for i, k in enumerate(matrix, 1):
        if not isinstance(k, dict):
            raise ValueError("matrix[%d] 不是对象" % i)
        unknown = sorted(set(k) - KEY_ALLOWED)
        if unknown:
            raise ValueError(
                "键位 %s（matrix[%d]）出现未识别字段：%s\n"
                "必需字段：%s\n"
                "可选字段（异形键）：%s\n"
                "新增字段请先在 docs/_tools/field_schema.json 登记。"
                % (repr(k.get("label")), i, ", ".join(unknown),
                   ", ".join(sorted(KEY_REQUIRED)), ", ".join(sorted(KEY_OPTIONAL)))
            )
        missing = sorted(KEY_REQUIRED - set(k))
        if missing:
            raise ValueError(
                "键位 %s（matrix[%d]）缺少必需字段：%s"
                % (repr(k.get("label")), i, ", ".join(missing))
            )
    return True


if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else "docs/_generated/matrix.json",
              encoding="utf-8") as f:
        validate(json.load(f))
    print("✅ matrix.json 字段校验通过（白名单来自 field_schema.json）")
