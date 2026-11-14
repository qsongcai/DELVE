import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from botocore.config import Config
import requests

DATASET = "ds007541"
CACHE = Path("pilot_dl/cache")
ROOT = CACHE / DATASET
BASE = f"s3://openneuro.org/{DATASET}"

# ---------- 1. 拉全部记录 ----------
flt = json.dumps({"dataset": DATASET})
recs, skip = [], 0
while True:
    r = requests.get("https://data.eegdash.org/api/eegdash/records",
                     params={"filter": flt, "limit": 1000, "skip": skip}, timeout=60)
    r.raise_for_status()
    batch = r.json().get("data", [])
    if not batch:
        break
    recs.extend(batch)
    if len(batch) < 1000:
        break
    skip += 1000
print("records:", len(recs))

# ---------- 2. 构建文件清单（BIDS 命名，openneuro 直接可取） ----------
pairs = []
for rec in recs:
    st = rec.get("storage") or {}
    keys = [st.get("raw_key")] + list(st.get("dep_keys") or [])
    for k in keys:
        if not k:
            continue
        uri = f"{BASE}/{k}"
        local = ROOT / k
        pairs.append((uri, local))
# 去重
pairs = list({str(l): (u, l) for u, l in pairs}.values())
print("total files:", len(pairs))

# ---------- 3. 并发下载 ----------
cfg = Config(region_name="us-east-2", signature_version="UNSIGNED",
             retries={"max_attempts": 5, "mode": "standard"})
s3 = boto3.client("s3", config=cfg)

def bucket_key(uri):
    assert uri.startswith("s3://")
    rest = uri[len("s3://"):]
    bucket, _, key = rest.partition("/")
    return bucket, key

def download(item):
    uri, local = item
    if local.exists() and local.stat().st_size > 0:
        return "skip"
    local.parent.mkdir(parents=True, exist_ok=True)
    bucket, key = bucket_key(uri)
    tmp = local.with_suffix(local.suffix + ".part")
    for t in range(6):
        try:
            resp = s3.get_object(Bucket=bucket, Key=key)
            with open(tmp, "wb") as f:
                for chunk in iter(lambda: resp["Body"].read(1 << 16), b""):
                    f.write(chunk)
            tmp.rename(local)
            return "ok"
        except Exception:
            time.sleep(1.5 * (t + 1))
    return "fail"

done = ok = fail = 0
fails = []
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = [ex.submit(download, p) for p in pairs]
    for fut in as_completed(futs):
        res = fut.result()
        done += 1
        if res == "ok":
            ok += 1
        elif res == "fail":
            fail += 1
            fails.append(res)
        if done % 250 == 0:
            print(f"  {done}/{len(pairs)} files (ok={ok} fail={fail})")

print(f"DONE files={done} ok={ok} skipped_or_cached={done-ok-fail} fail={fail}")
if fail:
    print("some failures; rerun to resume (resumable).")
