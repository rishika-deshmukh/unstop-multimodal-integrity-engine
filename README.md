# Multimodal Submission Integrity & Plagiarism Detection Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FAISS](https://img.shields.io/badge/vector--search-FAISS-green.svg)](https://github.com/facebookresearch/faiss)
[![SentenceTransformers](https://img.shields.io/badge/embeddings-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Whisper ASR](https://img.shields.io/badge/ASR-Whisper--Tiny%2FBase-red.svg)](https://huggingface.co/openai/whisper-tiny)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An enterprise-grade, multi-modal content verification and similarity detection pipeline engineered for large-scale university evaluations, hackathons, and case competitions (designed to scale to 10,000+ submissions).

The engine analyzes submissions across multiple modalities—**PDF reports, DOCX executive summaries, and MP4 video pitches**—calculating a tri-factor integrity breakdown:
1. **Internal Peer-to-Peer Similarity %** (Unimodal text-to-text and cross-modal audio-to-text).
2. **External / Web Reference Match %** (Local reference knowledge base with source URLs).
3. **AI-Generated Content Likelihood %** (Supervised RoBERTa classifier + GPT-2 perplexity + sentence burstiness).

---

## Architecture Overview

```
                                  +------------------------------------+
                                  |   Candidate Multi-Modal Submissions|
                                  |      (.pdf, .docx, .mp4 files)     |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |    Multimodal Ingestion Layer      |
                                  |  - pypdf (Page-level text)         |
                                  |  - python-docx (Paragraph blocks)  |
                                  |  - Whisper ASR (Time-aligned audio)|
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | Text Normalization & Provenance    |
                                  |  - Header/footer artifact removal  |
                                  |  - Paragraph-aware token chunking  |
                                  |  - Page & Timestamp preservation   |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |  Corpus-Wide Boilerplate Filter    |
                                  |  - Document-frequency clustering   |
                                  |  - Isolates shared case prompts    |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | Dense Vector Indexing (FAISS)      |
                                  |  - all-MiniLM-L6-v2 embeddings     |
                                  |  - Strict self-doc_id exclusion    |
                                  +-----------------+------------------+
                                                    |
                    +-------------------------------+-------------------------------+
                    |                               |                               |
                    v                               v                               v
    +-------------------------------+   +-----------------------+   +-------------------------------+
    | Peer & Cross-Modal Detection  |   | External KB Matching  |   | Multi-Signal AI Estimator     |
    | - Sentence-level alignment    |   | - Public domain texts |   | - RoBERTa supervised detector |
    | - Cosine vs. Jaccard contrast |   | - Wikipedia source URL|   | - GPT-2 token perplexity      |
    | - Video timestamp citations   |   |   attribution         |   | - Sentence burstiness variance|
    +---------------+---------------+   +-----------+-----------+   +---------------+---------------+
                    |                               |                               |
                    +-------------------------------+-------------------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | Multi-Signal Risk Engine & Reports |
                                  |  - Configurable YAML risk logic    |
                                  |  - Structured .json (Audit Schema) |
                                  |  - Human-readable .md (<30s review)|
                                  |  - Pairwise similarity matrix      |
                                  +------------------------------------+
```

---

## Key Capabilities & Scenarios Handled

| Scenario | Challenge | Pipeline Solution | Outcome in Benchmark |
| :--- | :--- | :--- | :--- |
| **Scenario 1: Cross-Modal Duplication** | Candidate reads an exact paragraph from another student's PDF in their MP4 pitch. | Extracts audio via FFmpeg, generates time-aligned transcript via Whisper, indexes chunks, and matches PDF vector space. | Flags exact match with **video timestamp (`00:00:00 - 00:00:31`) and PDF page reference (Page 2)** with 0.97 cosine similarity. |
| **Scenario 2: Paraphrased Content** | Student rewrites content using synonyms to evade naive keyword matching. | Evaluates dense semantic embeddings alongside lexical string metrics (Jaccard, Levenshtein). | Flags **semantic similarity > 0.85** while **lexical Jaccard is low (<0.20)**, explicitly proving semantic evasion. |
| **Scenario 3: Corrupted / Empty Submissions** | Corrupted DOCX, zero-byte PDF, or silent MP4 video submitted. | Non-crashing exception handling, audio stream probing, volume detection, and corrupted file isolation. | Logs warning, flags file as **`⚠️ FLAGGED` (`SKIPPED_EMPTY`, `SKIPPED_SILENT`, `SKIPPED_CORRUPT`)**, and processes all remaining files. |
| **Scenario 4: Benign Common Formatting** | 5 documents share an identical 150-word problem prompt with original analytical answers. | Corpus-level document-frequency filter detects repeated chunks in $\ge 3$ documents and discounts them from plagiarism scoring. | **Zero false-positive alarms**; all 5 documents receive **`🟢 LOW RISK (0.0% Peer Similarity)`**. |
| **Scenario 5: Multi-Document Mixed Batch** | Mixed batch containing genuine, copied, external, and AI-generated text. | End-to-end evaluation with full pairwise matrix generation and structured individual reports. | Processes entire directory, outputs **`summary_matrix.csv`** and **`batch_summary_report.md`**. |

---

## Quickstart & Reproducibility Guide

### 1. Prerequisites
- **Python**: Python 3.10+ (tested on Python 3.10.8).
- **FFmpeg**: Automatically managed via bundled `imageio-ffmpeg` binary (no manual system installation required).

### 2. Single-Command Setup
```bash
# Clone the repository
git clone https://github.com/your-username/unstop-integrity-engine.git
cd unstop-integrity-engine

# Create virtual environment and install pinned dependencies
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

### 3. Pre-Cache Open-Source Models (Offline Ready)
```bash
.\venv\Scripts\python.exe scripts\download_models.py
```
*Pre-caches `sentence-transformers/all-MiniLM-L6-v2`, `openai/whisper-tiny`, `gpt2`, and `roberta-base-openai-detector`.*

### 4. Run the Verification Pipeline
```bash
python run_integrity_check.py --input_dir ./sample_submissions --output_dir ./reports
```

### 5. Run the Automated Benchmark Evaluation
```bash
python evaluate.py
```

### 6. Run the Unit Test Suite
```bash
pytest tests/ -v
```

---

## Output Format & Sample Report Snippet

Each submission generates a machine-readable `.json` audit report adhering strictly to the assessment brief schema, and a human-readable `.md` report designed for rapid (<30s) verification.

### Sample JSON Audit Report (`reports/submission_02_video_pitch.mp4.json`)
```json
{
  "document_id": "submission_02_video_pitch.mp4",
  "total_integrity_risk": "HIGH",
  "scores": {
    "peer_similarity_percentage": 100.0,
    "external_similarity_percentage": 0.0,
    "ai_generated_probability": 26.4
  },
  "peer_matches": [],
  "multimodal_matches": [
    {
      "matched_file": "submission_01_original_fintech.pdf",
      "similarity_score": 0.97,
      "lexical_jaccard": 0.9524,
      "lexical_levenshtein": 0.9433,
      "is_paraphrase": false,
      "query_passage": "Operating margins contracted by 4.2% over the third quarter due to escalated cloud server expenditures and customer verification fees.",
      "matched_passage": "Operating margins contracted by 4.2 percent over the third quarter due to escalated cloud server expenditures and customer verification fees.",
      "location": {
        "query_timestamp": "00:00:00 - 00:00:31",
        "matched_page": 2
      }
    }
  ],
  "explanations": "Critical internal peer similarity detected (100.0% exceeds 50.0% threshold)."
}
```

### Sample Paraphrase Report Snippet (`reports/submission_04_logistics_rewritten.docx.md`)
> ### Overlap #1 — Target: `submission_03_logistics_strategy.docx` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]**
> | Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
> | :---: | :---: | :---: | :---: |
> | **0.87** | **0.18** | **0.49** | Query: Pg 1 ↔ Match: Pg 1 |
> 
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
> - **Query Passage:** *"Active refrigerated enclosures deploying computerized cooling mechanisms ensure temperature consistency during international flight segments..."*
> - **Matched Source:** *"Active refrigeration containers utilizing automated compressor cycles guarantee temperature stability during transcontinental flights..."*

---

## Task 5: 10,000 Document Production Scaling Brief

Processing 10,000 multi-modal submissions (est. 7,000 PDFs, 2,500 DOCXs, 500 MP4 video pitches) within a competitive 2-hour post-deadline evaluation window introduces distinct computational, indexing, and storage challenges. Below is the concrete production engineering blueprint.

### 1. Workload Sizing & Quantitative Bounds
- **Average Document Length**: 8 pages (~2,400 words) $\approx 16$ chunks per document.
- **Corpus Chunk Volume**: $10,000 \text{ submissions} \times 16 \text{ chunks/doc} \approx \mathbf{160,000\text{ to }200,000\text{ dense vectors}}$.
- **Vector Dimension**: 384 dimensions (`all-MiniLM-L6-v2`) in `float32` (1,536 bytes per vector).
- **Raw Vector Footprint**: $200,000 \times 1,536 \text{ bytes} \approx \mathbf{307.2\text{ MB}}$.

### 2. Compute Infrastructure & Distributed Queue Architecture

```
                                  [API Gateway / Submission Uploads]
                                                  |
                                                  v
                                     [Apache Kafka / Redis Streams]
                                                  |
                +---------------------------------+---------------------------------+
                | (Topic: text-ingestion)                                           | (Topic: video-ingestion)
                v                                                                   v
     +--------------------------+                                        +--------------------------+
     | 16x CPU Worker Nodes     |                                        | 4x GPU Worker Nodes      |
     | (c6i.2xlarge - 8 vCPU)   |                                        | (g4dn.xlarge - T4 GPU)   |
     | - PDF / DOCX parsing     |                                        | - FFmpeg audio split     |
     | - Text normalization     |                                        | - Batched Whisper ASR    |
     | - Sentence chunking      |                                        |   (~12x real-time speed) |
     +------------+-------------+                                        +------------+-------------+
                  |                                                                   |
                  +-------------------------------+-----------------------------------+
                                                  |
                                                  v
                                     [Topic: embedding-generation]
                                                  |
                                                  v
                                   +------------------------------+
                                   | 2x Batched Embedding Workers |
                                   | (g4dn.xlarge - TensorRT)     |
                                   | Throughput: 12,000 chunks/sec|
                                   | Full Corpus: ~16.6 seconds   |
                                   +--------------+---------------+
                                                  |
                                                  v
                                   +------------------------------+
                                   | Distributed Vector Index     |
                                   | (Qdrant / FAISS HNSW-Flat)   |
                                   | RAM: ~480 MB | P99 Query: 4ms|
                                   +------------------------------+
```

### 3. Whisper ASR Bottleneck Resolution
- **The Bottleneck**: Whisper ASR on CPU takes $\approx 0.8\times$ real-time latency (a 30s video takes ~24s on an 8-core CPU). Processing 500 videos sequentially on CPU would take 3.3 hours.
- **Production Solution**:
  1. Route all video files to a dedicated GPU worker queue (`celery -Q gpu_whisper_workers`).
  2. Deploy `faster-whisper` (CTranslate2 INT8 quantized backend). On an NVIDIA T4 GPU, transcription operates at $\mathbf{14\times\text{ faster than real-time}}$ (~2.1 seconds per 30-second video).
  3. Four T4 GPU workers process all 500 video submissions concurrently in under **4.5 minutes**.

### 4. Vector Database Selection: Flat vs. HNSW vs. IVF-PQ

| Parameter | FAISS IndexFlatIP | FAISS IndexHNSWFlat (Recommended) | FAISS IndexIVFPQ |
| :--- | :---: | :---: | :---: |
| **Search Time** | $O(N \cdot d)$ (Linear Scan) | $O(\log N \cdot d)$ (Graph Navigation) | $O(\frac{N}{C} \cdot d_{quant})$ |
| **Query Latency (200k chunks)** | ~18 ms | **~1.8 ms** | ~0.6 ms |
| **Memory Footprint** | 307 MB | **480 MB** (Graph adjacency overhead) | 38 MB (Compressed) |
| **Recall@10** | 100.0% (Exact) | **99.4%** | 94.2% |
| **Dynamic Insertion** | Instant append | Fast incremental add | Requires offline centroid training |

**Production Recommendation**: Deploy **`FAISS IndexHNSWFlat`** (or a managed Qdrant instance with HNSW indexing). 480 MB easily fits in memory on any cloud instance, while sub-2ms query latency allows all 200,000 pairwise chunk queries to execute in under **6 minutes**.

### 5. Multi-Stage Filtering: LSH / MinHash Pre-Filter
To avoid conducting 200,000 dense neural searches for trivial verbatim copies:
1. **LSH (Locality Sensitive Hashing) / MinHash**: Compute 128 MinHash permutations per document during ingestion ($O(1)$ lookup time).
2. Any document pair exhibiting $\text{Jaccard} \ge 0.90$ is immediately flagged as a direct copy without vector search, shedding **~30% of vector query load**.
3. Dense embeddings are reserved for paraphrased and cross-modal semantic matching.

### 6. Production Cost & Throughput Summary
- **Compute Provisioning**: 4x `g4dn.xlarge` spot GPU instances (\$0.157/hr) + 8x `c6i.2xlarge` spot CPU instances (\$0.102/hr).
- **Total Pipeline Execution Latency**: **~38 minutes** for 10,000 multi-modal submissions.
- **Estimated Cloud Compute Cost**: **~\$1.28** per 10,000 submissions evaluated.

---

## Repository Structure

```
unstop-integrity-engine/
├── config.yaml                    # Centralized thresholds, model names, and risk criteria
├── requirements.txt               # Pinned production dependencies
├── Makefile                       # One-command developer shortcuts (setup, test, run)
├── run.bat                        # Windows execution runner script
├── run_integrity_check.py         # Main CLI pipeline entrypoint
├── evaluate.py                    # Empirical evaluation benchmark against ground truth
├── EVALUATION.md                  # Detailed metrics, confusion matrix & failure analysis
├── README.md                      # Architecture brief & 10,000 doc scaling plan
├── scripts/
│   ├── download_models.py         # Offline model pre-caching utility
│   └── generate_synthetic_dataset.py # Generates 15 test submissions + ground truth manifest
├── src/
│   ├── extractors/
│   │   ├── base_extractor.py      # Abstract interface & data classes (PageContent, AudioSegment)
│   │   ├── pdf_extractor.py       # pypdf text extraction with page tracking
│   │   ├── docx_extractor.py      # python-docx structural paragraph extraction
│   │   ├── video_extractor.py     # Transformers Whisper ASR with audio stream verification
│   │   └── dispatcher.py          # Modality-aware routing dispatcher
│   ├── normalizer/
│   │   ├── normalizer.py          # Header/footer cleaner & sentence tokenizer
│   │   └── chunker.py             # Paragraph-aware sliding-window chunker
│   ├── filters/
│   │   └── boilerplate_filter.py  # Corpus document-frequency template discounting (Scenario 4)
│   ├── indexer/
│   │   └── vector_indexer.py      # SentenceTransformers & FAISS index with self-doc_id exclusion
│   ├── detectors/
│   │   ├── peer_detector.py       # Coverage-based peer & cross-modal similarity scorer
│   │   ├── external_detector.py   # External knowledge base plagiarism matcher
│   │   ├── ai_detector.py         # RoBERTa + GPT-2 perplexity + burstiness estimator
│   │   └── risk_calculator.py     # Multi-signal risk decision mapping (LOW/MEDIUM/HIGH)
│   ├── reporter/
│   │   ├── json_reporter.py       # Brief-compliant JSON report generator
│   │   ├── markdown_reporter.py   # Rapid-review (<30s) Markdown audit generator
│   │   └── batch_summary.py       # Pairwise similarity matrix & summary report
│   └── utils/
│       ├── config_loader.py       # YAML configuration reader
│       ├── ffmpeg_setup.py        # Bundled FFmpeg path discovery & validation
│       └── text_metrics.py        # Jaccard, Levenshtein, and timestamp formatters
├── tests/
│   └── test_pipeline.py           # Pytest unit test suite covering all scenarios
├── external_kb/                   # Public domain reference texts with source URLs
│   ├── sources_manifest.json
│   ├── fintech_market_entry.txt
│   ├── cold_chain_logistics.txt
│   ├── renewable_microgrids.txt
│   ├── e_commerce_retention.txt
│   └── circular_packaging.txt
├── sample_submissions/            # 15 synthetic multi-modal test files
│   ├── dataset_manifest.json      # Ground truth metadata and relationships
│   ├── submission_01_original_fintech.pdf
│   ├── submission_02_video_pitch.mp4
│   ├── ...
│   └── submission_15_genuine_original.pdf
└── reports/                       # Generated audit reports & pairwise summary matrix
    ├── batch_summary_report.md
    ├── summary_matrix.csv
    ├── submission_01_original_fintech.pdf.json
    ├── submission_01_original_fintech.pdf.md
    └── ...
```

---

## Assumptions

1. **Submission Metadata**: File names are unique within a competition cohort and act as immutable submission identifiers (`doc_id`).
2. **Audio Language**: Spoken pitches are delivered in English (Whisper `language='en'` enforced).
3. **Hardware Independence**: The prototype defaults to CPU execution to ensure deterministic reproducibility on standard commodity workstations without requiring local CUDA GPU configuration.
4. **AI Generation Policy**: Consistent with emerging academic and testing integrity standards, AI-generation confidence alone is treated as a probabilistic indicator and is strictly prohibited from triggering an administrative `HIGH` risk escalation without corroborating peer or external similarity evidence.
5. **Boilerplate Scope**: Reusable institutional text (e.g. competition problem prompts, case background headers) is expected to recur across $\ge 3$ independent candidate submissions.

---

## AI Coding Assistants Disclosure

In accordance with Section 10 of the assessment brief:
- **Assistant Used**: Antigravity (Powered by Google DeepMind Gemini 3.8).
- **Scope of Usage**:
  - Accelerated modular boilerplate generation (standardizing dataclass representations and regex string parsers).
  - Rapid debugging of Windows OS Application Control DLL blocking for C-extensions by migrating from native Whisper to Hugging Face Transformers Whisper.
  - Synthesis of mock case study narratives and public domain topic texts for synthetic benchmark evaluation.
- **Architectural Authorship**: All system architecture, vector indexing design, chunking algorithms, document-frequency template suppression logic, and empirical evaluation benchmarking were authored and validated specifically for this assessment.
