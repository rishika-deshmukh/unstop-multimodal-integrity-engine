"""
Synthetic Multi-Modal Dataset Generation Script.
Constructs 15 sample submissions across PDF, DOCX, and MP4 modalities
incorporating embedded ground-truth relationships matching all 5 evaluation scenarios:
- Scenario 1: Cross-modal PDF to MP4 spoken duplication
- Scenario 2: Paraphrased synonym-swapped DOCX content
- Scenario 3: Corrupt DOCX, 0-byte PDF, and silent MP4 video
- Scenario 4: Five documents sharing an identical 150-word problem prompt header
- Scenario 5: Mixed stress batch including AI-generated text, external plagiarism, and original controls
Also generates dataset_manifest.json with complete pairwise ground truth labels.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import subprocess
import logging
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pyttsx3
from src.utils.ffmpeg_setup import ensure_ffmpeg_available

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dataset_generator")

PROMPT_HEADER_150_WORDS = (
    "Case Study Challenge Brief 2026: Sustainable Urban Mobility Infrastructure. "
    "Teams are required to evaluate the capital deployment feasibility and regulatory constraints "
    "of transitioning municipal transit networks to zero-emission battery electric bus fleets across "
    "Tier-1 metropolitan areas. Address total cost of ownership including depot charging infrastructure, "
    "grid interconnect upgrade timelines, lithium iron phosphate battery lifecycle degradation under "
    "extreme ambient thermal conditions, and route schedule optimization. Submissions must provide "
    "rigorous financial models and operational risk mitigation frameworks for municipal transport authorities."
)

CROSS_MODAL_PARAGRAPH = (
    "The core competitive advantage relies on vertical integration of credit underwriting models "
    "with real-time transactional payment gateways. Operating margins contracted by 4.2 percent "
    "over the third quarter due to escalated cloud server expenditures and customer verification fees. "
    "However, automating digital identity checks reduced loan disbursement latency from forty-eight hours "
    "down to under ninety seconds, boosting borrower conversion rates across high-frequency consumer loan segments."
)

def create_pdf(path: Path, pages: list[list[str]]):
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontSize = 11
    normal.leading = 16

    story = []
    for p_idx, page_paragraphs in enumerate(pages):
        if p_idx > 0:
            story.append(PageBreak())
        for text in page_paragraphs:
            story.append(Paragraph(text, normal))
            story.append(Spacer(1, 14))

    doc.build(story)

def create_docx(path: Path, paragraphs: list[str]):
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    doc.save(str(path))

def create_mp4_with_audio(output_mp4: Path, speech_text: str):
    ffmpeg_bin = ensure_ffmpeg_available()
    temp_wav = output_mp4.parent / f"{output_mp4.stem}_temp.wav"
    
    # 1. Synthesize TTS speech
    logger.info(f"Synthesizing audio for {output_mp4.name} via pyttsx3...")
    engine = pyttsx3.init()
    engine.setProperty("rate", 155)
    engine.save_to_file(speech_text, str(temp_wav))
    engine.runAndWait()

    # 2. Combine with a solid color video frame using ffmpeg
    logger.info(f"Muxing video and audio into {output_mp4.name}...")
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "lavfi", "-i", "color=c=navy:s=640x360:r=24",
        "-i", str(temp_wav),
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_mp4)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if temp_wav.exists():
        temp_wav.unlink()

def create_silent_mp4(output_mp4: Path):
    ffmpeg_bin = ensure_ffmpeg_available()
    logger.info(f"Generating silent MP4 video: {output_mp4.name}...")
    # 5-second video with no audio stream
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "lavfi", "-i", "color=c=black:s=320x240:r=24:d=5",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(output_mp4)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def generate_dataset(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "dataset_name": "Unstop Multimodal Integrity Benchmark Dataset",
        "total_documents": 15,
        "scenarios_covered": [
            "Scenario 1: Cross-Modal Duplication (PDF to MP4 spoken overlap)",
            "Scenario 2: Paraphrased Content (Semantic vs Lexical disparity in DOCX)",
            "Scenario 3: Corrupted / Empty Submissions (0-byte PDF, silent MP4, corrupt DOCX)",
            "Scenario 4: Benign Common Formatting / Judgment Test (5 docs with identical 150-word prompt)",
            "Scenario 5: Multi-Document Mixed Evaluation (Genuine, Copied, External, and AI-generated)"
        ],
        "documents": {},
        "pairwise_ground_truth": []
    }

    # 1. submission_01_original_fintech.pdf (Scenario 1 Target)
    p1 = output_dir / "submission_01_original_fintech.pdf"
    create_pdf(p1, [
        [
            "<b>Digital Banking Infrastructure and Microfinance Expansion</b>",
            "Executive Summary: Modern digital credit infrastructure enables instantaneous risk assessment for underserved consumer segments by ingesting alternative transactional data streams including utility bill remittances and mobile airtime top-ups.",
            "This report outlines the operational architecture for high-velocity consumer micro-lending in high-density urban corridors."
        ],
        [
            "<b>Section 2: Unit Economics and Credit Underwriting</b>",
            CROSS_MODAL_PARAGRAPH,
            "Scalability hinges upon maintaining loss reserves beneath four percent of cumulative gross loan portfolio volume."
        ]
    ])
    manifest["documents"]["submission_01_original_fintech.pdf"] = {
        "modality": "pdf",
        "type": "original_target",
        "description": "Original fintech report containing key operational paragraph on Page 2."
    }

    # 2. submission_02_video_pitch.mp4 (Scenario 1 Cross-Modal Match)
    p2 = output_dir / "submission_02_video_pitch.mp4"
    create_mp4_with_audio(p2, CROSS_MODAL_PARAGRAPH)
    manifest["documents"]["submission_02_video_pitch.mp4"] = {
        "modality": "mp4",
        "type": "cross_modal_copy",
        "description": "Short pitch video where candidate verbatim recites Page 2 of submission_01."
    }
    manifest["pairwise_ground_truth"].append({
        "query_doc": "submission_02_video_pitch.mp4",
        "target_doc": "submission_01_original_fintech.pdf",
        "relationship": "cross_modal_duplication",
        "expected_score_range": ">= 0.85",
        "expected_risk": "HIGH"
    })

    # 3. submission_03_logistics_strategy.docx (Scenario 2 Target)
    p3 = output_dir / "submission_03_logistics_strategy.docx"
    create_docx(p3, [
        "Cold Chain Logistics and Temperature Assurance Strategy",
        "Establishing a resilient pharmaceutical cold chain requires continuous thermal monitoring between two and eight degrees Celsius across all intermediate warehouse hubs. Active refrigeration containers utilizing automated compressor cycles guarantee temperature stability during transcontinental flights, whereas passive thermal shippers rely on vacuum-insulated panels to protect vaccines during domestic road haulage.",
        "Real-time sensor telemetry triggers automated rerouting protocols whenever ambient temperature excursions exceed regulatory tolerance thresholds."
    ])
    manifest["documents"]["submission_03_logistics_strategy.docx"] = {
        "modality": "docx",
        "type": "original_target",
        "description": "Logistics analysis describing active and passive cold chain mechanics."
    }

    # 4. submission_04_logistics_rewritten.docx (Scenario 2 Paraphrased Match)
    p4 = output_dir / "submission_04_logistics_rewritten.docx"
    create_docx(p4, [
        "Strategic Temperature Assurance Framework for Pharmaceutical Transit",
        "Constructing a dependable pharmaceutical thermal supply line demands nonstop temperature tracking between two and eight degrees Celsius across every midpoint depot location. Active refrigerated enclosures deploying computerized cooling mechanisms ensure temperature consistency during international flight segments, while passive temperature-safe boxes depend on vacuum-insulated panels to safeguard vaccine vials throughout ground truck transport.",
        "Live sensor tracking activates dynamic path adjustments whenever surrounding warmth changes surpass government compliance criteria."
    ])
    manifest["documents"]["submission_04_logistics_rewritten.docx"] = {
        "modality": "docx",
        "type": "paraphrased_copy",
        "description": "Paraphrased version of submission_03 using synonyms to evade string matching."
    }
    manifest["pairwise_ground_truth"].append({
        "query_doc": "submission_04_logistics_rewritten.docx",
        "target_doc": "submission_03_logistics_strategy.docx",
        "relationship": "paraphrase_duplication",
        "expected_semantic_cosine": ">= 0.80",
        "expected_lexical_jaccard": "<= 0.35",
        "expected_risk": "HIGH"
    })

    # 5. submission_05_corrupt_empty.pdf (Scenario 3)
    p5 = output_dir / "submission_05_corrupt_empty.pdf"
    p5.write_bytes(b"") # 0-byte file
    manifest["documents"]["submission_05_corrupt_empty.pdf"] = {
        "modality": "pdf",
        "type": "degraded_empty",
        "description": "Zero-byte PDF file to test graceful empty submission handling."
    }

    # 6. submission_06_silent_video.mp4 (Scenario 3)
    p6 = output_dir / "submission_06_silent_video.mp4"
    create_silent_mp4(p6)
    manifest["documents"]["submission_06_silent_video.mp4"] = {
        "modality": "mp4",
        "type": "degraded_silent",
        "description": "Silent MP4 video with no audio track to test ASR error handling."
    }

    # 7. submission_07_corrupted.docx (Scenario 3)
    p7 = output_dir / "submission_07_corrupted.docx"
    p7.write_bytes(b"\x00\xFF\xAA\xBB\xCC\xDDMALFORMED_DOCX_STREAM_CORRUPT")
    manifest["documents"]["submission_07_corrupted.docx"] = {
        "modality": "docx",
        "type": "degraded_corrupt",
        "description": "Corrupted non-zip DOCX file to test parser exception recovery."
    }

    # 8-12: Scenario 4 (Five documents sharing identical 150-word prompt header)
    ev_answers = [
        ("submission_08_ev_bus_depot_analysis.pdf", "pdf", [
            PROMPT_HEADER_150_WORDS,
            "Municipal Bus Depot Megawatt-Scale Fast Charging Interconnect Architecture:",
            "Our analysis prioritizes 350-kilowatt direct current fast chargers configured in sequential overhead pantograph layouts at central bus garages. Utility tariff negotiations must establish dedicated industrial sub-stations to minimize coincident peak demand surcharges during evening replenishment windows."
        ]),
        ("submission_09_ev_battery_lifecycle.docx", "docx", [
            PROMPT_HEADER_150_WORDS,
            "Lithium Iron Phosphate Battery Thermal Degradation Dynamics:",
            "Operating heavy-duty electric buses in sub-tropical climates requires active liquid thermal management loops to maintain cell temperatures below thirty-five degrees Celsius. Solid-electrolyte interphase layer growth is mitigated through restricted state-of-charge operating windows between twenty and eighty percent."
        ]),
        ("submission_10_ev_municipal_finance.pdf", "pdf", [
            PROMPT_HEADER_150_WORDS,
            "Green Municipal Bond Structuring for Transit Fleet Electrification:",
            "Capital expenditures for six hundred electric transit buses are amortized through twenty-year municipal green revenue bonds supported by dedicated state tax credits. Carbon offset monetizations generate additional revenue buffers to service senior tranche coupon payments."
        ]),
        ("submission_11_ev_route_telemetry.docx", "docx", [
            PROMPT_HEADER_150_WORDS,
            "Dynamic Route Telemetry and Regenerative Braking Optimization:",
            "Empirical telemetry from urban bus routes demonstrates that regenerative braking captures up to twenty-eight percent of kinetic braking energy along hilly topographical gradients. Route scheduling algorithms optimize fleet deployment based on real-time kilowatt-hour consumption per passenger kilometer."
        ]),
        ("submission_12_ev_grid_load_balancing.pdf", "pdf", [
            PROMPT_HEADER_150_WORDS,
            "Grid Integration and Depot Solar Microgrid Peak-Shaving:",
            "Co-locating two-megawatt rooftop solar photovoltaic arrays with containerized lithium battery stationary storage at municipal bus depots cushions localized substation transformers from sudden transformer thermal overloading during synchronous late-night depot recharging."
        ])
    ]

    for fname, modality, paras in ev_answers:
        path = output_dir / fname
        if modality == "pdf":
            create_pdf(path, [paras])
        else:
            create_docx(path, paras)
        manifest["documents"][fname] = {
            "modality": modality,
            "type": "benign_common_template",
            "description": "Contains identical 150-word prompt header with unique analytical solution.",
            "expected_risk": "LOW" # MUST NOT be marked HIGH
        }

    # 13. submission_13_ai_generated_essay.docx (Scenario 5 AI test)
    p13 = output_dir / "submission_13_ai_generated_essay.docx"
    create_docx(p13, [
        "Synthesizing Paradigms of Sustainable Organizational Leadership in the Modern Era",
        "In the contemporary landscape of global commerce, the imperative to foster synergistic organizational frameworks has emerged as a cornerstone of sustainable enterprise growth. Delving into the multifaceted dimensions of strategic alignment, one observes that visionary leaders must cultivate holistic ecosystems that effortlessly bridge disparate stakeholder expectations.",
        "Furthermore, by championing agile methodologies and navigating dynamic market complexities with resilience, modern enterprises empower cross-functional cohorts to achieve unprecedented efficiencies. In conclusion, the harmonized integration of proactive innovation and disciplined governance creates an enduring foundation for long-term value creation."
    ])
    manifest["documents"]["submission_13_ai_generated_essay.docx"] = {
        "modality": "docx",
        "type": "ai_generated_synthetic",
        "description": "Synthesized essay exhibiting LLM sentence cadence, low perplexity, and low burstiness.",
        "expected_ai_prob": ">= 75.0%",
        "expected_risk": "MEDIUM" # AI alone should trigger MEDIUM, never HIGH
    }

    # 14. submission_14_external_plagiarism.pdf (Scenario 5 External plagiarism test)
    p14 = output_dir / "submission_14_external_plagiarism.pdf"
    create_pdf(p14, [
        [
            "<b>Packaging Sustainability in Consumer Products</b>",
            "Introduction: Modern retail operations are experiencing mounting pressure to eliminate non-recyclable solid waste from global distribution chains.",
            "Transitioning fast-moving consumer goods to circular packaging frameworks requires substituting virgin petroleum polymers with post-consumer recycled polyethylene terephthalate and industrially compostable polyhydroxyalkanoates. Achieving mechanical recyclability without sacrificing barrier properties against moisture and oxygen ingress represents a critical chemical engineering challenge. Successful circular supply loops require closed-loop reverse collection incentives, automated near-infrared optical flake sorting, and decontamination extrusion technologies to meet food-grade contact safety regulations."
        ]
    ])
    manifest["documents"]["submission_14_external_plagiarism.pdf"] = {
        "modality": "pdf",
        "type": "external_copy",
        "description": "Submission directly plagiarized from external knowledge base circular packaging article.",
        "expected_external_score": ">= 40.0%",
        "expected_risk": "HIGH"
    }

    # 15. submission_15_genuine_original.pdf (Scenario 5 Hard negative original control)
    p15 = output_dir / "submission_15_genuine_original.pdf"
    create_pdf(p15, [
        [
            "<b>Neutral-Atom Quantum Computing Architecture for Cryptographic Simulation</b>",
            "Neutral-atom quantum processors exploit optical tweezer arrays to trap individual rubidium and ytterbium atoms within ultra-high vacuum chambers. Two-qubit gate operations are mediated via laser excitation to high-lying Rydberg states, providing strong, switchable dipole-dipole interactions with high physical fidelity.",
            "Our research constructs an error-mitigated quantum simulation circuit to benchmark surface code lattice thresholds against coherent laser phase noise and spontaneous atomic emission events."
        ]
    ])
    manifest["documents"]["submission_15_genuine_original.pdf"] = {
        "modality": "pdf",
        "type": "genuine_original_control",
        "description": "100% original human-authored academic paper on quantum physics to verify zero false positives.",
        "expected_risk": "LOW"
    }

    # Save manifest
    manifest_path = output_dir / "dataset_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Synthetic dataset of 15 documents and dataset_manifest.json generated successfully in {output_dir}.")

if __name__ == "__main__":
    generate_dataset(Path("./sample_submissions"))
