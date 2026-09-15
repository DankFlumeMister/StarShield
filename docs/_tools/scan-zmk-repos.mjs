// scan-zmk-repos.mjs — 用 GitHub API 枚举真实键盘仓库并抓取其源文件，
// 找 ext-power 门控 / 电源开关 / 移位寄存器 / 矩阵引脚分配的实际做法。
import fs from 'node:fs';

const UA = { 'User-Agent': 'StarShield-research', Accept: 'application/vnd.github+json' };
const OUTDIR = 'research/_web/repos';
fs.mkdirSync(OUTDIR, { recursive: true });

const getJSON = async (u) => {
  try {
    const r = await fetch(u, { headers: UA });
    return r.ok ? await r.json() : null;
  } catch { return null; }
};
const getText = async (u) => {
  try {
    const r = await fetch(u, { headers: UA });
    return r.ok ? await r.text() : null;
  } catch { return null; }
};

// 1) 列出仓库的完整文件树
async function tree(repo, branch) {
  const j = await getJSON(`https://api.github.com/repos/${repo}/git/trees/${branch}?recursive=1`);
  if (!j || !j.tree) return [];
  return j.tree.filter(t => t.type === 'blob').map(t => t.path);
}

const REPOS = [
  ['zmkfirmware/zmk', 'main'],
  ['joric/nrfmicro', 'main'],
  ['foostan/crkbd', 'main'],
];

// 我们关心的文件模式
const INTEREST = [
  /\.overlay$/i, /\.dtsi?$/i, /\.keymap$/i, /\.conf$/i,
  /\.kicad_sch$/i, /\.kicad_pcb$/i, /\.kicad_sym$/i,
  /\.md$/i, /\.ya?ml$/i,
];

const report = [];
report.push('# 真实键盘仓库扫描（GitHub API）\n');
report.push(`生成时间：${new Date().toISOString()}\n`);

for (const [repo, branch] of REPOS) {
  console.log(`\n=== ${repo}@${branch} ===`);
  const files = await tree(repo, branch);
  console.log(`  文件总数 ${files.length}`);
  const interesting = files.filter(f => INTEREST.some(re => re.test(f)));
  console.log(`  关注文件 ${interesting.length}`);

  // 优先抓取的关键词文件
  const priority = interesting.filter(f =>
    /ext.?power|ext_power/i.test(f) ||
    /nrfmicro.*\.(dts|dtsi|overlay)$/i.test(f) ||
    /shield|board/i.test(f) && /\.(overlay|dtsi?)$/i.test(f) ||
    /power/i.test(f) ||
    f.endsWith('.kicad_sch')
  );
  console.log(`  优先抓取 ${priority.length} 个`);

  report.push(`\n## ${repo}@${branch}\n`);
  report.push(`- 文件总数：${files.length}；关注文件：${interesting.length}；优先抓取：${priority.length}\n`);

  if (priority.length) {
    report.push('\n### 优先文件清单\n');
    for (const f of priority.slice(0, 80)) report.push(`- \`${f}\``);
  }
  fs.writeFileSync(`${OUTDIR}/${repo.replace('/', '__')}.tree.txt`, files.join('\n'), 'utf8');
}

fs.writeFileSync('research/_web/repo-trees.md', report.join('\n') + '\n', 'utf8');
console.log('\n已写出 research/_web/repo-trees.md 与各仓库 tree 清单');
