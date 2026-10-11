"""Import the supplied reviewed snapshot into a fresh checkout; no network/provider.

Only pinned runtime evidence is copied, never the full research archive. Originals
are read-only. Validate every byte before writes; an existing destination is never
replaced. No environment or persistent credential configuration is performed.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import os
import shutil

from .corpus import JCEB_HASH,KCEB_HASH,JCEB_TEXT_HASH,KCEB_TEXT_HASH,INVENTORY_HASH
from .candidate_sources import SUMMARY_SHA,MANIFEST_SHA
from .demo_sources import load as load_prepared

PACK='OpenOracle-JacksonCounty-2026-Research/'
PINS={
    PACK+'jceb/2026-11-03-notice-sample-ballot.pdf':JCEB_HASH,
    PACK+'jceb/2026-11-03-notice-sample-ballot.md':JCEB_TEXT_HASH,
    PACK+'raw/kceb-sample.pdf':KCEB_HASH,
    PACK+'markdown/kceb-sample.md':KCEB_TEXT_HASH,
    PACK+'COUNTYWIDE-INVENTORY.md':INVENTORY_HASH,
    PACK+'candidate_records/candidate-sources.md':SUMMARY_SHA,
    PACK+'candidate_records/manifest.json':MANIFEST_SHA,
    PACK+'raw/combat-6096-adopted.pdf':'5fa4474560da047207bfd7c7033de0d0a1febb20d6e92cc6447982ca71a1afde',
    PACK+'markdown/combat-6096-adopted.md':'eff0807d7f6a29e07f478121aff3ec068c0c04c77b951ee602a969c1658a57fe',
    'Election-Measure-Audit-2026-10-11/raw/rsmo-67.547.html':'37b9538360246463997e93fe9ef1b46935a3b322d8eef65c4214a98017702ac7',
}


def read_bound(root,relative,expected=None):
    root=Path(root).resolve(strict=True)
    p=root/relative
    if p.is_symlink() or not p.is_file() or not p.resolve(strict=True).is_relative_to(root):
        raise ValueError('Expected a regular file inside the supplied archive')
    # An ancestor symlink could be replaced independently; refuse it too.
    for parent in p.parents:
        if parent==root:break
        if parent.is_symlink():raise ValueError('Symlinked archive component refused')
    if not 0<p.stat().st_size<=32*1024*1024:raise ValueError('Evidence size outside import bounds')
    data=p.read_bytes()
    if expected and sha256(data).hexdigest()!=expected:raise ValueError('Source checksum differs from reviewed snapshot: '+relative)
    return data


def collect(research,prepared=None):
    research=Path(research)
    files={p:read_bound(research,p,h)for p,h in PINS.items()}
    records=json.loads(files[PACK+'candidate_records/manifest.json'])
    for record in records:
        ident=record['id']
        if not ident.startswith('judge-2026-') or not ident.endswith(('-lawyer','-juror')) or record.get('status')!='downloaded':continue
        filename=record['raw_file']
        if Path(filename).name!=filename or not filename.endswith('.pdf'):raise ValueError('Unsafe candidate-original path')
        path=PACK+'candidate_records/'+filename
        files[path]=read_bound(research,path,record['sha256'])
    extras={}
    if prepared is not None:
        prepared=Path(prepared)
        for name in ('beacon-atlarge.json','beacon-atlarge-2026-09-22.html'):extras[name]=read_bound(prepared,name)
        if len(load_prepared(prepared))!=4:raise ValueError('Prepared candidate answers differ from reviewed passages')
    return files,extras


def install(research,prepared=None,*,checkout=None,check_only=False):
    root=Path(checkout or Path(__file__).resolve().parents[1]).resolve(strict=True)
    research_target=root/'research/HackMidwest2026_research'
    prepared_target=root/'.local/sources'
    # The existing checkout ignores these archives; importing does not publish them.
    ignores=(root/'.gitignore').read_text().splitlines()
    if 'research/HackMidwest2026_research/' not in ignores or '.local/' not in ignores:
        raise ValueError('Checkout must exclude imported source archives from Git')
    files,extras=collect(research,prepared)
    if research_target.exists() or (extras and prepared_target.exists()):
        raise ValueError('Import is for an unused destination; existing evidence is never overwritten')
    report={'research_files':len(files),'prepared_files':len(extras),'network_calls':0,'model_calls':0,
        'copied':False,'originals_modified':False,'full_archive_copied':False,
        'original_sha256_by_path':{p:sha256(b).hexdigest()for p,b in files.items()}}
    if check_only:return report
    local=root/'.local';local.mkdir(exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='source-bootstrap-',dir=local))
    try:
        a=stage/'research';a.mkdir()
        for rel,data in files.items():p=a/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        b=stage/'prepared';b.mkdir()
        for rel,data in extras.items():(b/rel).write_bytes(data)
        # All evidence is verified and staged before either archive becomes visible.
        research_target.parent.mkdir(exist_ok=True)
        if research_target.exists() or (extras and prepared_target.exists()):raise ValueError('Destination appeared during validation')
        os.rename(a,research_target)
        if extras:os.rename(b,prepared_target)
        report['copied']=True
    finally:shutil.rmtree(stage)
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--research',required=True,type=Path,help='Supplied retained research directory; read-only')
    ap.add_argument('--prepared',type=Path,help='Optional existing .local/sources directory; read-only')
    ap.add_argument('--check-only',action='store_true')
    args=ap.parse_args()
    try:report=install(args.research,args.prepared,check_only=args.check_only)
    except (OSError,ValueError,KeyError) as exc:ap.exit(2,'Source import failed: '+str(exc)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
