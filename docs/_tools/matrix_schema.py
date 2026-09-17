#!/usr/bin/env python3
"""matrix_schema.py — docs/_generated/matrix.json 的字段白名单校验

为什么需要它：
上一次事故的根因是「上游生成器静默丢弃了 KLE 的第二轮廓 x2/y2/w2/h2」，
主 Enter 的异形轮廓因此丢失，被下游当成完整矩形。上游已经改成遇到未识别属性
直接抛错；这里是第二跳 —— 下游脚本（gen_matrix_sch / gen_matrix_doc）读的是
matrix.json，同样不能对字段视而不见。

约定：
- 顶层字段与每条键位记录的字段都在白名单内才允许通过；
- 出现白名单外的字段一律报错（不是警告），逼迫先明确它对几何/开孔的影响；
- 缺少必需字段同样报错。
"""
import sys

TOP_FIELDS = {
    "generatedBy", "source", "unitMM", "rows", "cols",
    "gpioNeeded", "diodes", "keyCount", "matrix",
}

# 每条键位记录：必需字段（所有键都有）
KEY_REQUIRED = {
    "index", "label", "row", "col",
    "x_u", "y_u", "w_u", "h_u",
    "centerX_u", "centerX_mm",
}

# 每条键位记录：可选字段（仅异形/阶梯键出现）
KEY_OPTIONAL = {
    "stepped", "x2_u", "y2_u", "w2_u", "h2_u",
    "unionX_u", "unionW_u",
}


def validate(data):
    """校验 matrix.json 的字段集合。不合规时抛 ValueError。"""
    if not isinstance(data, dict):
        raise ValueError("顶层不是 JSON 对象")

    unknown_top = sorted(set(data) - TOP_FIELDS)
    if unknown_top:
        raise ValueError(
            "顶层出现未识别字段：%s\n"
            "已知字段：%s\n"
            "新增字段必须先明确其含义与下游用途，禁止静默忽略。"
            % (", ".join(unknown_top), ", ".join(sorted(TOP_FIELDS)))
        )

    missing_top = sorted(TOP_FIELDS - set(data))
    if missing_top:
        raise ValueError("顶层缺少字段：%s" % ", ".join(missing_top))

    matrix = data.get("matrix")
    if not isinstance(matrix, list):
        raise ValueError("matrix 字段不是数组")

    allowed = KEY_REQUIRED | KEY_OPTIONAL
    for i, k in enumerate(matrix, 1):
        if not isinstance(k, dict):
            raise ValueError("matrix[%d] 不是对象" % i)
        unknown = sorted(set(k) - allowed)
        if unknown:
            raise ValueError(
                "键位 %s（matrix[%d]）出现未识别字段：%s\n"
                "已知必需字段：%s\n"
                "已知可选字段（异形键）：%s\n"
                "新增字段必须先明确其对几何/定位板开孔的影响，禁止静默忽略。"
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
    import json
    with open(sys.argv[1] if len(sys.argv) > 1 else "docs/_generated/matrix.json",
              encoding="utf-8") as f:
        validate(json.load(f))
    print("✅ matrix.json 字段校验通过")
