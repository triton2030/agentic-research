"""Read-only checks of the submitted first-wave interview artifacts."""
from pathlib import Path
import hashlib
import json
import re

base = Path(__file__).resolve().parent

def hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}

def inspect_interview(path):
    body = path.read_text()
    missing = []
    for match in re.finditer(r'\]\(<?([^\s)>]+)>?\)', body):
        target = match.group(1).split('#', 1)[0]
        if target and not target.startswith(('http:', 'https:')):
            if not (path.parent / target).exists():
                missing.append(target)
    before_found = body.split('## Ответы, найденные при исследовании', 1)[0]
    return {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'missing_local_link_files': sorted(set(missing)),
        'question_headings': re.findall(r'^### (.+)', body, re.M),
        'h4_answer_fields': re.findall(r'^#### (.+)', body, re.M),
        'html_details_count': body.count('<details>'),
        'selected_checkboxes_before_found_answers': re.findall(r'^- \[x\].*', before_found, re.M),
        'has_service_search_phrase': 'Все четыре документа прочитаны полностью' in body,
    }

result = {
    'scope': 'Byte identity and artifact structure only; no model execution or semantic completeness claim.',
    'candidate_skill_hashes': hashes(base / 'candidate'),
    'candidate_matches_new_probe_skill': hashes(base / 'candidate') == hashes(base / 'probe-new/skill'),
    'before_matches_old_probe_skill': hashes(base / 'before') == hashes(base / 'probe-old/skill'),
    'project_hashes': hashes(base / 'probe-new/project'),
    'projects_are_byte_identical': hashes(base / 'probe-new/project') == hashes(base / 'probe-old/project'),
    'new_interview': inspect_interview(base / 'probe-new/result/interview.md'),
    'old_interview': inspect_interview(base / 'probe-old/result/2026-09-15-masterclass-booking.md'),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
