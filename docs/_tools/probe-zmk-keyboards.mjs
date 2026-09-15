// probe-zmk-keyboards.mjs — 批量探测真实 ZMK 键盘仓库，找「电池 + RGB + ext-power」的实证
// 本环境 shell/Node 有网络；GitHub 代码搜索 API 需鉴权（401），故用 Trees API 枚举 + 抓取源文件后本地 grep。
import fs from 'node:fs';

const UA = { 'User-Agent': 'StarShield-research', Accept: 'application/vnd.github+json' };
const OUT = 'research/_web/repos/keyboard-probe.md';
fs.mkdirSync('research/_web/repos', { recursive: true });

const api = async (u) => {
  try { const r = await fetch(u, { headers: UA }); return r.ok ? await r.json() : null; } catch { return null; }
};
const raw = async (u) => {
  try { const r = await fetch(u, { headers: UA }); return r.ok ? await r.text() : null; } catch { return null; }
};

// 候选：真实的无線/分体 ZMK 键盘 shield 仓库（owner/repo）
const REPOS = [
  'zmkfirmware/zmk',
  'joric/nrfmicro',
  'foostan/crkbd',
  'splitkb/kyria',
  'splitkb/aurora-series',
  'keebio/keebio- keyboards',
  'qmk/qmk_firmware',
  'a741725193/zmk-keyboard-chocofi',
  'kumamuk-git/zmk-config',
  'petejohanson/zmk-config',
  'josedeborja/zmk-config',
  'caksoylar/zmk-config',
  'urob/zmk-config',
  'manna-harbour/miryoku_zmk',
  'nicekeyboards/nice-nano',
  'keychron/zmk-config',
  'artseyio/artsey',
  'hitsmaxft/zmk-keyboard-fingery',
  'braindefender/zmk-keyboard-totem',
  'e7d/zmk-keyboard-totem',
  'tapioki/zmk-keyboard-totem',
  'mike1808/zmk-keyboard-ferris',
  'sadekbaroudi/zmk-keyboards',
  'sadekbaroudi/fingerpunch',
  'kiselev-dv/zmk-keyboard-hummingbird',
  'sporkus/zmk-keyboard-lily58',
  'minusplusminus/zmk-keyboard-sweep',
  'dreymar/zmk-keyboard-jian',
  'freistil/zmk-keyboard-jian',
  'zeroeth/zmk-keyboard-skeletyl',
];

const results = [];
const errors = [];

for (const repo of REPOS) {
  const info = await api(`https://api.github.com/repos/${repo.replace(/ /g, '')}`);
  if (!info || info.message) { errors.push(repo); continue; }
  const branch = info.default_branch;
  const tree = await api(`https://api.github.com/repos/${info.full_name}/git/trees/${branch}?recursive=1`);
  if (!tree || !tree.tree) { errors.push(repo + ' (no tree)'); continue; }
  const files = tree.tree.filter(t => t.type === 'blob').map(t => t.path);

  // 关注的文件：devicetree / 关键配置
  const cand = files.filter(f => /\.(overlay|dts|dtsi|keymap|conf)$/i.test(f) || /\.kicad_sch$/i.test(f));
  const interesting = [];
  for (const f of cand) {
    // 只抓体积可能较小的
    const txt = await raw(`https://raw.githubusercontent.com/${info.full_name}/${branch}/${f}`);
    if (!txt) continue;
    const hasExt = /ext[-_]power/i.test(txt);
    const hasRgb = /(ws2812|sk6812|rgb|underglow)/i.test(txt);
    const hasBat = /(vbatt|battery|battery-voltage-divider|battery-nrf-vddh)/i.test(txt);
    if (hasExt || hasRgb || hasBat) {
      interesting.push({ f, hasExt, hasRgb, hasBat, len: txt.length });
      if (hasExt) {
        // 抽取 ext-power 节点片段
        const m = txt.match(/EXT_POWER\s*\{[\s\S]{0,400}?\};/i) || txt.match(/ext[-_]power[\s\S]{0,300}/i);
        results.push({ repo: info.full_name, branch, file: f, snip: (m ? m[0] : '').slice(0, 400) });
      }
    }
  }
  if (interesting.length) {
    results.push({ repo: info.full_name, branch, file: '(summary)', snip: interesting.map(i =>
      `${i.f}  ext=${i.hasExt ? 'Y' : '-'} rgb=${i.hasRgb ? 'Y' : '-'} bat=${i.hasBat ? 'Y' : '-'}`).join('\n') });
  }
  console.log(`${info.full_name.padEnd(42)} branch=${branch.padEnd(8)} files=${String(files.length).padStart(5)} 命中=${interesting.length}`);
}

const lines = ['# 真实 ZMK 键盘仓库探测结果\n', `生成时间：${new Date().toISOString()}\n`];
lines.push(`探测仓库 ${REPOS.length} 个，成功 ${REPOS.length - errors.length} 个。\n`);
if (errors.length) lines.push(`\n无法访问：${errors.join(', ')}\n`);
for (const r of results) {
  lines.push(`\n## ${r.repo}@${r.branch} — ${r.file}\n`);
  lines.push('```\n' + r.snip + '\n```');
}
fs.writeFileSync(OUT, lines.join('\n') + '\n', 'utf8');
console.log(`\n已写出 ${OUT}`);
