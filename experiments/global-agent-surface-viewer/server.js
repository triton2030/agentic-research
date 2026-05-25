import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

import express from 'express';
import fg from 'fast-glob';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const require = createRequire(import.meta.url);

const HOME = os.homedir();
const HOST = '127.0.0.1';
const DEFAULT_PORT = 8765;
const DOCSIFY_ROOT = path.dirname(require.resolve('docsify/package.json'));
const PRISM_ROOT = path.dirname(require.resolve('prismjs/package.json'));
const SIDEBAR_COLLAPSE_ROOT = path.dirname(require.resolve('docsify-sidebar-collapse/package.json'));

const SECTION_ORDER = ['Skills', 'Global Instructions', 'Hooks', 'Agents', 'Runtime Config'];
const PLATFORM_ORDER = ['Codex', 'Claude', 'Agents Compat'];

const TEXT_EXTENSIONS = new Set([
  '.md',
  '.markdown',
  '.yaml',
  '.yml',
  '.json',
  '.toml',
  '.py',
  '.js',
  '.mjs',
  '.cjs',
  '.sh',
  '.txt'
]);

const MARKDOWN_EXTENSIONS = new Set(['.md', '.markdown']);

const FORBIDDEN_SEGMENTS = new Set([
  'auth',
  'history',
  'sessions',
  'logs',
  'log',
  'state',
  'cache',
  'backups',
  'backup',
  '__pycache__',
  'node_modules',
  'dist',
  'runs'
]);

const FORBIDDEN_FILE_EXTENSIONS = new Set([
  '.sqlite',
  '.sqlite3',
  '.db',
  '.db3',
  '.wal',
  '.shm',
  '.bak',
  '.tmp',
  '.pyc'
]);

const SOURCES = [
  {
    section: 'Skills',
    platform: 'Codex',
    root: path.join(HOME, '.codex', 'skills'),
    pattern: '**/*'
  },
  {
    section: 'Skills',
    platform: 'Claude',
    root: path.join(HOME, '.claude', 'skills'),
    pattern: '**/*'
  },
  {
    section: 'Skills',
    platform: 'Agents Compat',
    root: path.join(HOME, '.agents', 'skills'),
    pattern: '**/*'
  },
  {
    section: 'Global Instructions',
    platform: 'Codex',
    files: [path.join(HOME, '.codex', 'AGENTS.md')]
  },
  {
    section: 'Global Instructions',
    platform: 'Claude',
    files: [path.join(HOME, '.claude', 'CLAUDE.md')]
  },
  {
    section: 'Hooks',
    platform: 'Codex',
    root: path.join(HOME, '.codex', 'hooks'),
    pattern: '*.py'
  },
  {
    section: 'Hooks',
    platform: 'Claude',
    root: path.join(HOME, '.claude', 'hooks'),
    pattern: '*.py'
  },
  {
    section: 'Agents',
    platform: 'Codex',
    root: path.join(HOME, '.codex', 'agents'),
    pattern: '*.toml'
  },
  {
    section: 'Agents',
    platform: 'Claude',
    root: path.join(HOME, '.claude', 'agents'),
    pattern: '*.md'
  },
  {
    section: 'Runtime Config',
    platform: 'Codex',
    files: [path.join(HOME, '.codex', 'config.toml')]
  },
  {
    section: 'Runtime Config',
    platform: 'Claude',
    files: [
      path.join(HOME, '.claude', 'settings.json'),
      path.join(HOME, '.claude', 'settings.local.json')
    ]
  }
];

const ALLOWED_ROOTS = [
  path.join(HOME, '.codex', 'skills'),
  path.join(HOME, '.claude', 'skills'),
  path.join(HOME, '.agents', 'skills'),
  path.join(HOME, '.codex', 'hooks'),
  path.join(HOME, '.claude', 'hooks'),
  path.join(HOME, '.codex', 'agents'),
  path.join(HOME, '.claude', 'agents'),
  path.join(HOME, '.codex'),
  path.join(HOME, '.claude')
].map((root) => path.resolve(root));

function parseArgs(argv) {
  const args = { check: false, port: DEFAULT_PORT };

  for (let index = 2; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--check') {
      args.check = true;
    } else if (arg === '--port') {
      args.port = Number(argv[index + 1]);
      index += 1;
    } else if (arg.startsWith('--port=')) {
      args.port = Number(arg.slice('--port='.length));
    }
  }

  if (!Number.isInteger(args.port) || args.port < 1 || args.port > 65535) {
    throw new Error(`Invalid port: ${args.port}`);
  }

  return args;
}

function hasForbiddenSegment(filePath) {
  return filePath
    .split(path.sep)
    .map((segment) => segment.toLowerCase())
    .some((segment) => FORBIDDEN_SEGMENTS.has(segment));
}

function hasForbiddenExtension(filePath) {
  return FORBIDDEN_FILE_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function isTextFile(filePath) {
  return TEXT_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function isMarkdownFile(filePath) {
  return MARKDOWN_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function isInsideRoot(child, root) {
  const relative = path.relative(root, child);
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
}

function isAllowedRealPath(realPath) {
  return ALLOWED_ROOTS.some((root) => isInsideRoot(realPath, root));
}

function idFor(item) {
  return crypto
    .createHash('sha1')
    .update(`${item.section}\0${item.platform}\0${item.sourcePath}`)
    .digest('hex')
    .slice(0, 20);
}

function languageFor(filePath) {
  const extension = path.extname(filePath).toLowerCase();
  const map = {
    '.cjs': 'javascript',
    '.js': 'javascript',
    '.json': 'json',
    '.mjs': 'javascript',
    '.py': 'python',
    '.sh': 'bash',
    '.toml': 'toml',
    '.yaml': 'yaml',
    '.yml': 'yaml'
  };
  return map[extension] ?? 'text';
}

function fenceFor(content) {
  const longestRun = Math.max(2, ...[...content.matchAll(/`+/g)].map((match) => match[0].length));
  return '`'.repeat(longestRun + 1);
}

function titleFor(source, filePath) {
  if (source.root) {
    return path.relative(source.root, filePath).split(path.sep).join('/');
  }

  return path.basename(filePath);
}

async function fileExists(filePath) {
  try {
    const stat = await fs.stat(filePath);
    return stat.isFile();
  } catch {
    return false;
  }
}

async function makeItem(source, filePath) {
  const absolutePath = path.resolve(filePath);

  if (!isTextFile(absolutePath) || hasForbiddenSegment(absolutePath) || hasForbiddenExtension(absolutePath)) {
    return null;
  }

  const realPath = await fs.realpath(absolutePath);
  if (!isAllowedRealPath(realPath) || hasForbiddenSegment(realPath) || hasForbiddenExtension(realPath)) {
    return null;
  }

  const item = {
    id: '',
    section: source.section,
    platform: source.platform,
    title: titleFor(source, absolutePath),
    sourcePath: absolutePath,
    realPath,
    extension: path.extname(absolutePath).toLowerCase(),
    markdown: isMarkdownFile(absolutePath)
  };

  item.id = idFor(item);
  return item;
}

async function collectFromRoot(source) {
  if (!(await fileExists(source.root).catch(() => false))) {
    try {
      const stat = await fs.stat(source.root);
      if (!stat.isDirectory()) {
        return [];
      }
    } catch {
      return [];
    }
  }

  const entries = await fg(source.pattern, {
    cwd: source.root,
    absolute: true,
    dot: true,
    onlyFiles: true,
    followSymbolicLinks: true,
    suppressErrors: true
  });

  const items = [];
  for (const entry of entries.sort()) {
    try {
      const item = await makeItem(source, entry);
      if (item) {
        items.push(item);
      }
    } catch {
      // Ignore unreadable or broken symlink entries.
    }
  }

  return items;
}

async function collectFromFiles(source) {
  const items = [];
  for (const filePath of source.files) {
    try {
      if (!(await fileExists(filePath))) {
        continue;
      }

      const item = await makeItem(source, filePath);
      if (item) {
        items.push(item);
      }
    } catch {
      // Ignore missing or unreadable optional files.
    }
  }

  return items;
}

async function buildCatalog() {
  const allItems = [];

  for (const source of SOURCES) {
    const items = source.root ? await collectFromRoot(source) : await collectFromFiles(source);
    allItems.push(...items);
  }

  const unique = new Map();
  for (const item of allItems) {
    unique.set(item.id, item);
  }

  return [...unique.values()].sort((a, b) => {
    return (
      orderIndex(SECTION_ORDER, a.section) - orderIndex(SECTION_ORDER, b.section) ||
      orderIndex(PLATFORM_ORDER, a.platform) - orderIndex(PLATFORM_ORDER, b.platform) ||
      a.title.localeCompare(b.title)
    );
  });
}

function orderIndex(order, value) {
  const index = order.indexOf(value);
  return index === -1 ? order.length : index;
}

function groupCatalog(catalog) {
  const grouped = new Map();
  for (const item of catalog) {
    if (!grouped.has(item.section)) {
      grouped.set(item.section, new Map());
    }
    const section = grouped.get(item.section);
    if (!section.has(item.platform)) {
      section.set(item.platform, []);
    }
    section.get(item.platform).push(item);
  }
  return grouped;
}

function markdownLabel(label) {
  return label.replaceAll('[', '\\[').replaceAll(']', '\\]');
}

function treeNode() {
  return {
    children: new Map(),
    item: null
  };
}

function buildTree(items) {
  const root = treeNode();

  for (const item of items) {
    const parts = item.title.split('/').filter(Boolean);
    let current = root;

    for (const part of parts.slice(0, -1)) {
      if (!current.children.has(part)) {
        current.children.set(part, treeNode());
      }
      current = current.children.get(part);
    }

    const fileName = parts.at(-1) ?? item.title;
    if (!current.children.has(fileName)) {
      current.children.set(fileName, treeNode());
    }
    current.children.get(fileName).item = item;
  }

  return root;
}

function sortTreeEntries(entries) {
  return entries.sort(([nameA, nodeA], [nameB, nodeB]) => {
    const nodeAIsFolder = nodeA.children.size > 0;
    const nodeBIsFolder = nodeB.children.size > 0;
    const nodeAIsSkill = nameA === 'SKILL.md';
    const nodeBIsSkill = nameB === 'SKILL.md';

    if (nodeAIsSkill !== nodeBIsSkill) {
      return nodeAIsSkill ? -1 : 1;
    }
    if (nodeAIsFolder !== nodeBIsFolder) {
      return nodeAIsFolder ? 1 : -1;
    }
    return nameA.localeCompare(nameB);
  });
}

function renderTreeLines(node, depth) {
  const lines = [];
  const indent = '  '.repeat(depth);
  const entries = sortTreeEntries([...node.children.entries()]);

  for (const [name, child] of entries) {
    const label = markdownLabel(name);
    if (child.children.size > 0) {
      lines.push(`${indent}- ${label}`);
      lines.push(...renderTreeLines(child, depth + 1));
    } else if (child.item) {
      lines.push(`${indent}- [${label}](/docs/${child.item.id}.md)`);
    }
  }

  return lines;
}

async function renderSidebar(catalog) {
  catalog ??= await buildCatalog();
  const grouped = groupCatalog(catalog);
  const lines = ['- [Home](/)', ''];

  for (const [sectionName, platforms] of grouped) {
    lines.push(`- ${sectionName}`);
    for (const [platformName, items] of platforms) {
      lines.push(`  - ${platformName}`);
      lines.push(...renderTreeLines(buildTree(items), 2));
    }
  }

  return `${lines.join('\n')}\n`;
}

function assertSidebarShape(sidebar, catalog) {
  const catalogIds = new Set(catalog.map((item) => item.id));
  const links = [...sidebar.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)].map((match) => match[1]);
  const invalidLinks = links.filter((link) => link !== '/' && !/^\/docs\/[a-f0-9]{20}\.md$/.test(link));
  const linkedDocIds = links
    .map((link) => link.match(/^\/docs\/([a-f0-9]{20})\.md$/)?.[1])
    .filter(Boolean);
  const linkedDocIdSet = new Set(linkedDocIds);
  const unknownDocIds = linkedDocIds.filter((id) => !catalogIds.has(id));
  const missingLinkedItems = catalog.filter((item) => !linkedDocIdSet.has(item.id));

  if (invalidLinks.length > 0) {
    throw new Error(`Sidebar contains non-whitelisted links: ${invalidLinks.join(', ')}`);
  }

  if (unknownDocIds.length > 0) {
    throw new Error(`Sidebar links unknown document ids: ${unknownDocIds.join(', ')}`);
  }

  if (missingLinkedItems.length > 0) {
    throw new Error(`Sidebar misses catalog items: ${missingLinkedItems.map((item) => item.title).join(', ')}`);
  }

  const sampleSkill =
    catalog.find((item) => item.section === 'Skills' && item.platform === 'Codex' && item.title === '1start-here/SKILL.md') ??
    catalog.find((item) => item.section === 'Skills' && item.platform === 'Codex' && item.title.endsWith('/SKILL.md'));

  if (!sampleSkill) {
    throw new Error('Sidebar shape check needs at least one Codex SKILL.md item.');
  }

  const parts = sampleSkill.title.split('/');
  const expectedLines = parts.slice(0, -1).map((part, index) => {
    return `${'  '.repeat(2 + index)}- ${markdownLabel(part)}`;
  });
  expectedLines.push(`${'  '.repeat(2 + parts.length - 1)}- [${markdownLabel(parts.at(-1))}](/docs/${sampleSkill.id}.md)`);

  const missingNestedLines = expectedLines.filter((line) => !sidebar.includes(line));
  if (missingNestedLines.length > 0) {
    throw new Error(`Sidebar is not nested for ${sampleSkill.title}: ${missingNestedLines.join(' | ')}`);
  }

  const flatSkillPaths = catalog
    .filter((item) => item.section === 'Skills' && item.title.includes('/'))
    .filter((item) => sidebar.includes(item.title))
    .map((item) => item.title);

  if (flatSkillPaths.length > 0) {
    throw new Error(`Sidebar leaked flat skill paths: ${flatSkillPaths.slice(0, 10).join(', ')}`);
  }
}

async function renderHome() {
  const catalog = await buildCatalog();
  const grouped = groupCatalog(catalog);
  const lines = [
    '# Global Agent Surface Viewer',
    '',
    'Read-only live viewer for global Codex and Claude agent surfaces.',
    '',
    'Use the sidebar to open skills, global instructions, hooks, agents, and runtime config files.',
    '',
    'The server reads files on request from the allowlist and does not copy their contents into this repo.',
    '',
    '## Catalog',
    ''
  ];

  for (const [sectionName, platforms] of grouped) {
    const count = [...platforms.values()].reduce((sum, items) => sum + items.length, 0);
    lines.push(`- **${sectionName}**: ${count}`);
  }

  lines.push('');
  lines.push(`Generated at ${new Date().toISOString()}.`);
  lines.push('');
  return `${lines.join('\n')}\n`;
}

async function getItemById(id) {
  const catalog = await buildCatalog();
  return catalog.find((item) => item.id === id) ?? null;
}

function sourceNote(item) {
  return [
    `> Source: \`${item.sourcePath}\``,
    `> Platform: \`${item.platform}\` · Section: \`${item.section}\` · [Raw](/raw/${item.id})`,
    ''
  ].join('\n');
}

function renderMarkdownBody(content) {
  const frontmatterMatch = content.match(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/);
  if (!frontmatterMatch) {
    return content;
  }

  const frontmatter = frontmatterMatch[0].trimEnd();
  const body = content.slice(frontmatterMatch[0].length).replace(/^\r?\n/, '');
  const fence = fenceFor(frontmatter);

  return [`${fence}yaml`, frontmatter, fence, '', body].join('\n');
}

async function renderDocument(item) {
  const content = await fs.readFile(item.realPath, 'utf8');

  if (item.markdown) {
    return [`# ${item.title}`, '', sourceNote(item), '---', '', renderMarkdownBody(content)].join('\n');
  }

  const fence = fenceFor(content);
  const language = languageFor(item.sourcePath);
  return [
    `# ${item.title}`,
    '',
    sourceNote(item),
    `${fence}${language}`,
    content,
    fence,
    ''
  ].join('\n');
}

async function runCheck() {
  const catalog = await buildCatalog();
  const bySection = groupCatalog(catalog);
  const missing = [];

  for (const section of ['Skills', 'Global Instructions', 'Hooks', 'Agents', 'Runtime Config']) {
    if (!bySection.has(section)) {
      missing.push(section);
    }
  }

  const forbidden = catalog.filter((item) => {
    return (
      hasForbiddenSegment(item.sourcePath) ||
      hasForbiddenSegment(item.realPath) ||
      hasForbiddenExtension(item.sourcePath) ||
      hasForbiddenExtension(item.realPath) ||
      !isAllowedRealPath(item.realPath)
    );
  });

  console.log(`Catalog items: ${catalog.length}`);
  for (const [sectionName, platforms] of bySection) {
    const count = [...platforms.values()].reduce((sum, items) => sum + items.length, 0);
    console.log(`- ${sectionName}: ${count}`);
  }

  if (missing.length > 0) {
    throw new Error(`Missing expected sections: ${missing.join(', ')}`);
  }

  if (forbidden.length > 0) {
    throw new Error(`Forbidden items leaked into catalog: ${forbidden.map((item) => item.sourcePath).join(', ')}`);
  }

  assertSidebarShape(await renderSidebar(catalog), catalog);

  console.log('Sidebar tree: OK');
  console.log('Check passed.');
}

function createApp() {
  const app = express();

  app.disable('x-powered-by');
  app.use((request, response, next) => {
    if (
      request.path === '/_sidebar.md' ||
      request.path === '/README.md' ||
      request.path.startsWith('/api/') ||
      request.path.startsWith('/docs/') ||
      request.path.startsWith('/raw/')
    ) {
      response.set('Cache-Control', 'no-store, max-age=0');
    }
    next();
  });
  app.get('/favicon.ico', (_request, response) => {
    response.status(204).end();
  });
  app.get('/theme.css', async (_request, response, next) => {
    try {
      const themePath = path.join(DOCSIFY_ROOT, 'themes', 'vue.css');
      const css = await fs.readFile(themePath, 'utf8');
      response.type('text/css').send(css.replace(/^@import\s+url\([^)]+\);\s*/m, ''));
    } catch (error) {
      next(error);
    }
  });
  app.use('/vendor/docsify', express.static(DOCSIFY_ROOT, { fallthrough: false }));
  app.use('/vendor/prism', express.static(PRISM_ROOT, { fallthrough: false }));
  app.use('/vendor/sidebar-collapse', express.static(SIDEBAR_COLLAPSE_ROOT, { fallthrough: false }));
  app.use(express.static(path.join(__dirname, 'public'), { index: 'index.html' }));

  app.get('/api/catalog', async (_request, response, next) => {
    try {
      const catalog = await buildCatalog();
      response.json(
        catalog.map(({ id, section, platform, title, extension, markdown, sourcePath }) => ({
          id,
          section,
          platform,
          title,
          extension,
          markdown,
          sourcePath
        }))
      );
    } catch (error) {
      next(error);
    }
  });

  app.get('/_sidebar.md', async (_request, response, next) => {
    try {
      response.type('text/markdown').send(await renderSidebar());
    } catch (error) {
      next(error);
    }
  });

  app.get('/README.md', async (_request, response, next) => {
    try {
      response.type('text/markdown').send(await renderHome());
    } catch (error) {
      next(error);
    }
  });

  app.get('/docs/:id.md', async (request, response, next) => {
    try {
      const item = await getItemById(request.params.id);
      if (!item) {
        response.status(404).type('text/markdown').send('# Not found\n');
        return;
      }

      response.type('text/markdown').send(await renderDocument(item));
    } catch (error) {
      next(error);
    }
  });

  app.get('/raw/:id', async (request, response, next) => {
    try {
      const item = await getItemById(request.params.id);
      if (!item) {
        response.status(404).type('text/plain').send('Not found\n');
        return;
      }

      response.type('text/plain').send(await fs.readFile(item.realPath, 'utf8'));
    } catch (error) {
      next(error);
    }
  });

  return app;
}

const args = parseArgs(process.argv);

if (args.check) {
  await runCheck();
} else {
  const app = createApp();
  app.listen(args.port, HOST, () => {
    console.log(`Global Agent Surface Viewer: http://${HOST}:${args.port}`);
  });
}
