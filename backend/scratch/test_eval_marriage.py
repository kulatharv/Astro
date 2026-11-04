import sys, os
sys.path.insert(0, os.path.abspath("."))
from modules.kundali.engine import calculate_kundali
from shared.veda.marriage import evaluate_marriage_rules
from modules.prediction.scoring import _build_ctx

res = calculate_kundali(2004, 11, 2, 16, 15, 19.8762, 75.3433, tz_name="Asia/Kolkata")
ctx = _build_ctx(res)
eval_res = evaluate_marriage_rules(ctx)
print("Score:", eval_res["score"])
print("Supports:", eval_res["supports_count"])
print("Obstructs:", eval_res["obstructs_count"])
print("Conditional:", eval_res["conditional_count"])
print("\nMatched rules:")
for r in eval_res["matched_rules"]:
    print(f"- [{r['effect']}] {r['rule_id']}: {r['reason']}")
print("\nRejected rules:")
for r in eval_res["rejected_rules"]:
    print(f"- {r['rule_id']}: {r['reason']} (Rejected by: {r['cancellation_reason']})")
