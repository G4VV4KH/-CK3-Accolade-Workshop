"""Static source/nine-language validation; no native or visual acceptance claim."""
import argparse
import json
from pathlib import Path
import re
import hashlib
ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(path):
    return {p.relative_to(path).as_posix(): digest(p) for p in sorted(path.rglob("*")) if p.is_file() and (p.relative_to(path).parts[0] in {"common", "gfx", "gui", "localization"} or p.relative_to(path).as_posix() in {"descriptor.mod", "thumbnail.png"})}


LANGUAGES=('english','french','german','japanese','korean','polish','russian','simp_chinese','spanish')

def check(source):
    errors=[]
    files=inventory(source)
    text_files=[source/p for p in files if Path(p).suffix in {'.txt','.gui','.yml'} and p.split('/')[0]!='publishing']
    for path in text_files:
        raw=path.read_bytes()
        if not raw.startswith(b'\xef\xbb\xbf'):
            errors.append(f'{path.relative_to(source)}: missing UTF-8 BOM')
        text=raw.decode('utf-8-sig')
        if path.suffix in {'.txt','.gui'}:
            # Remove strings and comments before checking delimiter balance.
            normalized=re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*','',text)
            depth=0
            for char in normalized:
                depth+=1 if char=='{' else -1 if char=='}' else 0
                if depth<0: break
            if depth!=0: errors.append(f'{path.relative_to(source)}: unbalanced script braces')
            if re.search(r'AW_TEST\||aw_probe_',text): errors.append(f'{path.relative_to(source)}: test instrumentation leaked')
    loc={}
    for language in LANGUAGES:
        keys={}
        locale_files=sorted((source/'localization'/language).rglob('*.yml'))
        if not locale_files: errors.append(f'{language}: missing localization files')
        for path in locale_files:
            if not path.name.endswith(f'_l_{language}.yml'): errors.append(f'{path.name}: wrong locale filename')
            lines=path.read_text(encoding='utf-8-sig').splitlines()
            if not lines or lines[0].strip()!=f'l_{language}:': errors.append(f'{path.name}: wrong locale header')
            for number,line in enumerate(lines[1:],2):
                if not line.strip() or line.lstrip().startswith('#'): continue
                match=re.fullmatch(r'\s+([A-Za-z0-9_.-]+):(?:\d+)?\s+"((?:\\.|[^"\\])*)"\s*',line)
                if not match:
                    errors.append(f'{path.name}:{number}: invalid localization record')
                    continue
                key,value=match.groups()
                if key in keys: errors.append(f'{path.name}:{number}: duplicate {key}')
                keys[key]=value
                if not value.strip(): errors.append(f'{path.name}:{number}: empty translation')
                if '\ufffd' in value: errors.append(f'{path.name}:{number}: replacement character in translation')
                if value.count('[')!=value.count(']'): errors.append(f'{path.name}:{number}: unbalanced substitution brackets')
                if value.count('$')%2: errors.append(f'{path.name}:{number}: unbalanced string substitution')
                if re.search(r'\\(?![ntr"\\])',value): errors.append(f'{path.name}:{number}: unsupported escape sequence')
                styles=re.findall(r'#[A-Za-z_][A-Za-z0-9_]*|#!',value)
                if sum(token!='#!' for token in styles)!=styles.count('#!'):
                    errors.append(f'{path.name}:{number}: unbalanced formatting markers')
        loc[language]=keys
    for language in LANGUAGES[1:]:
        missing=sorted(loc['english'].keys()-loc[language].keys())
        extra=sorted(loc[language].keys()-loc['english'].keys())
        if missing or extra: errors.append(f'{language}: English key set differs; missing={missing}, extra={extra}')
        for key,value in loc['english'].items():
            if key not in loc[language]: continue
            translated=loc[language][key]
            for kind,pattern in (
                ('substitutions',r'\[[^\]]+\]|\$[A-Za-z0-9_.]+\$'),
                ('formatting markers',r'#[A-Za-z_][A-Za-z0-9_]*|#!'),
                ('escaped controls',r'\\[ntr]'),
            ):
                if sorted(re.findall(pattern,value))!=sorted(re.findall(pattern,translated)):
                    errors.append(f'{key}: English/{language} {kind} differ')
    referenced=set()
    for path in text_files:
        if path.suffix in {'.txt','.gui'}:
            referenced.update(re.findall(r'"(aw_[a-z0-9_]+)"',path.read_text(encoding='utf-8-sig')))
    # Widget IDs and persistent variables are not localization references.
    for key in referenced:
        if key.startswith(('aw_ui_', 'aw_rank_')) and key not in loc['english']:
            # Only require keys used by a localized GUI property, not state/ID names.
            if any(re.search(r'(?:text|tooltip|tooltip_when_disabled)\s*=\s*"'+re.escape(key)+'"',p.read_text(encoding='utf-8-sig')) for p in text_files if p.suffix=='.gui'):
                errors.append(f'missing localized GUI key {key}')
    return {'status':'PASS' if not errors else 'FAIL','errors':errors,'english_keys':len(loc['english']),'russian_keys':len(loc['russian']),'required_languages':list(LANGUAGES),'language_keys':{language:len(keys) for language,keys in loc.items()},'runtime_sha256':{k:v for k,v in files.items() if k.split('/')[0]!='publishing' and not k.endswith('.md')},'scope':'Static syntax and all nine installed localization variants, keys, substitutions, formatting and escapes; no native/visual claim.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=ROOT)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    report=check(args.source)
    if args.output:
        if args.output.exists(): raise SystemExit('Report exists')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='runtime_sha256'},ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status']=='PASS' else 1)
