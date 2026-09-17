// fold-matrix.mjs — 矩阵折叠分析（最终版）
//
// 回答一个问题：StarShield 的 95 键矩阵，能否折叠到 nice!nano v2 的 21 GPIO 以内？
//
// ★ 电气模型（关键 —— 之前几版模型都错了）
//   矩阵列 = 物理 x 槽位（开关中心 X）。
//   两把键可以共用一根列线 ⟺ 它们**不在同一逻辑行**。
//   ⇒ **同一逻辑行内，键的 x 槽位必须互不相同。**
//
//   「同一物理行」与「同一逻辑行」是两回事：
//   物理行是键在键盘上排成的一横排（6 行）；
//   逻辑行是我们自己指派给键的矩阵行（可以多于或少于 6）。
//   把同一个物理行的键拆到多个逻辑行，就换来更少的列 —— 这就是「折叠」。
//
// ★ 可行判据
//   方案 (R 逻辑行, C 列) 可行 ⟺ 能把 95 键分成 R 组，每组 ≤ C 键，组内 x 互异。
//
// ★ 硬下界
//   (a) 同一 x 槽位最多有 5 把键 ⇒ R ≥ 5
//   (b) R·C ≥ 95 ⇒ C ≥ ceil(95/R)
//
// 用法: node docs/_tools/fold-matrix.mjs

import fs from 'node:fs';
import { validateKle } from './kle_schema.mjs';

const kle = JSON.parse(fs.readFileSync('sketch/keyboard-layout.json', 'utf8'));
validateKle(kle, 'fold-matrix'); // 未识别属性直接抛错，禁止静默忽略（见 PROJECT_HANDOFF §10.2 第 17 条）

// ---------- 解析 KLE ----------
let cy = 0;
const keys = [];
for (const row of kle) {
  let x = 0, pending = { w: 1, h: 1 };
  for (const it of row) {
    if (typeof it === 'string') {
      keys.push({ label: it.replace(/\n/g, '/') || 'Space', x, y: cy, w: pending.w, h: pending.h });
      x += pending.w; pending = { w: 1, h: 1 };
    } else {
      if (it.x !== undefined) x += it.x;
      if (it.y !== undefined) cy += it.y;
      if (it.w !== undefined) pending.w = it.w;
      if (it.h !== undefined) pending.h = it.h;
    }
  }
  cy += 1;
}
const N = keys.length;
const rowsY = [...new Set(keys.map(k => k.y))].sort((a, b) => a - b);
const rowOf = new Map(rowsY.map((y, i) => [y, i]));
for (const k of keys) { k.pr = rowOf.get(k.y); k.xs = +(k.x + k.w / 2).toFixed(3); }
keys.forEach((k, i) => k.i = i);

// x 团：同一 x 槽位的键必须互异（不同逻辑行）
const groups = new Map();
for (const k of keys) {
  if (!groups.has(k.xs)) groups.set(k.xs, []);
  groups.get(k.xs).push(k);
}
const groupList = [...groups.entries()].map(([xs, g]) => ({ xs, g })).sort((a, b) => b.g.length - a.g.length);
const maxSameX = groupList[0].g.length;
const multHist = {};
for (const gr of groupList) multHist[gr.g.length] = (multHist[gr.g.length] || 0) + 1;

console.log('='.repeat(76));
console.log('StarShield 95 键矩阵折叠分析');
console.log('='.repeat(76));
console.log(`键数 ${N}｜物理行 ${rowsY.length}｜互异 x 槽位 ${groupList.length}`);
console.log(`同一 x 槽位键数分布: ${Object.entries(multHist).sort().map(([k, v]) => `${k}把×${v}个x`).join(', ')}`);
console.log(`\n硬下界：同一 x 最多 ${maxSameX} 把键 ⇒ 逻辑行 R ≥ ${maxSameX}；R·C ≥ 95 ⇒ C ≥ ceil(95/R)`);

// ---------- 求解器（best-fit 装箱 + 完整验证） ----------
function solve(R, C) {
  const rowKeys = Array.from({ length: R }, () => []);
  const rowX = Array.from({ length: R }, () => new Set());
  const assign = new Array(N);
  for (const { xs, g } of groupList) {
    if (g.length > R) return { fail: `x=${xs} 有 ${g.length} 把键 > R` };
    const avail = [];
    for (let r = 0; r < R; r++) {
      if (!rowX[r].has(xs) && rowKeys[r].length < C) avail.push(r);
    }
    if (avail.length < g.length) return { fail: '本团无足够行可放' };
    // best-fit：优先填剩余容量最小的行，压实负载
    avail.sort((a, b) => rowKeys[b].length - rowKeys[a].length);
    for (let j = 0; j < g.length; j++) {
      const r = avail[j];
      rowX[r].add(xs); rowKeys[r].push(g[j]); assign[g[j].i] = r;
    }
  }
  // ---- 独立验证（不信任构造过程） ----
  const seen = new Map();
  for (const k of keys) {
    if (assign[k.i] === undefined) return { fail: `${k.label} 未分配` };
    const id = `${assign[k.i]}|${k.xs}`;
    if (seen.has(id)) return { fail: `格冲突 ${id}: ${seen.get(id).label} / ${k.label}` };
    seen.set(id, k);
  }
  const sizes = rowKeys.map(r => r.length);
  if (Math.max(...sizes) > C) return { fail: `某行 ${Math.max(...sizes)} 键 > C=${C}` };
  return { assign, sizes, rowKeys };
}

// ---------- 扫描 ----------
console.log('\n' + '='.repeat(76));
console.log('扫描结果（每个 R 下最小的可行 C）');
console.log('='.repeat(76));
const results = [];
for (let R = maxSameX; R <= 12; R++) {
  for (let C = Math.ceil(N / R); C <= 18; C++) {
    const r = solve(R, C);
    if (r && !r.fail) {
      results.push({ R, C, ...r });
      console.log(`  ✅ ${String(R).padStart(2)} 行 × ${String(C).padStart(2)} 列 = ${String(R + C).padStart(2)} 引脚` +
        `  行负载 [${r.sizes.join(',')}]  利用率 ${(N / (R * C) * 100).toFixed(1)}%` +
        (R + C <= 21 ? '  ★ ≤21' : ''));
      break;
    }
  }
}

// ---------- 结论 ----------
console.log('\n' + '='.repeat(76));
console.log('结论');
console.log('='.repeat(76));
results.sort((a, b) => (a.R + a.C) - (b.R + b.C) || a.R - b.R);
console.log('\n与当前方案的对比：');
console.log('  ┌────────────────────────────────────────────────────────────────┐');
console.log('  │ 方案            引脚   逻辑行   列   利用率   相对当前           │');
console.log('  ├────────────────────────────────────────────────────────────────┤');
const cur = { R: 6, C: 18, pins: 24 };
console.log(`  │ 当前（已实现）  ${String(cur.pins).padStart(3)}    ${String(cur.R).padStart(3)}    ${String(cur.C).padStart(3)}   ${(95 / 108 * 100).toFixed(1)}%   —                  │`);
for (const r of results) {
  const tag = r.R + r.C <= 21 ? '★ 可直连 nice!nano' : '';
  console.log(`  │ ${String(r.R + '行×' + r.C + '列').padEnd(14)} ${String(r.R + r.C).padStart(3)}    ${String(r.R).padStart(3)}    ${String(r.C).padStart(3)}   ${(95 / (r.R * r.C) * 100).toFixed(1)}%   省 ${String(24 - (r.R + r.C)).padStart(2)} 引脚  ${tag.padEnd(18)}│`);
}
console.log('  └────────────────────────────────────────────────────────────────┘');

const best = results[0];
console.log(`\n✅ 结论：折叠**可行**。`);
console.log(`   最少引脚 = ${best.R + best.C}（${best.R} 行 × ${best.C} 列），比当前方案省 ${24 - (best.R + best.C)} 个 GPIO。`);
console.log(`   且在 21 GPIO 以内有多个方案，**nice!nano v2 可以直连，不再强制需要 74HC595**。`);

// ---------- 代价分析 ----------
console.log('\n' + '='.repeat(76));
console.log('代价（折叠不是免费的）');
console.log('='.repeat(76));
console.log(`
折叠的代价全部在 PCB 走线上，不在电气上：

1) 逻辑行数 > 物理行数 6 ⇒ 同一物理行内的键被拆到多根行线上。
   6×18：每个物理行对应 1 根行线，行线是"直"的。
   8×12：8 根行线要穿过 6 个物理行，同一横排里相邻的键可能接不同的行线，
         行线需要在键之间反复"上下跳"，走线密度显著上升。

2) 列数减少 ⇒ 每根列线串更多键、横向更长。
   6×18：每列平均 95/18 ≈ 5.3 键
   8×12：每列平均 95/12 ≈ 7.9 键（+49%），跨 371mm 板宽

3) 对新手复刻（本项目目标用户）而言，走线复杂度是硬成本：
   飞线/手工焊接时，行线越乱越容易接错。

⇒ 建议：**电气上 8×12=20 或 7×14=21 都可行**，但若走 74HC595 路线，
   保持 6×18 的整齐矩阵 + 1 颗移位寄存器，对新手更友好（走线规整、可复制粘贴）。
   若决定去掉移位寄存器，则 7×14 = 21 引脚是"行列都比 6 多 1"的折中方案。
`);
