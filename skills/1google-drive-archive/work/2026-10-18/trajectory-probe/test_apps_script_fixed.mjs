import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const source = readFileSync("/Users/triton/Documents/GitHub/agentic-research/skills/1google-drive-archive/versions/candidate-2026-10-18/assets/apps-script/Code.gs", 'utf8');
const secret = 'SYNTHETIC_SECRET_DO_NOT_LOG';
const sha = 'a'.repeat(64), md5 = 'b'.repeat(32);
const target = (index = 0) => ({index, name: secret, size: '12', sha256: sha, md5});
const file = (id = 'file_1', extra = {}) => ({id, name: secret, description: secret,
  mimeType: 'application/zip', size: '12', sha256Checksum: sha, md5Checksum: md5,
  trashed: false, version: '42', ownedByMe: true, capabilities: {canDownload: true}, ...extra});
const page = (files = [], nextPageToken) => ({files, incompleteSearch: false,
  ...(nextPageToken === undefined ? {} : {nextPageToken})});

function harness(pages = [page([file()])]) {
  const data = new Map(), logs = [], requests = [];
  let account = 'permission_123', calls = 0, locked = false, writeFail = false, failAfterWrite = false;
  let clock = Date.parse('2026-10-18T12:00:00.000Z');
  class FakeDate extends Date {
    constructor(...args) { super(...(args.length ? args : [clock])); }
    static now() { return clock; }
  }
  const properties = {
    getProperty: key => data.get(key) ?? null,
    setProperty(key, value) {
      if (writeFail) throw new Error(secret);
      data.set(key, value);
      if (failAfterWrite) throw new Error(secret);
    },
  };
  const context = vm.createContext({console: {log: s => logs.push(s)}, Date: FakeDate, Set, Map,
    Drive: {
      About: {get(params) { assert.equal(params.fields, 'user(permissionId)'); return {user: {permissionId: account, emailAddress: secret}}; }},
      Files: {
        get(id, params) { requests.push({method: 'get', id, params}); return context.rawFile ?? file(id); },
        list(params) {
          requests.push({method: 'list', params: JSON.parse(JSON.stringify(params))});
          const entry = pages[calls++];
          if (entry instanceof Error) throw entry;
          if (!entry) throw new Error(secret);
          return entry;
        },
      },
    },
    PropertiesService: {getScriptProperties: () => properties},
    LockService: {getScriptLock: () => ({tryLock: () => { if (locked) return false; locked = true; return true; }, releaseLock: () => {locked = false;}})},
    Utilities: {
      DigestAlgorithm: {SHA_256: 'sha256'}, Charset: {UTF_8: 'utf8'},
      computeDigest: (_, s) => [...createHash('sha256').update(s).digest()].map(b => b > 127 ? b - 256 : b),
      newBlob: s => ({getBytes: () => [...Buffer.from(s)]}),
    },
  });
  vm.runInContext(source, context);
  context.TARGETS = [target()]; context.RUN_ID = 'run_1';
  return {context, data, logs, requests, setAccount: a => {account = a;},
    setClock: value => { clock = Date.parse(value); },
    setWriteFail: b => {writeFail = b;}, setFailAfterWrite: b => {failAfterWrite = b;},
    scan: () => JSON.parse(JSON.stringify(context.continueArchiveScan())),
    snapshot: () => JSON.parse(JSON.stringify(context.metadataSnapshot())),
    state: () => JSON.parse([...data.values()][0]),
    assertSafe() { assert.ok(!logs.join('\n').includes(secret)); assert.ok(!logs.join('\n').includes('nextPageToken')); },
  };
}

test('safe empty config rejects before Drive calls', () => {
  const h = harness(); h.context.TARGETS = []; h.context.RUN_ID = '';
  assert.equal(h.scan().code, 'INVALID_CONFIG');
  assert.equal(h.snapshot().code, 'INVALID_CONFIG');
  assert.equal(h.requests.length, 0); assert.equal(h.data.size, 0);
});
test('snapshot exact schema, decimal strings, null optionals; no names or secrets', () => {
  const h = harness(); h.context.FILE_IDS = ['file_1'];
  h.context.rawFile = file('file_1', {version: undefined, md5Checksum: undefined,
    capabilities: undefined, ownedByMe: undefined, size: '9007199254740993'});
  const row = h.snapshot()[0];
  assert.deepEqual(Object.keys(row).sort(), ['schemaVersion','checkedAt','accountKey','fileId','size',
    'sha256Checksum','md5Checksum','version','trashed','binaryFile','canDownload','ownedByMe'].sort());
  assert.equal(row.size, '9007199254740993'); assert.equal(row.version, null);
  assert.equal(row.md5Checksum, null); assert.equal(row.canDownload, null); assert.equal(row.ownedByMe, null);
  assert.equal(row.accountKey, 'permission_123'); assert.equal(row.binaryFile, true);
  assert.match(row.checkedAt, /^\d{4}-/);
  assert.equal(h.requests[0].params.supportsAllDrives, true);
  assert.ok(!h.requests[0].params.fields.includes('name')); h.assertSafe();
});
test('snapshot wrong ID / missing fields / malformed optional fail without rows', () => {
  for (const [raw, code] of [[file('wrong'), 'WRONG_FILE_ID'], [file('file_1', {size: undefined}), 'MISSING_FIELDS'],
    [file('file_1', {sha256Checksum: secret}), 'INVALID_METADATA']]) {
    const h = harness(); h.context.FILE_IDS = ['file_1']; h.context.rawFile = raw;
    assert.equal(h.snapshot().code, code); assert.equal(h.logs.length, 1); h.assertSafe();
  }
});
test('full pagination incl empty advancing page and private tokens', () => {
  const h = harness([page([file()], 'private_token_' + secret), page([], 'end_token'), page([file('file_2')])]);
  const r = h.scan(); assert.equal(r.status, 'SCAN_COMPLETE'); assert.equal(r.freshInventory, true);
  assert.equal(r.pages, 3); assert.equal(r.files, 2); assert.equal(r.candidateCount, 2);
  assert.deepEqual(r.candidates[0], {index: 0, id: 'file_1', matchkind: 'SHA256_CANDIDATE'});
  assert.equal(h.requests[0].params.corpora, 'user'); assert.equal(h.requests[0].params.spaces, 'drive');
  assert.equal(h.requests[1].params.pageToken, 'private_token_' + secret); h.assertSafe();
});
test('20-page bound resumes >=200 pages without fingerprint quota exhaustion', () => {
  const pages = Array.from({length: 201}, (_, i) => page([file('id_' + i, {sha256Checksum: 'c'.repeat(64)})], i === 200 ? undefined : 'tok_' + i));
  const h = harness(pages);
  let r = h.scan(); assert.equal(r.status, 'SCAN_PAUSED'); assert.equal(r.pages, 20);
  for (let i = 0; i < 10; i++) r = h.scan();
  assert.equal(r.status, 'SCAN_COMPLETE'); assert.equal(r.pages, 201); assert.equal(r.files, 201);
  assert.ok(Buffer.byteLength([...h.data.values()][0]) < 8000); h.assertSafe();
});
test('finished same RUN_ID is not fresh; new unique RUN_ID starts new inventory', () => {
  const h = harness([page([file()]), page([file('next')])]);
  assert.equal(h.scan().status, 'SCAN_COMPLETE');
  const r = h.scan(); assert.equal(r.status, 'SCAN_ALREADY_COMPLETE'); assert.equal(r.freshInventory, false);
  assert.equal(h.requests.length, 1);
  h.context.RUN_ID = 'run_2'; assert.equal(h.scan().status, 'SCAN_COMPLETE');
  assert.equal(h.data.size, 2); assert.equal(h.requests[1].params.pageToken, undefined);
});
test('config/account change rejects same RUN_ID; new RUN_ID can bind new config', () => {
  const h = harness([page([file()]), page([])]); h.scan();
  h.context.TARGETS = [target(4)]; assert.equal(h.scan().code, 'CONFIG_CHANGED');
  h.context.TARGETS = [target()]; h.setAccount('permission_other'); assert.equal(h.scan().code, 'ACCOUNT_CHANGED');
  h.context.RUN_ID = 'run_new'; h.context.TARGETS = [target(4)]; assert.equal(h.scan().complete, true);
});
test('API error resumes exact failed page; error never logged', () => {
  const h = harness([page([file()], 'private_token_' + secret), new Error(secret), page([file('file_2')])]);
  const r = h.scan(); assert.equal(r.code, 'API_FAILED'); assert.equal(r.complete, false); assert.equal(r.pages, 1);
  assert.equal(h.scan().status, 'SCAN_COMPLETE');
  assert.equal(h.requests[1].params.pageToken, h.requests[2].params.pageToken); h.assertSafe();
});
test('cycle token halts fail closed and does not commit offending page', () => {
  const h = harness([page([file()], 'a'), page([], 'b'), page([file('file_2')], 'a')]);
  const r = h.scan(); assert.equal(r.code, 'REPEATED_PAGE_TOKEN'); assert.equal(r.complete, false);
  assert.equal(r.pages, 2); assert.equal(r.files, 1); assert.equal(r.candidateCount, 1);
  assert.equal(h.scan().status, 'SCAN_HALTED'); assert.equal(h.requests.length, 3); h.assertSafe();
});
test('incomplete search halts without committing page; duplicate page rows fail closed', () => {
  for (const [response, reason] of [[{...page([file()]), incompleteSearch: true}, 'INCOMPLETE_SEARCH'],
    [page([file(), file()]), 'DUPLICATE_FILE'], [{files: []}, 'MISSING_FIELDS']]) {
    const h = harness([response]); const r = h.scan(); assert.equal(r.code, reason);
    assert.equal(r.complete, false); assert.equal(r.files, 0); assert.equal(r.candidateCount, 0);
  }
});
test('candidate pair duplicates across pages are deduplicated', () => {
  const h = harness([page([file()], 'a'), page([file()])]);
  const r = h.scan(); assert.equal(r.complete, true); assert.equal(r.candidateCount, 1);
});
test('MD5/name-size are candidates only; SHA256 mismatch never downgraded', () => {
  const h = harness([page([file('md5_only', {sha256Checksum: undefined}),
    file('name_size', {sha256Checksum: undefined, md5Checksum: undefined}),
    file('mismatch', {sha256Checksum: 'c'.repeat(64)})])]);
  const r = h.scan(); assert.deepEqual(r.candidates, [
    {index: 0, id: 'md5_only', matchkind: 'MD5_CANDIDATE'},
    {index: 0, id: 'name_size', matchkind: 'NAME_SIZE_CANDIDATE'}]); h.assertSafe();
});
test('zero bytes and Google-native files are never backup candidates', () => {
  const h = harness([page([file('zero', {size: '0'}), file('native', {mimeType: 'application/vnd.google-apps.document', size: undefined})])]);
  h.context.TARGETS = [{...target(), size: '0'}];
  const r = h.scan(); assert.equal(r.complete, true); assert.equal(r.files, 2); assert.equal(r.candidateCount, 0);
});
test('candidate overflow never loses page while claiming complete', () => {
  const h = harness([page([file()], 'next'), page(Array.from({length: 32}, (_, i) => file('more_' + i)))]);
  const r = h.scan(); assert.equal(r.code, 'CANDIDATE_LIMIT'); assert.equal(r.complete, false);
  assert.equal(r.pages, 1); assert.equal(r.files, 1); assert.equal(r.candidateCount, 1);
  assert.equal(h.state().nextToken, 'next'); assert.equal(h.state().halt, 'CANDIDATE_LIMIT');
});
test('state size quota stops incomplete; property write failure does not commit page', () => {
  const h = harness([new Error(secret), page([file()], 'next')]); h.scan();
  h.context.LIMITS_.stateBytes = Buffer.byteLength([...h.data.values()][0]) + 10;
  assert.equal(h.scan().code, 'STATE_LIMIT'); assert.equal(h.state().complete, false);
  assert.equal(h.state().pages, 0); assert.equal(h.state().candidates.length, 0);
  const h2 = harness(); h2.setWriteFail(true);
  assert.equal(h2.scan().code, 'STATE_WRITE_FAILED'); assert.equal(h2.requests.length, 0); h2.assertSafe();
});
test('scan manifest binds account/run/config/scope and preserves old resumed timestamps', () => {
  const h = harness([page([], 'next'), new Error(secret), page([file()])]);
  const first = h.scan(); assert.equal(first.status, 'SCAN_INCOMPLETE');
  assert.equal(first.accountKey, 'permission_123'); assert.equal(first.runId, 'run_1');
  assert.match(first.configDigest, /^[0-9a-f]{64}$/);
  assert.deepEqual(first.scope, {corpora: 'user', spaces: 'drive', driveId: null, trashed: false, excludeFolders: true});
  assert.equal(first.startedAt, '2026-10-18T12:00:00.000Z');
  assert.equal(first.lastPageCheckedAt, first.startedAt); assert.equal(first.completedAt, null);
  h.setClock('2026-10-19T12:00:00.000Z');
  const final = h.scan(); assert.equal(final.status, 'SCAN_COMPLETE'); assert.equal(final.freshInventory, false);
  assert.equal(final.startedAt, first.startedAt); assert.equal(final.lastPageCheckedAt, '2026-10-19T12:00:00.000Z');
  assert.equal(final.completedAt, final.lastPageCheckedAt); assert.equal(final.configDigest, first.configDigest);
  const again = h.scan(); assert.equal(again.freshInventory, false); assert.equal(again.completedAt, final.completedAt);
  h.assertSafe();
});
test('persisted manifest identity/timestamps reject corruption without reflecting values', () => {
  for (const [field, value] of [['startedAt', secret], ['lastPageCheckedAt', '2026-10-17T12:00:00.000Z'],
    ['completedAt', null], ['runId', 'wrong_run'], ['scope', {corpora: secret}]]) {
    const h = harness(); h.scan();
    const [key, raw] = [...h.data][0]; const s = JSON.parse(raw); s[field] = value; h.data.set(key, JSON.stringify(s));
    const r = h.scan(); assert.equal(r.status, 'SCAN_INCOMPLETE'); assert.equal(r.complete, false);
    assert.equal(r.accountKey, null); assert.equal(r.startedAt, null); h.assertSafe();
  }
});
test('emitted snapshot JSON passes sibling Python valid_remote schema without hashing', () => {
  const h = harness(); h.context.FILE_IDS = ['file_1']; const row = h.snapshot()[0];
  const validator = process.env.ARCHIVE_VERIFY_PY ?? "/Users/triton/Documents/GitHub/agentic-research/skills/1google-drive-archive/versions/candidate-2026-10-18/scripts/archive_verify.py";
  const script = 'import importlib.util,json,sys\nspec=importlib.util.spec_from_file_location("archive_verify",sys.argv[1])\nm=importlib.util.module_from_spec(spec)\nspec.loader.exec_module(m)\nassert m.valid_remote(json.load(sys.stdin))\n';
  const result = spawnSync('python3', ['-B', '-c', script, validator], {input: JSON.stringify(row), encoding: 'utf8'});
  assert.equal(result.status, 0, 'Python schema rejected the emitted synthetic snapshot');
  assert.equal(result.stdout, ''); assert.equal(result.stderr, ''); h.assertSafe();
});
test('setter uncertain success is checked by read-back', () => {
  const h = harness(); h.setFailAfterWrite(true);
  assert.equal(h.scan().status, 'SCAN_COMPLETE'); assert.equal(h.state().complete, true); h.assertSafe();
});
test('specific shared drive uses drive corpus and exact ID', () => {
  const h = harness(); h.context.DRIVE_ID = 'shared_drive_1'; h.scan();
  assert.equal(h.requests[0].params.corpora, 'drive'); assert.equal(h.requests[0].params.driveId, 'shared_drive_1');
});
test('manifest contains only metadata-readonly scope, V8, Drive v3, no exception logging', () => {
  const manifest = JSON.parse(readFileSync("/Users/triton/Documents/GitHub/agentic-research/skills/1google-drive-archive/versions/candidate-2026-10-18/assets/apps-script/appsscript.json", 'utf8'));
  assert.deepEqual(manifest.oauthScopes, ['https://www.googleapis.com/auth/drive.metadata.readonly']);
  assert.equal(manifest.exceptionLogging, 'NONE'); assert.equal(manifest.runtimeVersion, 'V8');
  assert.deepEqual(manifest.dependencies.enabledAdvancedServices, [{userSymbol: 'Drive', version: 'v3', serviceId: 'drive'}]);
  assert.ok(!/getOAuthToken|UrlFetchApp|DriveApp|\.remove\(|\.delete\(|\.create\(|\.update\(/.test(source));
});
