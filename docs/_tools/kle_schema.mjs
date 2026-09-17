// kle_schema.mjs — sketch/keyboard-layout.json（KLE）的属性白名单校验（JS 侧）
//
// 为什么需要它：matrix-assign.mjs 曾只读 w/h，静默丢弃阶梯键的第二轮廓
// x2/y2/w2/h2，主键区 Enter 因此被下游当成完整矩形。
// 现在凡是解析 KLE 的脚本都必须先调用本模块，遇到未识别属性直接抛错。
//
// 白名单本身不在这里写死，而是读 docs/_tools/field_schema.json ——
// 与 Python 侧（matrix_schema.py）共用一份清单，避免两侧漂移。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SCHEMA_PATH = path.join(HERE, 'field_schema.json');

const schema = JSON.parse(fs.readFileSync(SCHEMA_PATH, 'utf8'));
export const KLE_GEOM = schema.kle.geom;
export const KLE_IGNORED = schema.kle.ignored;

const geomSet = new Set(KLE_GEOM);
const ignoredSet = new Set(KLE_IGNORED);

/**
 * 校验 KLE 数组。任何未登记属性都会抛错。
 * @param {Array} kle 已解析的 KLE JSON
 * @param {string} who 调用方名称（用于错误信息）
 */
export function validateKle(kle, who = 'caller') {
  if (!Array.isArray(kle)) {
    throw new Error(`[${who}] KLE 顶层不是数组`);
  }
  kle.forEach((row, rowIdx) => {
    if (!Array.isArray(row)) {
      throw new Error(
        `[${who}] KLE 第 ${rowIdx} 项不是数组（不支持顶层元数据对象）：${JSON.stringify(row)}`
      );
    }
    for (const it of row) {
      if (typeof it !== 'object' || it === null) continue; // 字符串 = 键帽图例
      for (const p of Object.keys(it)) {
        if (!geomSet.has(p) && !ignoredSet.has(p)) {
          throw new Error(
            `[${who}] KLE 第 ${rowIdx} 行出现未识别属性 "${p}"（对象 ${JSON.stringify(it)}）。\n` +
            `允许的几何属性：${KLE_GEOM.join('/')}；不参与计算的：${KLE_IGNORED.join('/')}。\n` +
            `新增属性必须先明确它对几何/定位板开孔的影响，并在 docs/_tools/field_schema.json 登记。`
          );
        }
      }
    }
  });
  return true;
}
