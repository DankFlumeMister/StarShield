// gen_transform.mjs — 由 docs/_generated/matrix.json 生成 ZMK 键位映射表
//
// ZMK 的矩阵转换表把「键位序号（0 = 键盘左上角，按物理顺序）」映射到「矩阵格 (行, 列)」。
// 宏：RC(row, col) = ((row) << 8) + (col)   —— 见 ZMK 官方 dt-bindings/zmk/matrix_transform.h
//
// 排序规则（物理顺序，从上到下、从左到右）：
//   1) KLE 的 y（物理行，0 在上）
//   2) 同一物理行内按开关中心 x
// 这与「人眼扫过键盘」的顺序一致，因此 keymap 可以按直觉书写。
//
// 输出：
//   - 控制台预览
//   - firmware/boards/shields/starshield/starshield_transform.dtsi

import fs from 'node:fs';

const data = JSON.parse(fs.readFileSync('docs/_generated/matrix.json', 'utf8'));
const keys = data.matrix.slice();
const ROWS = data.rows, COLS = data.cols;

// 物理顺序排序
keys.sort((a, b) => (a.y_u - b.y_u) || (a.centerX_u - b.centerX_u));

// 位置号 = 物理顺序下标
keys.forEach((k, i) => { k.pos = i; });

const missing = keys.filter(k => k.row === undefined || k.col === undefined);
if (missing.length) throw new Error(`有 ${missing.length} 个键未分配矩阵格`);

// 校验：位置号唯一、矩阵格唯一、数量正确
const posSet = new Set(keys.map(k => k.pos));
const cellSet = new Set(keys.map(k => `${k.row}:${k.col}`));
if (posSet.size !== keys.length) throw new Error('位置号重复');
if (cellSet.size !== keys.length) throw new Error('矩阵格重复（短路！）');
if (keys.length !== 95) throw new Error(`键数应为 95，实际 ${keys.length}`);

console.log(`键数 ${keys.length}｜矩阵 ${ROWS} × ${COLS}`);
console.log(`位置号 0..${keys.length - 1} 唯一 ✅；矩阵格唯一 ✅（无冲突）`);

// 生成一张「物理顺序 → 矩阵格」的对照表，便于人眼核对
// ⚠️ 把任意文本安全地放进 DTS 的 /* */ 注释里。
//
// 本布局里有键位标签是 `*` 和 `/`（小键盘的乘除键），拼在一起就成了 `*/`，
// 会**提前闭合注释**：`/* ... */8 | (/9 */` —— 后面的内容变成代码，DTS 直接坏掉。
// 这与之前 KiCad 生成器踩过的「标签以反斜杠结尾」是同一类坑：**注释文本必须消毒**。
// 另外 `/*` 也要处理（会在注释里再开一层）。
function c(text) {
  return String(text).replace(/\*\//g, '* /').replace(/\/\*/g, '/ *');
}

const lines = [];
lines.push(`/*`);
lines.push(` * StarShield 键位映射表 + 物理布局（自动生成，请勿手改）`);
lines.push(` *`);
lines.push(` * 生成源：docs/_generated/matrix.json`);
lines.push(` * 生成脚本：docs/_tools/gen_transform.mjs`);
lines.push(` * 说明文档：docs/matrix-assignment.md`);
lines.push(` *`);
lines.push(` * 位置号按【物理顺序】排列（KLE 的 y 从上到下，同一行内按开关中心 x 从左到右），`);
lines.push(` * 因此 keymap 里第 0 个键就是键盘左上角那个键。`);
lines.push(` *`);
lines.push(` * 矩阵：${ROWS} 行 × ${COLS} 列，键数 ${keys.length}`);
lines.push(` *`);
lines.push(` * ⚠️ 采用 ZMK 的 physical-layout 模型（官方 physical-layouts.md）：`);
lines.push(` *    - physical_layout0 聚合 kscan + matrix transform + 可选按键物理位置`);
lines.push(` *    - keys 属性（centi-keyunit）是 ZMK Studio 支持所必需的`);
lines.push(` *    旧式 chosen { zmk,matrix-transform = ... } 已不再使用。`);
lines.push(` */`);
lines.push(``);
lines.push(`#include <physical_layouts.dtsi>`);
lines.push(`#include <dt-bindings/zmk/matrix_transform.h>`);
lines.push(``);
lines.push(`/ {`);
lines.push(`    physical_layout0: physical_layout_0 {`);
lines.push(`        compatible = "zmk,physical-layout";`);
lines.push(`        display-name = "StarShield 95";`);
lines.push(``);
lines.push(`        /* 取 KLE 坐标 ×100 得 centi-keyunit；顺序与 keymap 绑定严格一致 */`);
lines.push(`        keys  //                  w    h     x     y   rot  rx  ry`);
for (let i = 0; i < keys.length; i++) {
  const k = keys[i];
  const w = Math.round(k.w_u * 100);
  const h = Math.round(k.h_u * 100);
  const x = Math.round(k.x_u * 100);
  const y = Math.round(k.y_u * 100);
  const line = `            ${i === 0 ? '=' : ','} <&key_physical_attrs ${String(w).padStart(3)} ${String(h).padStart(3)} ${String(x).padStart(4)} ${String(y).padStart(4)}     0   0   0>`;
  lines.push(`${line}   /* ${c(String(i).padStart(2))} ${c(k.label)} */`);
}
lines.push(`            ;`);
lines.push(`    };`);
lines.push(`};`);
lines.push(``);
lines.push(`&physical_layout0 {`);
lines.push(`    transform = <&default_transform>;`);
lines.push(`};`);
lines.push(``);
lines.push(`/ {`);
lines.push(`    /*`);
lines.push(`     * 矩阵转换表：位置号 -> 矩阵格 (行, 列)。`);
lines.push(`     * 宏 RC(row, col) 来自 <dt-bindings/zmk/matrix_transform.h>。`);
lines.push(`     *`);
lines.push(`     * ⚠️ 必须用「节点定义」形式（label: node { ... }）而不是 &label { ... }：`);
lines.push(`     *    后者是 fragment 覆写，对【尚未定义】的新标签无效。`);
lines.push(`     */`);
lines.push(`    default_transform: keymap_transform_0 {`);
lines.push(`        compatible = "zmk,matrix-transform";`);
lines.push(`        columns = <${COLS}>;`);
lines.push(`        rows = <${ROWS}>;`);
lines.push(`        map = <`);

// ⚠️⚠️ `map` 里的 cell 用【空格分隔】，不用逗号。
//
// ZMK 官方 shield（a_dux / corne 等）的写法就是空格分隔：
//     map = <
//         RC(0,0)  RC(0,1)  RC(0,2)
//         RC(0,5)  RC(0,6)  RC(0,7)
//     >;
// 本项目最初按普通语言习惯写成「逗号分隔 + 行尾逗号」，CI 报：
//     devicetree error: starshield_transform.dtsi:144 (column 21):
//     parse error: expected number or parenthesized expression
// 改为与官方一致的空格分隔后通过。
//
// 另：本文件必须自己 #include <dt-bindings/zmk/matrix_transform.h> 以取得 RC 宏，
// 不能依赖包含它的 .overlay 代为引入（官方每个用 RC 的文件都自行 include）。
for (let i = 0; i < keys.length; i += 6) {
  const chunk = keys.slice(i, i + 6);
  const body = chunk.map(k => `RC(${k.row},${String(k.col).padStart(2)})`).join('  ');
  const labels = chunk.map(k => k.label).join(' | ');
  lines.push(`            ${body}   /* ${c(String(chunk[0].pos).padStart(2))}-${c(String(chunk[chunk.length - 1].pos).padStart(2))}  ${c(labels)} */`);
}
lines.push(`        >;`);
lines.push(`    };`);
lines.push(`};`);
lines.push(``);

// 附录：完整对照表（注释形式，便于人工核对）
lines.push(`/* 完整对照：位置号 → (行, 列) → 键位`);
for (const k of keys) {
  lines.push(` *   ${String(k.pos).padStart(2)}  RC(${k.row}, ${String(k.col).padStart(2)})  ${c(k.label)}   [x=${k.centerX_u.toFixed(3)}u y=${k.y_u}u]`);
}
lines.push(` */`);

const out = lines.join('\n') + '\n';
fs.mkdirSync('firmware/boards/shields/starshield', { recursive: true });
fs.writeFileSync('firmware/boards/shields/starshield/starshield_transform.dtsi', out, 'utf8');
console.log(`\n已写出 firmware/boards/shields/starshield/starshield_transform.dtsi（${out.length} 字节）`);

// 控制台预览：物理行分布
console.log('\n=== 位置号在各物理行的分布 ===');
const byRow = new Map();
for (const k of keys) {
  if (!byRow.has(k.y_u)) byRow.set(k.y_u, []);
  byRow.get(k.y_u).push(k);
}
for (const y of [...byRow.keys()].sort((a, b) => a - b)) {
  const g = byRow.get(y);
  console.log(`  y=${y}u  位置 ${g[0].pos}-${g[g.length - 1].pos}（${g.length} 键）`);
}
