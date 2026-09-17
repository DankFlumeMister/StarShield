// dump-positions.mjs — 列出物理顺序的位置号与键位，供设计 keymap 使用
import fs from 'node:fs';
import { validateMatrix } from './matrix_schema.mjs';

const data = JSON.parse(fs.readFileSync('docs/_generated/matrix.json', 'utf8'));
validateMatrix(data, 'dump-positions'); // 字段白名单：未登记字段直接抛错
const keys = data.matrix.slice();
keys.sort((a, b) => (a.y_u - b.y_u) || (a.centerX_u - b.centerX_u));
keys.forEach((k, i) => { k.pos = i; });

// 也读 transform 里的 map，确保顺序一致
const t = fs.readFileSync('firmware/boards/shields/starshield/starshield_transform.dtsi', 'utf8');
const mapBlock = t.match(/map\s*=\s*<([\s\S]*?)>;/)[1];
const rc = [...mapBlock.matchAll(/RC\(\s*(\d+),\s*(\d+)\)/g)].map(m => [ +m[1], +m[2] ]);
let ok = true;
keys.forEach((k, i) => {
  if (rc[i][0] !== k.row || rc[i][1] !== k.col) { ok = false; console.log(`不一致 @${i}`); }
});
console.log(`transform 与 matrix.json 顺序一致: ${ok ? '✅' : '❌'}  (${rc.length} 条)`);

const byRow = new Map();
for (const k of keys) {
  if (!byRow.has(k.y_u)) byRow.set(k.y_u, []);
  byRow.get(k.y_u).push(k);
}

for (const y of [...byRow.keys()].sort((a, b) => a - b)) {
  const g = byRow.get(y);
  console.log(`\n===== 物理行 y=${y}u   位置 ${g[0].pos}–${g[g.length - 1].pos}  共 ${g.length} 键 =====`);
  // 按 x 分段：x<4 视为小键盘/导航区
  const np = g.filter(k => k.centerX_u < 4);
  const mb = g.filter(k => k.centerX_u >= 4);
  if (np.length) {
    console.log(`  小键盘/导航区 (x<4):  ${np.map(k => `${k.pos}:${k.label}`).join('  ')}`);
  }
  if (mb.length) {
    console.log(`  主键区 (x>=4):        ${mb.map(k => `${k.pos}:${k.label}`).join('  ')}`);
  }
  console.log(`  完整顺序:  ${g.map(k => `${k.pos}=${k.label}`).join('  ')}`);
}

// 校验总键数与行和
const rowSums = [16, 18, 18, 15, 17, 11].reduce((a, b) => a + b, 0);
console.log(`\n=== 行键数之和 = ${rowSums}  (应 = 95) ===`);
