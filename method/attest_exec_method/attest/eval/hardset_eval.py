"""Evaluate Attest (full pipeline) and an enhanced LLM judge on the
LLM-refined BCB HardSet.

The HardSet (772 balanced pairs) is pooled from clone-detector
misclassifications and filtered by LLM label audit.
We report our execution-based pipeline and the balanced clone_finder direct judge.

HONESTY NOTE: this set was curated by selecting cases where an LLM agreed with the
BCB label, which biases it toward LLM-judgeable pairs; an LLM-direct number here is
therefore an upper-leaning estimate, not a neutral baseline. We report it but flag
this. Our pipeline's verdict comes from execution where available, flagged fallback
otherwise; gold is used only to score.

Usage:
    python -m attest.eval.hardset_eval --methods full clone_finder \
        --limit 0 --concurrency 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ..config import DEFAULT
from ..llm import LLMClient
from ..pipeline import run_pair
from ..prompts import clone_finder_messages, improved_direct_messages, functional_clone_messages
from ..schemas import Pair, Snippet, Verdict

HARDSET = Path(os.environ.get("ATTEST_HARDSET",
               "data/bcb_llm_refined_hard_cases"))


def _f1(tp, fp, fn):
    p = tp/(tp+fp) if tp+fp else 0.0
    r = tp/(tp+fn) if tp+fn else 0.0
    return p, r, (2*p*r/(p+r) if p+r else 0.0)


def _metrics(preds):  # preds: list of (pred, gold), pred in {0,1,None}
    tp=fp=tn=fn=0; undec=0
    for pred, gold in preds:
        if pred is None:
            undec += 1; continue
        if gold==1 and pred==1: tp+=1
        elif gold==1: fn+=1
        elif gold==0 and pred==1: fp+=1
        else: tn+=1
    p,r,f = _f1(tp,fp,fn)
    n = len(preds)
    return {"n":n,"P":round(p*100,2),"R":round(r*100,2),"F1":round(f*100,2),
            "Acc":round((tp+tn)/n*100,2) if n else 0,
            "tp":tp,"fp":fp,"tn":tn,"fn":fn,"undecided":undec}


def load_pairs(limit:int):
    funcs={}
    for line in open(HARDSET/"data.jsonl", encoding="utf-8"):
        r=json.loads(line); funcs[str(r["idx"])]=r["func"]
    pairs=[]
    for line in open(HARDSET/"test.txt", encoding="utf-8"):
        p=line.split()
        if len(p)<3: continue
        a,b,lab=p[0],p[1],int(p[2])
        if a in funcs and b in funcs:
            pairs.append(Pair(pair_id=f"hs_{a}_{b}",
                              a=Snippet(id=a,code=funcs[a],language="java"),
                              b=Snippet(id=b,code=funcs[b],language="java"),label=lab))
    return pairs[:limit] if limit else pairs


def main(argv=None)->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--methods",nargs="+",default=["full","clone_finder"],
                    choices=["full","clone_finder","improved_direct","functional_clone"])
    ap.add_argument("--limit",type=int,default=0)
    ap.add_argument("--inputs",type=int,default=8)
    ap.add_argument("--concurrency",type=int,default=6)
    ap.add_argument("--out",default="runs/hardset_eval.json")
    args=ap.parse_args(argv)

    pairs=load_pairs(args.limit)
    print(f"HardSet: {len(pairs)} pairs "
          f"({sum(1 for p in pairs if p.label==1)} clone / "
          f"{sum(1 for p in pairs if p.label==0)} non-clone)")
    client=LLMClient(DEFAULT)
    report={"n_pairs":len(pairs),"methods":{}}

    for method in args.methods:
        print(f"\n=== {method} ===")
        def one(item):
            i,p=item
            t=time.monotonic()
            if method=="full":
                try:
                    o=run_pair(p,DEFAULT,client,n_inputs=args.inputs)
                    pred=1 if o.verdict==Verdict.CLONE else (0 if o.verdict==Verdict.NON_CLONE else None)
                    extra=f"stage={o.stage_reached} fb={o.extra.get('fallback')}"
                except Exception as e:
                    pred=None; extra=f"ERR {e}"
            else:
                if method=="clone_finder": msgs=clone_finder_messages(p)
                elif method=="functional_clone": msgs=functional_clone_messages(p)
                else: msgs=improved_direct_messages(p)
                try:
                    d=client.chat_json(msgs,tag=f"{method}-{p.pair_id}",max_tokens=5000)
                    pred=1 if bool(d.get("clone",False)) else 0; extra=""
                except Exception as e:
                    pred=None; extra=f"ERR {e}"
            print(f"  [{method}] {i}/{len(pairs)} {p.pair_id} pred={pred} gold={p.label} ({time.monotonic()-t:.0f}s) {extra}")
            return (pred,p.label)
        items=list(enumerate(pairs,1))
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            preds=list(ex.map(one,items))
        m=_metrics(preds)
        report["methods"][method]=m
        print(f"  -> {m}")

    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n"+"="*60)
    for method,m in report["methods"].items():
        print(f"{method:16} P={m['P']} R={m['R']} F1={m['F1']} Acc={m['Acc']} (undec={m['undecided']})")
    print(client.cost_summary())
    print(f"-> {args.out}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
