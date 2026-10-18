// Fill these locally in a private, owner-only Apps Script project. Empty = no Drive calls.
var FILE_IDS = [];
var TARGETS = []; // [{index: 0, name: 'archive.zip', size: '123', sha256: '64 hex', md5: null}]
var RUN_ID = ''; // New unique value for EVERY new inventory; retain it only to resume.
var DRIVE_ID = ''; // Optional shared-drive ID; otherwise corpora=user.

var LIMITS_ = {pages: 20, milliseconds: 150000, candidates: 32, stateBytes: 8000};
var SNAP_FIELDS_ = 'id,size,sha256Checksum,md5Checksum,version,trashed,mimeType,capabilities(canDownload),ownedByMe';
var LIST_FIELDS_ = 'nextPageToken,incompleteSearch,files(id,name,size,sha256Checksum,md5Checksum,mimeType,trashed)';

function emit_(value) { console.log(JSON.stringify(value)); return value; }
function fail_(code) { var e = new Error('Metadata helper stopped'); e.safeCode = code; throw e; }
function code_(error) {
  var allowed = ['INVALID_CONFIG','MISSING_FIELDS','WRONG_FILE_ID','INVALID_METADATA','ACCOUNT_UNAVAILABLE',
    'ACCOUNT_CHANGED','CONFIG_CHANGED','STATE_INVALID','STATE_LIMIT','STATE_WRITE_FAILED','REPEATED_PAGE_TOKEN',
    'DUPLICATE_FILE','INCOMPLETE_SEARCH','CANDIDATE_LIMIT','LOCK_BUSY','API_FAILED'];
  return error && allowed.indexOf(error.safeCode) >= 0 ? error.safeCode : 'API_FAILED';
}
function id_(s) { return typeof s === 'string' && /^[A-Za-z0-9_-]{1,200}$/.test(s); }
function decimal_(s) { return typeof s === 'string' && /^(0|[1-9][0-9]{0,24})$/.test(s); }
function time_(s) {
  return typeof s === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(s) &&
    !isNaN(Date.parse(s)) && new Date(s).toISOString() === s;
}
function hash_(s) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, s, Utilities.Charset.UTF_8)
    .map(function(b) { return ('0' + ((b + 256) % 256).toString(16)).slice(-2); }).join('');
}
function checksum_(s, length) {
  if (s === undefined || s === null) return null;
  if (typeof s !== 'string' || !(new RegExp('^[a-fA-F0-9]{' + length + '}$')).test(s)) fail_('INVALID_METADATA');
  return s.toLowerCase();
}
function bool_(s) {
  if (s === undefined || s === null) return null;
  if (typeof s !== 'boolean') fail_('INVALID_METADATA');
  return s;
}
function account_() {
  var a = Drive.About.get({fields: 'user(permissionId)'});
  if (!a || !a.user || !id_(a.user.permissionId)) fail_('ACCOUNT_UNAVAILABLE');
  return a.user.permissionId;
}
function file_(f, needName) {
  if (!f || !id_(f.id) || typeof f.mimeType !== 'string' || !f.mimeType) fail_('MISSING_FIELDS');
  var binary = f.mimeType.indexOf('application/vnd.google-apps.') !== 0;
  if (needName && typeof f.name !== 'string') fail_('MISSING_FIELDS');
  if (f.size !== undefined && !decimal_(f.size)) fail_('INVALID_METADATA');
  if (binary && f.size === undefined) fail_('MISSING_FIELDS');
  return {id: f.id, name: needName ? f.name : null, size: f.size === undefined ? null : f.size,
    sha256: checksum_(f.sha256Checksum, 64), md5: checksum_(f.md5Checksum, 32), binary: binary,
    trashed: bool_(f.trashed)};
}

// All rows are validated before anything is emitted. Save JSON lines around a fresh local hash.
function metadataSnapshot() {
  try {
    if (!Array.isArray(FILE_IDS) || !FILE_IDS.length || FILE_IDS.length > 32 ||
        FILE_IDS.some(function(id) { return !id_(id); }) || new Set(FILE_IDS).size !== FILE_IDS.length) fail_('INVALID_CONFIG');
    var account = account_();
    var rows = FILE_IDS.map(function(id) {
      var raw = Drive.Files.get(id, {fields: SNAP_FIELDS_, supportsAllDrives: true});
      if (!raw || raw.id !== id) fail_('WRONG_FILE_ID');
      var f = file_(raw, false);
      if (f.size === null) fail_('MISSING_FIELDS');
      if (raw.version !== undefined && raw.version !== null && !decimal_(raw.version)) fail_('INVALID_METADATA');
      return {schemaVersion: 1, checkedAt: new Date().toISOString(), accountKey: account, fileId: id,
        size: f.size, sha256Checksum: f.sha256, md5Checksum: f.md5,
        version: raw.version === undefined ? null : raw.version, trashed: f.trashed, binaryFile: f.binary,
        canDownload: bool_(raw.capabilities && raw.capabilities.canDownload), ownedByMe: bool_(raw.ownedByMe)};
    });
    rows.forEach(emit_);
    return rows;
  } catch (error) { return emit_({schemaVersion: 1, status: 'SNAPSHOT_FAILED', code: code_(error)}); }
}

function scanConfig_() {
  if (typeof RUN_ID !== 'string' || !/^[A-Za-z0-9_-]{1,100}$/.test(RUN_ID) ||
      typeof DRIVE_ID !== 'string' || (DRIVE_ID && !id_(DRIVE_ID)) ||
      !Array.isArray(TARGETS) || !TARGETS.length || TARGETS.length > 32) fail_('INVALID_CONFIG');
  var indices = {};
  var targets = TARGETS.map(function(t) {
    if (!t || !Number.isSafeInteger(t.index) || t.index < 0 || indices[t.index] ||
        typeof t.name !== 'string' || !t.name || t.name.length > 1024 || !decimal_(t.size) ||
        (t.sha256 === null || t.sha256 === undefined) && (t.md5 === null || t.md5 === undefined)) fail_('INVALID_CONFIG');
    indices[t.index] = true;
    var normalized;
    try { normalized = {index: t.index, name: t.name, size: t.size,
      sha256: checksum_(t.sha256, 64), md5: checksum_(t.md5, 32)}; }
    catch (error) { fail_('INVALID_CONFIG'); }
    return normalized;
  });
  var scope = {corpora: DRIVE_ID ? 'drive' : 'user', spaces: 'drive', driveId: DRIVE_ID || null,
    trashed: false, excludeFolders: true};
  return {targets: targets, scope: scope, digest: hash_(JSON.stringify({schema: 1, targets: targets, scope: scope}))};
}
function result_(state, status, code, fresh) {
  return {schemaVersion: 1, status: status, code: code, complete: !!(state && state.complete),
    accountKey: state ? state.accountKey : null, runId: state ? state.runId : null,
    configDigest: state ? state.configDigest : null,
    scope: state ? {corpora: state.scope.corpora, spaces: 'drive', driveId: state.scope.driveId,
      trashed: false, excludeFolders: true} : null,
    startedAt: state ? state.startedAt : null, lastPageCheckedAt: state ? state.lastPageCheckedAt : null,
    completedAt: state ? state.completedAt : null,
    freshInventory: !!fresh, pages: state ? state.pages : 0, files: state ? state.files : 0,
    candidateCount: state ? state.candidates.length : 0, candidates: state ? state.candidates : []};
}
function save_(properties, key, state) {
  var value = JSON.stringify(state);
  if (Utilities.newBlob(value).getBytes().length > LIMITS_.stateBytes) fail_('STATE_LIMIT');
  try { properties.setProperty(key, value); }
  catch (error) {
    // A setter may fail after committing. Read back before deciding whether progress persisted.
    try { if (properties.getProperty(key) === value) return; } catch (ignored) {}
    fail_('STATE_WRITE_FAILED');
  }
  if (properties.getProperty(key) !== value) fail_('STATE_WRITE_FAILED');
}
function load_(properties, key, account, config) {
  var value = properties.getProperty(key);
  if (!value) return {schemaVersion: 1, accountKey: account, runId: RUN_ID, configDigest: config.digest,
    scope: config.scope, startedAt: new Date().toISOString(), lastPageCheckedAt: null, completedAt: null,
    invocations: 0, complete: false,
    halt: null, pages: 0, files: 0, nextToken: null, tokens: [], candidates: []};
  var s;
  try { s = JSON.parse(value); } catch (error) { fail_('STATE_INVALID'); }
  if (!s || s.schemaVersion !== 1 || !Array.isArray(s.tokens) ||
      !Array.isArray(s.candidates) || s.candidates.length > LIMITS_.candidates ||
      !Number.isSafeInteger(s.pages) || s.pages < 0 || !Number.isSafeInteger(s.files) || s.files < 0 ||
      !Number.isSafeInteger(s.invocations) || s.invocations < 1 ||
      !time_(s.startedAt) || (s.lastPageCheckedAt !== null && !time_(s.lastPageCheckedAt)) ||
      (s.completedAt !== null && !time_(s.completedAt)) ||
      (s.pages === 0 ? s.lastPageCheckedAt !== null : s.lastPageCheckedAt === null) ||
      (s.lastPageCheckedAt !== null && s.lastPageCheckedAt < s.startedAt) ||
      (s.complete ? s.completedAt !== s.lastPageCheckedAt || s.pages === 0 || s.nextToken !== null : s.completedAt !== null) ||
      typeof s.complete !== 'boolean' || (s.nextToken !== null && typeof s.nextToken !== 'string')) fail_('STATE_INVALID');
  if (s.runId !== RUN_ID || !s.scope || JSON.stringify(s.scope) !== JSON.stringify(config.scope)) fail_('CONFIG_CHANGED');
  if (s.accountKey !== account) fail_('ACCOUNT_CHANGED');
  if (s.configDigest !== config.digest) fail_('CONFIG_CHANGED');
  if (s.tokens.some(function(t) { return typeof t !== 'string' || !/^[0-9a-f]{16}$/.test(t); }) ||
      new Set(s.tokens).size !== s.tokens.length || s.tokens.length !== s.pages - (s.complete ? 1 : 0)) fail_('STATE_INVALID');
  // State is private but still never echo arbitrary persisted fields.
  s.candidates.forEach(function(c) {
    if (!c || !Number.isSafeInteger(c.index) || !id_(c.id) ||
        ['SHA256_CANDIDATE','MD5_CANDIDATE','NAME_SIZE_CANDIDATE'].indexOf(c.matchkind) < 0 ||
        Object.keys(c).sort().join(',') !== 'id,index,matchkind') fail_('STATE_INVALID');
  });
  if (s.halt !== null && ['REPEATED_PAGE_TOKEN','DUPLICATE_FILE','INCOMPLETE_SEARCH',
      'CANDIDATE_LIMIT','STATE_LIMIT','MISSING_FIELDS','INVALID_METADATA'].indexOf(s.halt) < 0) fail_('STATE_INVALID');
  return s;
}
function page_(state, response, targets) {
  if (!response || !Array.isArray(response.files) || typeof response.incompleteSearch !== 'boolean') fail_('MISSING_FIELDS');
  if (response.incompleteSearch) fail_('INCOMPLETE_SEARCH');
  var token = response.nextPageToken;
  if (token !== undefined && (typeof token !== 'string' || !token)) fail_('INVALID_METADATA');
  var fingerprint = token === undefined ? null : hash_(token).slice(0, 16);
  if (fingerprint && state.tokens.indexOf(fingerprint) >= 0) fail_('REPEATED_PAGE_TOKEN');
  var files = response.files.map(function(raw) {
    var f = file_(raw, true);
    if (f.trashed !== false || raw.mimeType === 'application/vnd.google-apps.folder') fail_('INVALID_METADATA');
    return f;
  });
  var ids = files.map(function(f) { return f.id; });
  if (new Set(ids).size !== ids.length) fail_('DUPLICATE_FILE');
  var next = JSON.parse(JSON.stringify(state));
  files.forEach(function(f) {
    if (!f.binary || f.size === '0') return; // Zero-byte or native files are never backup candidates.
    targets.forEach(function(t) {
      if (t.size === '0' || t.size !== f.size) return;
      var kind = null;
      if (t.sha256 && f.sha256) {
        if (t.sha256 === f.sha256) kind = 'SHA256_CANDIDATE';
      } else if (t.md5 && f.md5) {
        if (t.md5 === f.md5) kind = 'MD5_CANDIDATE';
      } else if (t.name === f.name) kind = 'NAME_SIZE_CANDIDATE';
      if (kind) {
        if (next.candidates.some(function(c) { return c.index === t.index && c.id === f.id; })) return;
        next.candidates.push({index: t.index, id: f.id, matchkind: kind});
        if (next.candidates.length > LIMITS_.candidates) fail_('CANDIDATE_LIMIT');
      }
    });
  });
  next.pages++; next.files += files.length;
  next.nextToken = token === undefined ? null : token;
  if (fingerprint) next.tokens.push(fingerprint);
  next.complete = token === undefined;
  next.lastPageCheckedAt = new Date().toISOString();
  if (next.lastPageCheckedAt < next.startedAt) fail_('INVALID_METADATA');
  next.completedAt = next.complete ? next.lastPageCheckedAt : null;
  return next;
}

// Invoke repeatedly with unchanged config + RUN_ID until complete or a permanent halt.
function continueArchiveScan() {
  var lock, locked = false, state = null;
  try {
    var config = scanConfig_(); // Empty defaults fail before any Drive call.
    lock = LockService.getScriptLock();
    if (!lock.tryLock(1000)) fail_('LOCK_BUSY');
    locked = true;
    var account = account_();
    var properties = PropertiesService.getScriptProperties();
    var key = 'archiveScan.v1.' + hash_(RUN_ID);
    state = load_(properties, key, account, config);
    if (state.complete) return emit_(result_(state, 'SCAN_ALREADY_COMPLETE', null, false));
    if (state.halt) return emit_(result_(state, 'SCAN_HALTED', state.halt, false));
    // Commit a new run before the first remote page.
    state.invocations++;
    save_(properties, key, state);
    var started = Date.now();
    for (var n = 0; n < LIMITS_.pages && Date.now() - started < LIMITS_.milliseconds; n++) {
      var params = {corpora: DRIVE_ID ? 'drive' : 'user', spaces: 'drive', pageSize: 1000,
        q: "trashed = false and mimeType != 'application/vnd.google-apps.folder'",
        fields: LIST_FIELDS_, supportsAllDrives: true, includeItemsFromAllDrives: true};
      if (DRIVE_ID) params.driveId = DRIVE_ID;
      if (state.nextToken !== null) params.pageToken = state.nextToken;
      var response = Drive.Files.list(params); // Exceptions are never printed.
      var next;
      try {
        next = page_(state, response, config.targets);
        save_(properties, key, next);
      } catch (error) {
        var reason = code_(error);
        if (reason !== 'STATE_WRITE_FAILED' && reason !== 'API_FAILED') {
          var halted = JSON.parse(JSON.stringify(state)); halted.halt = reason;
          // Even if marking the halt exceeds quota, the old checkpoint remains incomplete.
          try { save_(properties, key, halted); state = halted; } catch (ignored) {}
        }
        return emit_(result_(state, 'SCAN_INCOMPLETE', reason, false));
      }
      state = next;
      if (state.complete) return emit_(result_(state, 'SCAN_COMPLETE', null, state.invocations === 1));
    }
    return emit_(result_(state, 'SCAN_PAUSED', null, false));
  } catch (error) { return emit_(result_(state, 'SCAN_INCOMPLETE', code_(error), false)); }
  finally { if (locked) { try { lock.releaseLock(); } catch (ignored) {} } }
}
