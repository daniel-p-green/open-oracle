"""Validate/import the reviewed public SOS packet into ignored local originals.

No network, providers, visitor lookup or public release. Call with --archive to
validate only; --install copies only pinned admitted files to the local archive.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from open_oracle.corpus import Corpus
from strands_quality.research_corpus import load_verified_corpus
from strands_quality.voting_procedure import admission, load_voting_procedure, CONTEST_ID

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    packet = admission(args.archive)
    load_voting_procedure(args.archive)
    archive = args.archive
    if args.install:
        archive = PROJECT / ".local/sources/missouri-voting-procedure"
        names = ["admission.json"] + [s[k] for s in packet["sources"] for k in ("original_path", "extracted_path")]
        # Refuse an unknown existing archive before making any writes.
        for name in names:
            target = archive / name
            if target.exists() and target.read_bytes() != (args.archive / name).read_bytes():
                raise ValueError("Existing admitted original differs; preserve for owner reconciliation")
        archive.mkdir(parents=True, exist_ok=True)
        for name in names:
            shutil.copyfile(args.archive / name, archive / name)
    registry = load_verified_corpus(Corpus(), voting_procedure_archive=archive)
    print(json.dumps({"archive": str(archive), "sources": len(registry.sources),
                      "procedure_sources": 5, "procedure_chunks": sum(c.contest_id == CONTEST_ID for c in registry.chunks.values()),
                      "claims": 12, "indexed": True, "public_release": False, "provider_calls": 0}))

if __name__ == "__main__":
    main()
