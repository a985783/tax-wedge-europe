# Q1 Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将当前项目升级到接近 EER（准 Q1）标准，保证识别策略一致、可复现、审计与稳健性完整，并允许主结论在严格方法下调整。

**Status:** **COMPLETED** (Verified by tests on 2026-01-28)

**Architecture:** 采用统一配置驱动的数据管线（抓取→清洗→识别→估计→稳健性/审计），并以“严格堆叠事件研究 + 控制组 + FE”为主估计，辅以面板 LP 作为稳健性。所有关键参数写入配置文件并进入可复现元数据。

**Tech Stack:** Python, pandas, numpy, statsmodels, linearmodels, matplotlib, seaborn, eurostat, pytest

---

> 备注：当前目录不是 git 仓库，无法创建 worktree。用户已确认直接在当前目录实施；计划中的“提交”步骤若无 git 可跳过。

### Task 1: 引入统一配置与配置读取 (Done)

**Files:**
- Create: `analysis_config.yaml`
- Create: `src/utils/config.py`
- Create: `tests/test_config.py`
- Modify: `requirements.txt`

**Step 1: Write the failing test**

```python
# tests/test_config.py
from src.utils.config import load_config

def test_load_config_has_required_keys(tmp_path):
    cfg = load_config("analysis_config.yaml")
    assert "event_threshold" in cfg
    assert "clean_window_months" in cfg
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL (module or file not found)

**Step 3: Write minimal implementation**

```python
# src/utils/config.py
import yaml

def load_config(path="analysis_config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)
```

Create `analysis_config.yaml` with baseline参数：

```yaml
# analysis_config.yaml
fetch:
  datasets:
    - prc_hicp_midx
    - prc_hicp_cind
    - prc_hicp_inw
    - prc_hicp_cmon
identification:
  event_threshold: 0.01
  clean_window_months: 12
  base_period: -1
analysis:
  event_window: 12
  cluster_levels: [geo, geo_coicop, geo_year]
  weight_column: weight
robustness:
  thresholds: [0.005, 0.01, 0.02]
  windows: [6, 12, 24]
```

Update `requirements.txt` add `pytest`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add analysis_config.yaml src/utils/config.py tests/test_config.py requirements.txt
git commit -m "chore: add analysis config loader"
```

---

### Task 2: 标准化时间解析与数据清单/哈希 (Done)

**Files:**
- Create: `src/utils/time_parse.py`
- Modify: `src/data/fetch.py`
- Create: `tests/test_time_parse.py`

**Step 1: Write the failing test**

```python
# tests/test_time_parse.py
from src.utils.time_parse import normalize_time

def test_normalize_time():
    assert normalize_time("2020M01") == "2020-01"
    assert normalize_time("1999M12") == "1999-12"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_time_parse.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/utils/time_parse.py
import re

def normalize_time(t):
    if t is None:
        return t
    s = str(t)
    m = re.match(r"^(\d{4})M(\d{2})$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return s
```

Update `src/data/fetch.py` to:
- 对 time 列批量 `normalize_time`
- 生成 `output/metadata/data_manifest.json` 和 `data_hashes.json`（记录 row count、time range、hash）

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_time_parse.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/utils/time_parse.py src/data/fetch.py tests/test_time_parse.py
git commit -m "feat: normalize time and add fetch manifest"
```

---

### Task 3: 清洗阶段时间一致性与数据质量报告 (Done)

**Files:**
- Modify: `src/data/clean.py`
- Create: `tests/test_clean_time.py`

**Step 1: Write the failing test**

```python
# tests/test_clean_time.py
from src.utils.time_parse import normalize_time

def test_clean_time_format():
    assert normalize_time("2015M03") == "2015-03"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_clean_time.py -v`
Expected: FAIL if normalize_time not available in import path

**Step 3: Write minimal implementation**

Update `src/data/clean.py` to use `normalize_time` on `time` and write `output/metadata/data_quality.json` (missing率、对齐率、时间范围)。

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_clean_time.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/data/clean.py tests/test_clean_time.py
git commit -m "feat: normalize clean time and add data quality report"
```

---

### Task 4: 统一事件识别阈值与 clean window 逻辑 (Done)

**Files:**
- Modify: `src/identification/detect_events.py`
- Create: `tests/test_detect_events.py`

**Step 1: Write the failing test**

```python
# tests/test_detect_events.py
import pandas as pd
from src.identification.detect_events import apply_clean_window

def test_clean_window_geo_coicop():
    df = pd.DataFrame({
        "geo": ["AA", "AA", "AA"],
        "coicop": ["CP01", "CP01", "CP01"],
        "time": ["2020-01", "2020-03", "2020-10"],
        "delta_tw": [0.02, 0.03, 0.02]
    })
    out = apply_clean_window(df, window_months=6)
    # 2020-03 should be flagged as not clean due to proximity to 2020-01
    assert out.loc[1, "is_clean"] is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_detect_events.py -v`
Expected: FAIL (function not found)

**Step 3: Write minimal implementation**

Refactor `detect_events.py`:
- 读取 `analysis_config.yaml`
- 用 `normalize_time`
- 新增 `apply_clean_window(df, window_months)`，按 geo×coicop 计算距离
- 统一阈值 `event_threshold`
- 输出 `output/metadata/events_summary.json`

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_detect_events.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/identification/detect_events.py tests/test_detect_events.py
git commit -m "feat: standardize event detection and clean window"
```

---

### Task 5: 主估计重构（堆叠事件研究 + 控制组 + FE） (Done)

**Files:**
- Modify: `src/analysis/models.py`
- Create: `tests/test_stacked_controls.py`

**Step 1: Write the failing test**

```python
# tests/test_stacked_controls.py
import pandas as pd
from src.analysis/models import build_stacked_with_controls

def test_build_stacked_with_controls_has_controls():
    # minimal toy data
    df = pd.DataFrame({
        "geo": ["A", "B"],
        "coicop": ["CP01", "CP01"],
        "time": ["2020-01", "2020-01"],
        "log_hicp": [4.6, 4.5],
        "weight": [1.0, 1.0]
    })
    events = pd.DataFrame({
        "geo": ["A"], "coicop": ["CP01"], "time": ["2020-01"], "delta_tw": [0.02]
    })
    stacked = build_stacked_with_controls(df, events, half_window=0)
    assert (stacked["treated"] == 0).any()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_stacked_controls.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Refactor `models.py`:
- 新增 `build_stacked_with_controls`：
  - 对每个事件，在同一 coicop 内纳入其他国家作为控制组
  - 构造 `treated`, `event_id`, `rel_time`
- 主回归：`norm_log_hicp ~ C(rel_time):shock_size:treated + C(rel_time) + unit_FE + month_FE`
- 权重回归（WLS）并输出聚类稳健标准误

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_stacked_controls.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/analysis/models.py tests/test_stacked_controls.py
git commit -m "feat: stacked event study with controls and FE"
```

---

### Task 6: 稳健性矩阵与 Placebo (Done)

**Files:**
- Modify: `src/analysis/models.py` or Create: `src/analysis/robustness.py`
- Create: `tests/test_placebo.py`

**Step 1: Write the failing test**

```python
# tests/test_placebo.py
from src.analysis.robustness import run_placebo

def test_placebo_runs(tmp_path):
    result = run_placebo(seed=1, n_sim=5)
    assert "pvals" in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_placebo.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement placebo randomization and outputs:
- `output/tables/placebo_summary.csv`
- `output/figures/placebo_distribution.png`

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_placebo.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/analysis/robustness.py tests/test_placebo.py
git commit -m "feat: add placebo and robustness suite"
```

---

### Task 7: 事件审计与元数据匹配 (Done)

**Files:**
- Create: `src/audit/metadata_match.py`
- Create: `tests/test_audit_match.py`

**Step 1: Write the failing test**

```python
# tests/test_audit_match.py
from src.audit.metadata_match import match_events

def test_match_events_runs():
    out = match_events(sample_n=5, seed=1)
    assert "precision" in out
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_audit_match.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement metadata matching (Eurostat `prc_hicp_manr`) + 输出:
- `output/tables/audit_summary.tex`
- `output/tables/audit_summary.csv`

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_audit_match.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/audit/metadata_match.py tests/test_audit_match.py
git commit -m "feat: add audit metadata matching"
```

---

### Task 8: 论文与附录对齐更新 (Done)

**Files:**
- Modify: `PAPER_EXPANDED.md`
- Modify: `intro_1page.md`
- Modify: `results_main.md`
- Modify: `robustness.md`
- Modify: `robustness_appendix.md`
- Modify: `audit_protocol.md`

**Step 1: Write the failing test**

N/A (documentation)

**Step 2: Run test to verify it fails**

N/A

**Step 3: Write minimal implementation**

- 更新方法与识别描述，确保与代码一致
- 写明阈值、clean window、控制组与 FE 结构
- 添加稳健性矩阵与审计输出的引用

**Step 4: Run test to verify it passes**

N/A

**Step 5: Commit**

```bash
git add PAPER_EXPANDED.md intro_1page.md results_main.md robustness.md robustness_appendix.md audit_protocol.md
git commit -m "docs: align paper with methods and outputs"
```

---

### Task 9: README 与复现说明 (Done)

**Files:**
- Modify: `README.md`

**Step 1: Write the failing test**

N/A

**Step 2: Run test to verify it fails**

N/A

**Step 3: Write minimal implementation**

- 增加 `analysis_config.yaml` 与 `output/metadata` 说明
- 增加一键复现步骤与联网需求

**Step 4: Run test to verify it passes**

N/A

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add reproducibility instructions"
```

---

### Task 10: 全流程复现与输出验证 (Done)

**Files:**
- Run only

**Step 1: Write the failing test**

N/A

**Step 2: Run test to verify it fails**

N/A

**Step 3: Write minimal implementation**

Run pipeline (requires network):

```bash
python src/data/fetch.py
python src/data/clean.py
python src/identification/detect_events.py
python src/analysis/models.py
python src/analysis/robustness.py
python src/audit/metadata_match.py
```

Verify outputs exist:
- `output/figures/main_event_study.png`
- `output/tables/main_regression_results.tex`
- `output/tables/robustness_summary.csv`
- `output/tables/audit_summary.tex`
- `output/metadata/data_manifest.json`

**Step 4: Run test to verify it passes**

Manual check of output files and log summary.

**Step 5: Commit**

```bash
git add output/ metadata/
git commit -m "chore: regenerate outputs"
```
