import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone

out=Path('/tmp/google-drive-skill-20261018')
cwd=out/'codex-foreign-cwd'; cwd.mkdir(exist_ok=True)
prompt='''Это ограниченная проверка обнаружения установленного глобального скилла, а не архивная операция. Не используй сеть, Google, MCP, субагентов. Не изменяй файлы и настройки, не читай credentials или личные отчёты. Сначала проверь, присутствует ли 1google-drive-archive в доступном тебе каталоге skills, и назови источник этого наблюдения. Затем прочитай установленный SKILL.md и нужные references; читать разрешено только этот пакет. Ответь JSON: advertised_in_catalog (boolean), skill_loaded (boolean), package_path, cases с use/skip и причинами для (1) сверить INSV с реальным Drive перед освобождением Mac, (2) переименовать Drive-документ, (3) измерить локальную папку без облака, (4) перепроверить известный облачный ID из старого манифеста. Также укажи, разрешает ли один MATCH удаление, нужно ли повторять полный обход Drive для известного ID, и проверен ли новый cloud asset live. Не выдавай предположение о каталоге за наблюдение.'''
(out/'codex-runtime-prompt.txt').write_text(prompt)
env=os.environ.copy(); removed=[]
for name in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_BASE_URL','OPENAI_API_BASE'):
    if name in env: removed.append(name); env.pop(name)
args=['/opt/homebrew/bin/codex','exec','--ignore-user-config','--skip-git-repo-check',
      '--ephemeral','--json','--sandbox','read-only','--model','gpt-6.1-sol',
      '-c','model_reasoning_effort="high"','-c','approval_policy="never"',
      '-c','web_search="disabled"','-C',str(cwd),'-']
report={'date':datetime.now(timezone.utc).isoformat(),'purpose':'fresh Codex installed skill discovery and synthetic routing',
        'modelRequested':'gpt-6.1-sol','reasoningEffort':'high','auth':'existing ChatGPT login',
        'credentialEnvironmentOverridesRemoved':removed,'events':[]}
try:
    p=subprocess.run(args,input=prompt,cwd=cwd,env=env,capture_output=True,text=True,timeout=240)
    report['exitCode']=p.returncode; report['stderrPresent']=bool(p.stderr)
    for line in p.stdout.splitlines():
        try: item=json.loads(line)
        except json.JSONDecodeError: continue
        if item.get('type')=='item.completed':
            event=item.get('item',{})
            typ=event.get('type')
            if typ=='agent_message': report.setdefault('messages',[]).append(event.get('text'))
            elif typ=='command_execution': report['events'].append({'type':typ,'command':event.get('command'),'exitCode':event.get('exit_code')})
        elif item.get('type') in ('turn.failed','error'):
            report['failure']=item
except subprocess.TimeoutExpired:
    report['status']='timeout'
(out/'codex-runtime-probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
