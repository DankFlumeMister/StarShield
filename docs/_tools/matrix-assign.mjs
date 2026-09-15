// matrix-assign.mjs — StarShield 95 键矩阵行列分配（最终分配表生成）
// 输入：sketch/keyboard-layout.json（KLE，唯一权威）
// 用法：node docs/_tools/matrix-assign.mjs [输出目录]
// 产出：docs/matrix-assignment.md 的表格数据 + 控制台报告
import fs from 'node:fs';

const kle = JSON.parse(fs.readFileSync('sketch/keyboard-layout.json', 'utf8'));

// ---------- 1. 解析 KLE（x/y 为累积偏移，作用于其后的键并持续累加） ----------
let cy = 0;
const keys = [];
for (const row of kle) {
  let x = 0;
  let pending = { w: 1, h: 1 };
  for (const it of row) {
    if (typeof it === 'string') {
      keys.push({ label: it.replace(/\n/g, '/'), x, y: cy, w: pending.w, h: pending.h });
      x += pending.w;
      pending = { w: 1, h: 1 };
    } else {
      if (it.x !== undefined) x += it.x;
      if (it.y !== undefined) cy += it.y;
      if (it.w !== undefined) pending.w = it.w;
      if (it.h !== undefined) pending.h = it.h;
    }
  }
  cy += 1;
}
if (keys.length !== 95) throw new Error(`expected 95 keys, got ${keys.length}`);

// ---------- 2. 行归属：以键位起始 y 归行（2u 高键归上排，符合矩阵惯例） ----------
const rowsY = [...new Set(keys.map(k => k.y))].sort((a, b) => a - b);
const rowOf = new Map(rowsY.map((y, i) => [y, i]));
for (const k of keys) {
  k.r = rowOf.get(k.y);
  k.cx = +(k.x + k.w / 2).toFixed(2); // 开关中心 X（u）
}

// ---------- 3. 矩阵列分配：同一矩阵列内不得出现同一行 ----------
// 按物理 X 从左到右处理；若与已有列冲突则新开一列。
// 该贪心解已达理论下界（单行最多 18 键 → 至少 18 列）。
const columns = []; // 每列：Set(已占用的行)
const assign = new Map(); // key -> colIndex
for (const k of keys.slice().sort((a, b) => a.cx - b.cx || a.r - b.r)) {
  let placed = false;
  for (let c = 0; c < columns.length; c++) {
    if (!columns[c].has(k.r)) { columns[c].add(k.r); assign.set(k, c); placed = true; break; }
  }
  if (!placed) { columns.push(new Set([k.r])); assign.set(k, columns.length - 1); }
}

const NROW = rowsY.length;
const NCOL = columns.length;

// ---------- 4. 校验 ----------
let errors = [];
const seen = new Set();
for (const k of keys) {
  const c = assign.get(k);
  const id = `${k.r}:${c}`;
  if (seen.has(id)) errors.push(`重复占用 row${k.r} col${c} -> ${k.label}`);
  seen.add(id);
  if (c === undefined || c < 0 || c >= NCOL) errors.push(`列越界: ${k.label}`);
  if (k.r < 0 || k.r >= NROW) errors.push(`行越界: ${k.label}`);
}
const coverage = [...seen].length;
console.log('================ 校验 ================');
console.log(`键数        : ${keys.length}`);
console.log(`行数        : ${NROW}   (Y = ${rowsY.join(', ')})`);
console.log(`列数        : ${NCOL}   (理论下界 = 单行最多键数 = ${Math.max(...rowsY.map((_, i) => keys.filter(k => k.r === i).length))})`);
console.log(`占用格数    : ${coverage} / ${NROW * NCOL}  (利用率 ${(coverage / (NROW * NCOL) * 100).toFixed(1)}%)`);
console.log(`重复占用    : ${errors.length === 0 ? '✅ 无' : '❌ ' + errors.join('; ')}`);
console.log(`所需 GPIO   : ${NROW} 行 + ${NCOL} 列 = ${NROW + NCOL} 个`);
console.log(`二极管数量  : ${keys.length}（每键一颗 1N4148 / SOD-123）`);

// ---------- 5. 每行键数 / 每列键数 ----------
console.log('\n================ 每行键数 ================');
for (let r = 0; r < NROW; r++) {
  const ks = keys.filter(k => k.r === r).sort((a, b) => a.cx - b.cx);
  console.log(`  行 R${r} (y=${rowsY[r]}u): ${String(ks.length).padStart(2)} 键  ${ks.map(k => k.label || '空格').join(' ')}`);
}
console.log('\n================ 每列键数 ================');
for (let c = 0; c < NCOL; c++) {
  const ks = keys.filter(k => assign.get(k) === c).sort((a, b) => a.r - b.r);
  console.log(`  列 C${String(c).padStart(2)}: ${String(ks.length).padStart(2)} 键  行[${ks.map(k => k.r).join(',')}]  x=[${ks.map(k => k.cx.toFixed(2)).join(', ')}]`);
}

// ---------- 6. 矩阵表 ----------
console.log('\n================ 矩阵占用表（行 × 列）================');
const header = '      ' + Array.from({ length: NCOL }, (_, c) => `C${String(c).padStart(2)}`).join(' ');
console.log(header);
for (let r = 0; r < NROW; r++) {
  const cells = [];
  for (let c = 0; c < NCOL; c++) {
    const k = keys.find(k => k.r === r && assign.get(k) === c);
    cells.push((k ? (k.label || 'SPACE').slice(0, 3) : '·').padEnd(4));
  }
  console.log(`  R${r}  ` + cells.join(''));
}

// ---------- 7. 输出 Markdown 表 ----------
// 注意：95 键完整分配表由 gen_matrix_doc.py 生成（带参考号与按行/列汇总）。
// 这里只输出机器可读 JSON，避免产生两份会漂移的表格。
fs.mkdirSync('docs/_generated', { recursive: true });
const json = {
  generatedBy: 'docs/_tools/matrix-assign.mjs',
  source: 'sketch/keyboard-layout.json',
  unitMM: 19.05,
  rows: NROW,
  cols: NCOL,
  gpioNeeded: NROW + NCOL,
  diodes: keys.length,
  keyCount: keys.length,
  matrix: keys.map((k, i) => ({
    index: i + 1,
    label: k.label || 'Space',
    row: k.r, col: assign.get(k),
    x_u: +k.x.toFixed(3), y_u: +k.y.toFixed(3),
    w_u: k.w, h_u: k.h,
    centerX_u: k.cx,
    centerX_mm: +(k.cx * 19.05).toFixed(3),
  })),
};
fs.writeFileSync('docs/_generated/matrix.json', JSON.stringify(json, null, 2) + '\n', 'utf8');
console.log('\n已写出 docs/_generated/matrix.json');
