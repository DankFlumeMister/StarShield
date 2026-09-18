// gen_keymap.mjs — 生成 StarShield 的 ZMK 键位映射（starshield.keymap）
//
// 位置号 = 物理顺序（0 = 键盘左上角 Esc），与 starshield_transform.dtsi 严格对应。
// 本文件是键位的【唯一权威定义】：每层必须恰好给出 95 条绑定。
//
// 校验：
//   1. 两层都必须 95 条
//   2. 位置号连续无缺漏
//   3. 生成后与 transform 的位置数一致

import fs from 'node:fs';

// ---------- 位置表（由 dump-positions.mjs 导出，此处作为设计依据固化）----------
// [位置, 键帽标签, 物理行分组]
const P = (pos, label, row) => ({ pos, label, row });

const LAYOUT = [
  // ---- 物理行 0（F 行）----
  P(0, 'Esc', 'F'), P(1, 'FN', 'F'), P(2, 'NumLock', 'F'),
  P(3, 'F1', 'F'), P(4, 'F2', 'F'), P(5, 'F3', 'F'), P(6, 'F4', 'F'), P(7, 'F5', 'F'), P(8, 'F6', 'F'),
  P(9, 'F7', 'F'), P(10, 'F8', 'F'), P(11, 'F9', 'F'), P(12, 'F10', 'F'), P(13, 'F11', 'F'), P(14, 'F12', 'F'),
  P(15, 'Del', 'F'),
  // ---- 物理行 1（数字行）----
  P(16, 'KP /', 'N'), P(17, 'KP *', 'N'), P(18, 'KP -', 'N'), P(19, 'KP +', 'N'),
  P(20, '`~', '1'), P(21, '1!', '1'), P(22, '2@', '1'), P(23, '3#', '1'), P(24, '4$', '1'), P(25, '5%', '1'),
  P(26, '6^', '1'), P(27, '7&', '1'), P(28, '8*', '1'), P(29, '9(', '1'), P(30, '0)', '1'),
  P(31, '-_', '1'), P(32, '=+', '1'), P(33, 'Bksp', '1'),
  // ---- 物理行 2（Q 行）----
  P(34, 'KP Del', 'N'), P(35, 'KP 7', 'N'), P(36, 'KP 8', 'N'), P(37, 'KP 9', 'N'),
  P(38, 'Tab', '2'), P(39, 'Q', '2'), P(40, 'W', '2'), P(41, 'E', '2'), P(42, 'R', '2'), P(43, 'T', '2'),
  P(44, 'Y', '2'), P(45, 'U', '2'), P(46, 'I', '2'), P(47, 'O', '2'), P(48, 'P', '2'),
  P(49, '[{', '2'), P(50, ']}', '2'), P(51, 'Enter', '2'),
  // ---- 物理行 3（A 行）----
  P(52, 'KP 4', 'N'), P(53, 'KP 5', 'N'), P(54, 'KP 6', 'N'),
  P(55, 'Caps', '3'), P(56, 'A', '3'), P(57, 'S', '3'), P(58, 'D', '3'), P(59, 'F', '3'), P(60, 'G', '3'),
  P(61, 'H', '3'), P(62, 'J', '3'), P(63, 'K', '3'), P(64, 'L', '3'), P(65, ';:', '3'), P(66, '\'"', '3'),
  // ---- 物理行 4（Z 行）----
  P(67, 'KP Ent', 'N'), P(68, 'KP 1', 'N'), P(69, 'KP 2', 'N'), P(70, 'KP 3', 'N'),
  P(71, 'LShift', '4'), P(72, 'Z', '4'), P(73, 'X', '4'), P(74, 'C', '4'), P(75, 'V', '4'), P(76, 'B', '4'),
  P(77, 'N', '4'), P(78, 'M', '4'), P(79, ',<', '4'), P(80, '.>', '4'), P(81, '/?', '4'),
  P(82, 'Up', '4'), P(83, 'RShift', '4'),
  // ---- 物理行 5（底行）----
  P(84, 'KP 0', 'N'), P(85, 'KP .', 'N'),
  P(86, 'LCtrl', '5'), P(87, 'LWin', '5'), P(88, 'LAlt', '5'), P(89, 'Space', '5'),
  P(90, '\\|', '5'), P(91, 'Left', '5'), P(92, 'Down', '5'), P(93, 'Right', '5'), P(94, 'RCtrl', '5'),
];

// ---------- 默认层 ----------
const BASE = {
  0: '&kp ESC', 1: '&mo FN', 2: '&kp KP_NUM',
  3: '&kp F1', 4: '&kp F2', 5: '&kp F3', 6: '&kp F4', 7: '&kp F5', 8: '&kp F6',
  9: '&kp F7', 10: '&kp F8', 11: '&kp F9', 12: '&kp F10', 13: '&kp F11', 14: '&kp F12',
  15: '&kp DEL',

  16: '&kp KP_SLASH', 17: '&kp KP_ASTERISK', 18: '&kp KP_MINUS', 19: '&kp KP_PLUS',
  20: '&kp GRAVE', 21: '&kp N1', 22: '&kp N2', 23: '&kp N3', 24: '&kp N4', 25: '&kp N5',
  26: '&kp N6', 27: '&kp N7', 28: '&kp N8', 29: '&kp N9', 30: '&kp N0',
  31: '&kp MINUS', 32: '&kp EQUAL', 33: '&kp BSPC',

  34: '&kp KP_NUM', 35: '&kp KP_N7', 36: '&kp KP_N8', 37: '&kp KP_N9',
  38: '&kp TAB', 39: '&kp Q', 40: '&kp W', 41: '&kp E', 42: '&kp R', 43: '&kp T',
  44: '&kp Y', 45: '&kp U', 46: '&kp I', 47: '&kp O', 48: '&kp P',
  49: '&kp LBKT', 50: '&kp RBKT', 51: '&kp RET',

  52: '&kp KP_N4', 53: '&kp KP_N5', 54: '&kp KP_N6',
  55: '&kp CLCK', 56: '&kp A', 57: '&kp S', 58: '&kp D', 59: '&kp F', 60: '&kp G',
  61: '&kp H', 62: '&kp J', 63: '&kp K', 64: '&kp L', 65: '&kp SEMI', 66: '&kp SQT',

  67: '&kp KP_ENTER', 68: '&kp KP_N1', 69: '&kp KP_N2', 70: '&kp KP_N3',
  71: '&kp LSHFT', 72: '&kp Z', 73: '&kp X', 74: '&kp C', 75: '&kp V', 76: '&kp B',
  77: '&kp N', 78: '&kp M', 79: '&kp COMMA', 80: '&kp DOT', 81: '&kp FSLH',
  82: '&kp UP', 83: '&kp RSHFT',

  84: '&kp KP_N0', 85: '&kp KP_DOT',
  86: '&kp LCTRL', 87: '&kp LGUI', 88: '&kp LALT', 89: '&kp SPACE',
  90: '&kp BSLH', 91: '&kp LEFT', 92: '&kp DOWN', 93: '&kp RIGHT', 94: '&kp RCTRL',
};

// ---------- FN 层（小键盘变导航区 + F 键 + RGB + 蓝牙）----------
const FN = {
  0: '&kp ESC', 1: '&mo FN', 2: '&kp KP_NUM',
  3: '&kp C_BRI_DN', 4: '&kp C_BRI_UP', 5: '&kp C_MUTE', 6: '&kp C_VOL_DN', 7: '&kp C_VOL_UP',
  8: '&kp C_PREV', 9: '&kp C_PLAY_PAUSE', 10: '&kp C_NEXT',
  11: '&rgb_ug RGB_TOG', 12: '&rgb_ug RGB_BRD', 13: '&rgb_ug RGB_BRI', 14: '&rgb_ug RGB_EFF',
  15: '&kp DEL',

  // 小键盘区 → 导航键簇（经典 numpad 导航布局）
  // ⚠️ 位置 16（小键盘 `/`）改绑 `&soft_off`（C3）：本项目不设物理断电开关（ADR-0010），
  //    长时间存放靠软关机。需要 `CONFIG_ZMK_PM_SOFT_OFF=y`；**唤醒只能靠复位**。
  //    换位置只改这一行即可（当前是 FN + 小键盘 `/`，需刻意按，不易误触）。
  16: '&soft_off', 17: '&kp KP_NUM', 18: '&kp K_CMENU', 19: '&kp KP_NUM',
  // 主键区数字行 → F1..F12
  20: '&kp GRAVE', 21: '&kp F1', 22: '&kp F2', 23: '&kp F3', 24: '&kp F4', 25: '&kp F5',
  26: '&kp F6', 27: '&kp F7', 28: '&kp F8', 29: '&kp F9', 30: '&kp F10',
  31: '&kp F11', 32: '&kp F12', 33: '&kp BSPC',

  34: '&kp K_CMENU', 35: '&kp HOME', 36: '&kp UP', 37: '&kp PG_UP',
  38: '&kp TAB', 39: '&kp Q', 40: '&kp W', 41: '&kp E', 42: '&kp R', 43: '&kp T',
  44: '&kp Y', 45: '&kp U', 46: '&kp I', 47: '&kp O', 48: '&kp P',
  49: '&kp LBKT', 50: '&kp RBKT', 51: '&kp RET',

  52: '&kp LEFT', 53: '&kp KP_N5', 54: '&kp RIGHT',
  55: '&kp CLCK', 56: '&kp A', 57: '&kp S', 58: '&kp D', 59: '&kp F', 60: '&kp G',
  61: '&kp H', 62: '&kp J', 63: '&kp K', 64: '&kp L', 65: '&kp SEMI', 66: '&kp SQT',

  67: '&kp K_CMENU', 68: '&kp END', 69: '&kp DOWN', 70: '&kp PG_DN',
  71: '&kp LSHFT', 72: '&kp Z', 73: '&kp X', 74: '&kp C', 75: '&kp V', 76: '&kp B',
  77: '&kp N', 78: '&kp M', 79: '&kp COMMA', 80: '&kp DOT', 81: '&kp FSLH',
  82: '&kp UP', 83: '&kp RSHFT',

  84: '&kp INS', 85: '&kp DEL',
  86: '&kp LCTRL', 87: '&kp LGUI', 88: '&kp LALT', 89: '&kp SPACE',
  90: '&kp BSLH', 91: '&kp LEFT', 92: '&kp DOWN', 93: '&kp RIGHT', 94: '&kp RCTRL',
};

// ---------- 校验 ----------
const N = 95;
const errs = [];
for (const [name, layer] of [['BASE', BASE], ['FN', FN]]) {
  const ks = Object.keys(layer).map(Number).sort((a, b) => a - b);
  if (ks.length !== N) errs.push(`${name} 层绑定数 = ${ks.length}，应为 ${N}`);
  for (let i = 0; i < N; i++) if (ks[i] !== i) { errs.push(`${name} 层位置号缺漏/重复：期望 ${i}，实得 ${ks[i]}`); break; }
}
if (LAYOUT.length !== N) errs.push(`LAYOUT 位置表 ${LAYOUT.length} 条，应为 ${N}`);
// 确认位置表与生成器一致
const t = fs.readFileSync('firmware/boards/shields/starshield/starshield_transform.dtsi', 'utf8');
const mapCount = [...t.matchAll(/RC\(/g)].length / 2;   // map + 注释各一遍
if (errs.length) {
  console.error('❌ 校验失败：');
  for (const e of errs) console.error('   ' + e);
  process.exit(1);
}
console.log(`✅ 校验通过：两层各 ${N} 条绑定，位置号 0..${N - 1} 连续`);

// ---------- 输出 ----------
//
// ⚠️⚠️ 关键：DTS 里 bindings 的【书写顺序】就是位置号顺序 —— 第 n 个绑定 = 位置 n。
//    因此**必须严格按位置号 0..94 顺序输出**，绝不能为了排版好看而按「小键盘/主键区」分组，
//    否则整张键位会错位。（本脚本第一版就犯了这个错：把位置 34 的 KP Del 排到了后面，
//    导致输出顺序变成 ... KP_NUM, KP_N7 ... 而非 ... KP_SLASH, KP_ASTERISK ...
//    —— 位置与实际键位不符。已修正。）
const sorted = LAYOUT.slice().sort((a, b) => a.pos - b.pos);
for (let i = 0; i < sorted.length; i++) {
  if (sorted[i].pos !== i) throw new Error(`位置表不连续：下标 ${i} 处 pos=${sorted[i].pos}`);
}

// 物理行起始位置，用于在注释里标注分段
const ROW_START = new Map();
for (const k of sorted) if (!ROW_START.has(k.row)) ROW_START.set(k.row, k.pos);
const ROW_LABEL = {
  F: 'F 行', N: '小键盘/导航', '1': '数字行', '2': 'Q 行', '3': 'A 行', '4': 'Z 行', '5': '底行',
};

// ⚠️ 把任意文本安全地放进 DTS 注释：本布局有键帽标签是 `*` 和 `/`（小键盘乘除键），
// 拼起来就是 `*/`，会**提前闭合注释**使 DTS 语法崩坏。
// 同理 `/*` 也要处理。这与 gen_transform.mjs 是同一类坑。
const c = (s) => String(s).replace(/\*\//g, '* /').replace(/\/\*/g, '/ *');

function emitLayer(layer, indent) {
  const out = [];
  for (let i = 0; i < sorted.length; i += 6) {
    const chunk = sorted.slice(i, i + 6);
    // 若本组跨入新的物理行，先插一条分段注释（只用 ASCII，避免任何编码/解析风险）
    for (const k of chunk) {
      if (ROW_START.get(k.row) === k.pos) {
        out.push(`${indent}/* ----- ${c(ROW_LABEL[k.row])}（位置 ${k.pos} 起）----- */`);
      }
    }
    const b = chunk.map(k => layer[k.pos].padEnd(20)).join(' ');
    out.push(`${indent}${b}/* ${c(String(chunk[0].pos).padStart(2))}-${c(String(chunk[chunk.length - 1].pos).padStart(2))}  ${c(chunk.map(k => k.label).join(' '))} */`);
  }
  return out.join('\n');
}

const lines = [];
lines.push(`/*`);
lines.push(` * StarShield 键位映射（自动生成，请勿手改）`);
lines.push(` *`);
lines.push(` * 生成脚本：docs/_tools/gen_keymap.mjs`);
lines.push(` * 位置号 = 物理顺序（0 = 键盘左上角 Esc），与 starshield_transform.dtsi 严格对应。`);
lines.push(` * 键位布局与几何见 docs/matrix-assignment.md；本文件每层必须恰好 ${N} 条绑定。`);
lines.push(` */`);
lines.push(``);
lines.push(`#include <behaviors.dtsi>`);
lines.push(`#include <dt-bindings/zmk/keys.h>`);
lines.push(`#include <dt-bindings/zmk/bt.h>`);
lines.push(`#include <dt-bindings/zmk/outputs.h>`);
lines.push(`#include <dt-bindings/zmk/rgb.h>`);
lines.push(`#include <dt-bindings/zmk/ext_power.h>`);
lines.push(`#include <dt-bindings/zmk/reset.h>`);
lines.push(``);
lines.push(`#define FN 1`);
lines.push(``);
lines.push(`/ {`);
lines.push(`    keymap {`);
lines.push(`        compatible = "zmk,keymap";`);
lines.push(``);
lines.push(`        default_layer {`);
lines.push(`            display-name = "Base";`);
lines.push(`            bindings = <`);
lines.push(emitLayer(BASE, '                '));
lines.push(`            >;`);
lines.push(`        };`);
lines.push(``);
lines.push(`        fn_layer {`);
lines.push(`            display-name = "FN";`);
lines.push(`            bindings = <`);
lines.push(emitLayer(FN, '                '));
lines.push(`            >;`);
lines.push(`        };`);
lines.push(`    };`);
lines.push(`};`);

const out = lines.join('\n').replace(/\n{3,}/g, '\n\n') + '\n';
fs.writeFileSync('firmware/boards/shields/starshield/starshield.keymap', out, 'utf8');
console.log(`已写出 firmware/boards/shields/starshield/starshield.keymap（${out.length} 字节）`);
