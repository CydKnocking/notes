# Research coordination log

- Date: 2026-09-08 (Asia/Shanghai).
- User-confirmed scope: monocular RGB, unknown camera poses, dynamic streaming/long videos; 8 H20D GPUs; target ICLR/CVPR; training-free, test-time optimization/adaptation, or modest fine-tuning.
- User-confirmed deliverable: Chinese Markdown research notes. Existing notes are context and discovery leads, not primary evidence.
- Tool availability: searched enabled tool metadata for update_plan; unavailable. Planning recorded here instead. No goal or automation created.
- Source classes: original papers (CVF, arXiv, OpenReview/NeurIPS), author project pages, official code/checkpoints and benchmark documentation. Search snippets are explicitly limited evidence.

## Plan

1. Scope and bounded discovery: complete. Read existing 4D/tracking/long-sequence notes; delegated tracking, joint optimization, and evaluation source lanes.
2. Follow-up and contradiction resolution: complete. Checked newest 2026 competition, causal vs chunk/offline operation, real training budgets, benchmark coordinate systems and code/version discrepancies.
3. Synthesis: complete. Prioritized mechanism-level hypotheses, reported reproducibility caveats and direct overlap rather than claiming novelty.
4. Deliverable verification: complete. Independent tracking and evaluation reviews complete; corrected DELTA/D4RT links, causal query scoring, initial gauge, and phase-specific training costs. Structural verification passed: 12 numbered sections, 10 consistent tables, 125 citation links (75 distinct URLs), 50 internal provenance records. Published note matches canonical text on readback. No browser visual review or universal live-link sweep was performed, as disclosed.

## Delivery

Verified final artifact: docs/papers/streaming_4d_tracking_research_2026.md (46,437 bytes at creation).
The existing user modification to docs/papers/research_diary.md was not edited by this task. No large dataset download, model execution/training, commit, publishing/deployment, or automation was performed.

## Gap matrix

| Material claim | Primary evidence | Confidence / caveat | Next action |
|---|---|---|---|
| Joint reconstruction/tracking + TTA already exists | St4RTrack paper and official repo | High; released reweighted weights differ from paper | Report both and require checkpoint pinning |
| Short-window video DPM is not validated long causal tracking | V-DPM main paper and supplement | High: about 20-frame training / 50 inference, longer pose/depth uses sliding windows and BA | Report as backbone/baseline, not turnkey strict stream |
| Generic state gating / filtering is occupied | TTT3R, FILT3R, RayMap3R primary texts | High | Do not propose only dynamic masking or Kalman gate |
| Generic 3D endpoint chaining is occupied | Point4D public indexed PDF | Medium; anonymous manuscript, full PDF fetch failed | Label discovery/watch item, no acceptance/code claim |
| World-coordinate metrics and window track handoff are occupied | TAPVid-MV Sept 2026 primary HTML Appendix B/C | High; multi-view baseline has future context | Include as overlap and adapt input protocol to mono |
| Strict causal end-to-end SpaTrackerV2 availability | Official inference script and HF Online model, agent verification | Medium/high; online tracker checkpoint is available but geometry frontend uses full video | Flag frontend causality separately |
| Point4Cast methods beyond overview | CVF proceedings, MERL official description | High for task; PDF retrieval exceeds tool size | Explicitly limit detailed implementation/cost claims |
| Runtime on 8 H20D | No local experiment | Unknown | No cross-GPU speed/memory equivalence; propose profiling |

## Search scope and stop rule

First wave: streaming dynamic 4D, joint reconstruction/tracking, 2D/3D point tracking, low-cost adaptation and public datasets (2023-2026).
Second wave: exact paper names, official repositories, appendices with training/sequence lengths, latest 2026 methods, benchmark scaling and causal leakage; new leads from local notes independently checked.
Targeted final checks: St4RTrack released loss/checkpoint differences; SpaTrackerV2 README versus HF/code; V-DPM actual 16-GH200 training; TAPVid-MV world-frame and handoff protocol; Point4D restricted evidence.
Stopping reason: core comparisons and consequential claims have primary evidence or explicit limitations; further broad search would mainly add adjacent variants. This is a decision-oriented review, not an exhaustive bibliometric survey.
