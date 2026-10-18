import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone

out = Path('/tmp/google-drive-skill-20261018')
cwd = out / 'claude-foreign-cwd'
cwd.mkdir(exist_ok=True)
prompt = '''Проверка установленного скилла, без действий в Google Drive и без изменения файлов.
Найди установленный глобальный скилл 1google-drive-archive, вызови его через Skill и прочитай его инструкции. Если не найден, явно сообщи это. Не создавай субагентов и не запускай команды.
Для каждого случая выбери use или skip и короткую причину:
1) Сверить локальные INSV с реальными оригиналами Google Drive перед освобождением MacBook.
2) Переименовать обычный документ в Google Drive.
3) Посчитать размер локальной папки; облако пока не проверять.
4) Повторно проверить уже известный Drive ID из старого архивного манифеста.
Затем ответь: что делать, если имя и размер совпадают, SHA-256 отсутствует, а папка Mac синхронизируется через mirror? Даёт ли установка скилла разрешение на удаление и общую авторизацию для другой среды? Был ли именно новый cloud asset live-проверен?
Выдай JSON с полями skill_loaded, cases (id, decision, reason), uncertain_case, authorization, cloud_asset_status, next_step. Не читай личные файлы, отчёты проекта, настройки и credentials. Не выполняй никаких реальных архивных действий.'''
(out / 'claude-runtime-prompt.txt').write_text(prompt)
env = os.environ.copy()
removed = []
for name in list(env):
    if name.startswith('ANTHROPIC_') or name in {'CLAUDE_CODE_USE_BEDROCK','CLAUDE_CODE_USE_VERTEX','CLAUDE_CODE_USE_FOUNDRY','CLAUDE_CODE_API_KEY_HELPER_TTL_MS'}:
        removed.append(name)
        env.pop(name)
args = ['/Users/triton/.local/bin/claude', '-p', prompt,
        '--output-format', 'stream-json', '--verbose', '--tools', 'Skill,Read',
        '--allowedTools', 'Skill,Read', '--permission-mode', 'dontAsk',
        '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
        '--no-chrome', '--no-session-persistence', '--setting-sources', 'user',
        '--settings', '{"disableAllHooks":true}']
report = {'date': datetime.now(timezone.utc).isoformat(), 'purpose':'installed skill discovery and read-only synthetic routing',
          'credentialEnvironmentOverridesRemoved': removed, 'externalConnectorsDisabled':True,
          'toolsAllowed':['Skill','Read'], 'events':[]}
try:
    p = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=240)
    report['exitCode'] = p.returncode
    report['stderrPresent'] = bool(p.stderr)
    for line in p.stdout.splitlines():
        try: item=json.loads(line)
        except json.JSONDecodeError: continue
        if item.get('type') == 'system' and item.get('subtype') == 'init':
            report['model'] = item.get('model')
            report['skillAdvertised'] = '1google-drive-archive' in item.get('skills',[])
            report['authSource'] = item.get('apiKeySource')
        elif item.get('type') == 'assistant':
            for block in item.get('message',{}).get('content',[]):
                if block.get('type') == 'tool_use':
                    name = block.get('name'); inp=block.get('input',{})
                    e={'tool':name}
                    if name=='Skill': e['skill']=inp.get('skill')
                    elif name=='Read':
                        path=inp.get('file_path','')
                        e['installedSkillFile']=path if path.startswith('/Users/triton/.claude/skills/1google-drive-archive/') else 'other-path-redacted'
                    report['events'].append(e)
        elif item.get('type') == 'result':
            report['isError'] = item.get('is_error')
            report['result'] = item.get('result')
            report['numTurns'] = item.get('num_turns')
            report['modelUsageNames'] = list(item.get('modelUsage',{}))
            report['permissionDenialCount'] = len(item.get('permission_denials',[]))
except subprocess.TimeoutExpired:
    report['status']='timeout'
(out/'claude-runtime-probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
