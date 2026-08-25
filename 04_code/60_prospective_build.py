#!/usr/bin/env python3
"""Prospective candidate build (P4) — cqadupstack-android.

Logic is byte-for-byte build_candidates.py (shift-study ef825e1d): BM25 + 3
dense retrievers, K0=10, M=30, identical features and CSV schema. The ONLY
changes are CPU execution (device, batch size) and standalone embedding
caching — recorded as deviations in the lock's run log. qrels are touched
only to write the judged/grade/relevant columns (auditor stand-in), exactly
as the original builder does.

Usage: python3 60_prospective_build.py cqadupstack-android
"""
import csv, os, sys, time
import numpy as np
import torch
import bm25s

sys.path.insert(0, "/root/shift-study/src")
from common import DATA, RUNS, DENSE, K0, M, load_beir, eligible_qids  # noqa: E402

EMB = os.path.join(DATA, "emb")
OUT = os.path.join(RUNS, "candidates")
os.makedirs(EMB, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH = 512 if DEVICE == "cuda" else 64


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


def tset(s):
    return set(s.lower().split())


def corpus_embeddings_cpu(name, model_key, texts_ordered):
    path = os.path.join(EMB, f"{name}__{model_key}_docs.npy")
    if os.path.exists(path):
        return np.load(path, mmap_mode="r")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(DENSE[model_key], device=DEVICE)
    emb = model.encode(texts_ordered, batch_size=BATCH, convert_to_numpy=True,
                       normalize_embeddings=True,
                       show_progress_bar=False).astype(np.float32)
    np.save(path, emb)
    return emb


def build(name):
    if os.path.exists(os.path.join(OUT, f"{name}.csv")):
        log(f"skip {name} (exists)")
        return
    log(f"=== {name} (device={DEVICE}) ===")
    texts, queries, qrels = load_beir(name)
    qids = eligible_qids(queries, qrels)
    dids = list(texts.keys())
    doc_texts = [texts[d] for d in dids]
    q_texts = [queries[q] for q in qids]
    q_tok = [tset(t) for t in q_texts]
    log(f"docs={len(dids)} queries={len(qids)}")

    ret = bm25s.BM25()
    ret.index(bm25s.tokenize(doc_texts, stopwords="en", show_progress=False),
              show_progress=False)
    bi, bsc = ret.retrieve(bm25s.tokenize(q_texts, stopwords="en", show_progress=False),
                           k=min(M, len(dids)), show_progress=False)
    sysret = {"bm25": (bi, bsc)}
    log("bm25 done")

    from sentence_transformers import SentenceTransformer
    for skey in DENSE:
        demb = corpus_embeddings_cpu(name, skey, doc_texts)
        model = SentenceTransformer(DENSE[skey], device=DEVICE)
        qemb = model.encode(q_texts, batch_size=BATCH, convert_to_numpy=True,
                            normalize_embeddings=True,
                            show_progress_bar=False).astype(np.float32)
        dt = torch.from_numpy(np.ascontiguousarray(demb))
        qt = torch.from_numpy(qemb)
        ii, ss = [], []
        for s0 in range(0, len(qids), 256):
            sims = qt[s0:s0 + 256] @ dt.T
            v, ix = torch.topk(sims, min(M, dt.shape[0]), dim=1)
            ii.extend(ix.numpy())
            ss.extend(v.numpy())
        sysret[skey] = (ii, ss)
        del dt, qt
        log(f"  {skey} done")

    with open(os.path.join(OUT, f"{name}.csv"), "w", newline="") as fc, \
         open(os.path.join(OUT, f"{name}_meta.csv"), "w", newline="") as fm:
        wc = csv.writer(fc)
        wm = csv.writer(fm)
        wc.writerow(["qid", "docid", "score_norm", "rank", "consensus", "lexoverlap",
                     "in_bm25top10", "judged", "grade", "relevant"])
        wm.writerow(["qid", "nG", "n_judged"])
        for qi, qid in enumerate(qids):
            rel = qrels[qid]
            G = set(d for d, g in rel.items() if g > 0)
            wm.writerow([qid, len(G), len(rel)])
            bm25_top10 = set(dids[j] for j in sysret["bm25"][0][qi][:K0])
            agg = {}
            for skey, (idxs, scs) in sysret.items():
                row_i, row_s = idxs[qi], scs[qi]
                top1 = float(row_s[0]) if len(row_s) else 1.0
                for r, (j, sc) in enumerate(zip(row_i, row_s)):
                    d = dids[j]
                    sn = float(sc) / (abs(top1) + 1e-9)
                    if d not in agg:
                        agg[d] = dict(score_norm=sn, rank=r, consensus=1)
                    else:
                        agg[d]["consensus"] += 1
                        agg[d]["score_norm"] = max(agg[d]["score_norm"], sn)
                        agg[d]["rank"] = min(agg[d]["rank"], r)
            for d, info in agg.items():
                lex = len(q_tok[qi] & tset(texts[d])) / max(len(q_tok[qi]), 1)
                grade = rel.get(d, -1)
                wc.writerow([qid, d, f"{info['score_norm']:.6f}", info["rank"],
                             info["consensus"], f"{lex:.6f}",
                             int(d in bm25_top10), int(d in rel),
                             grade, int(grade > 0)])
    log(f"{name} saved")


if __name__ == "__main__":
    for name in sys.argv[1:]:
        build(name)
    log("DONE")
