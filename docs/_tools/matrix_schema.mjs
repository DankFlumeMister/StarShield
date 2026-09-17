// matrix_schema.mjs — docs/_generated/matrix.json 的字段白名单校验（JS 侧）
//
// 与 Python 侧的 matrix_schema.py 共用同一份清单（docs/_tools/field_schema.json），
// 避免「上游加了字段、下游视而不见」的事故重演。
// 凡读取 matrix.json 的脚本都应在载入后立即调用 validateMatrix()。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const schema = JSON.parse(fs.readFileSync(path.join(HERE, 'field_schema.json'), 'utf8'));

export const MATRIX_TOP = schema.matrix.top;
export const MATRIX_KEY_REQUIRED = schema.matrix.keyRequired;
export const MATRIX_KEY_OPTIONAL = schema.matrix.keyOptional;

const topSet = new Set(MATRIX_TOP);
const requiredSet = new Set(MATRIX_KEY_REQUIRED);
const allowedKeySet = new Set([...MATRIX_KEY_REQUIRED, ...MATRIX_KEY_OPTIONAL]);

/**
 * 校验 matrix.json 的字段集合。不合规时抛错。
 * @param {object} data 已解析的 matrix.json
 * @param {string} who 调用方名称（用于错误信息）
 */
export function validateMatrix(data, who = 'caller') {
  if (typeof data !== 'object' || data === null || Array.isArray(data)) {
    throw new Error(`[${who}] matrix.json 顶层不是对象`);
  }

  const unknownTop = Object.keys(data).filter((k) => !topSet.has(k)).sort();
  if (unknownTop.length) {
    throw new Error(
      `[${who}] matrix.json 顶层出现未识别字段：${unknownTop.join(', ')}\n` +
      `已知字段：${MATRIX_TOP.join(', ')}\n` +
      `新增字段请在 docs/_tools/field_schema.json 登记，并明确下游用途。`
    );
  }

  const missingTop = MATRIX_TOP.filter((k) => !(k in data));
  if (missingTop.length) {
    throw new Error(`[${who}] matrix.json 顶层缺少字段：${missingTop.join(', ')}`);
  }

  if (!Array.isArray(data.matrix)) {
    throw new Error(`[${who}] matrix 字段不是数组`);
  }

  data.matrix.forEach((k, i) => {
    if (typeof k !== 'object' || k === null) {
      throw new Error(`[${who}] matrix[${i}] 不是对象`);
    }
    const unknown = Object.keys(k).filter((f) => !allowedKeySet.has(f)).sort();
    if (unknown.length) {
      throw new Error(
        `[${who}] 键位 ${JSON.stringify(k.label)}（matrix[${i}]）出现未识别字段：${unknown.join(', ')}\n` +
        `必需字段：${MATRIX_KEY_REQUIRED.join(', ')}\n` +
        `可选字段（异形键）：${MATRIX_KEY_OPTIONAL.join(', ')}\n` +
        `新增字段请先在 docs/_tools/field_schema.json 登记。`
      );
    }
    const missing = MATRIX_KEY_REQUIRED.filter((f) => !(f in k));
    if (missing.length) {
      throw new Error(
        `[${who}] 键位 ${JSON.stringify(k.label)}（matrix[${i}]）缺少必需字段：${missing.join(', ')}`
      );
    }
  });

  return true;
}
