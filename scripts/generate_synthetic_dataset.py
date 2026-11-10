"""
Synthetic Multi-Modal Dataset Generation Script.
Constructs 18 sample submissions across PDF, DOCX, and MP4 modalities
incorporating embedded ground-truth relationships matching all 5 evaluation scenarios:
- Scenario 1: Cross-modal PDF to MP4 spoken duplication
- Scenario 2: Paraphrased synonym-swapped DOCX content
- Scenario 3: Corrupt DOCX, 0-byte PDF, and silent MP4 video
- Scenario 4: Five documents sharing an identical 150-word problem prompt header
- Scenario 5: Multi-document mixed batch including exact copies, 2 LLM-generated docs (ChatGPT & Claude),
  2 hard negative human originals on similar topics, and external knowledge base plagiarism.
Generates an exhaustive pairwise dataset_manifest.json with explicit labels for every pair.
"""

import os
import sys
import json
import itertools
import subprocess
import logging
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
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

PARAPHRASED_CROSS_MODAL_TEXT = (
    "Digital microfinance providers in emerging economies utilize algorithmic credit scoring trained on "
    "alternative consumer signals, including telecom payment regularity and point-of-sale transaction records. "
    "Portfolio risk management improves as automated loan decisions lower default rates among uncollateralized lending segments."
)

FINTECH_REPORT_P1 = (
    "Digital Banking Infrastructure and Microfinance Expansion. "
    "Modern digital credit infrastructure enables instantaneous risk assessment for underserved consumer segments "
    "by ingesting alternative transactional data streams including utility bill remittances and mobile airtime top-ups. "
    "This report outlines the operational architecture for high-velocity consumer micro-lending in high-density urban corridors."
)

def create_pdf(path: Path, pages: list[list[str]]):
    doc = SimpleDocTemplate(str(path.resolve()), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontSize = 11
    normal.leading = 16

    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        if os.path.exists("C:/Windows/Fonts/arial.ttf"):
            pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
            normal.fontName = "Arial"
    except Exception:
        pass

    story = []
    for p_idx, page_paragraphs in enumerate(pages):
        if p_idx > 0:
            story.append(PageBreak())
        for text in page_paragraphs:
            formatted_text = text.replace("\n", "<br/>")
            story.append(Paragraph(formatted_text, normal))
            story.append(Spacer(1, 14))

    doc.build(story)

def create_docx(path: Path, paragraphs: list[str]):
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    doc.save(str(path))

def create_mp4_with_audio(output_mp4: Path, speech_text: str, speech_rate: int = 185):
    ffmpeg_bin = ensure_ffmpeg_available()
    temp_wav = output_mp4.parent / f"{output_mp4.stem}_temp.wav"

    logger.info(f"Synthesizing audio for {output_mp4.name} via pyttsx3 (rate={speech_rate})...")
    engine = pyttsx3.init()
    engine.setProperty("rate", speech_rate)
    engine.save_to_file(speech_text, str(temp_wav))
    engine.runAndWait()

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

    documents_meta = {}

    # 1. submission_01_fintech_report.pdf (Original PDF Target)
    p1 = output_dir / "submission_01_fintech_report.pdf"
    create_pdf(p1, [
        [FINTECH_REPORT_P1],
        [
            "Section 2: Unit Economics and Credit Underwriting.",
            CROSS_MODAL_PARAGRAPH,
            "Scalability hinges upon maintaining loss reserves beneath four percent of cumulative gross loan portfolio volume."
        ]
    ])
    documents_meta["submission_01_fintech_report.pdf"] = {
        "modality": "pdf",
        "type": "original_target",
        "is_degraded": False,
        "is_ai": False,
        "description": "Synthetic (script-generated) fintech microfinance report containing key operational underwriting section on Page 2."
    }

    # 2. submission_02_video_pitch.mp4 (Cross-Modal match with sub_01)
    p2 = output_dir / "submission_02_video_pitch.mp4"
    create_mp4_with_audio(p2, CROSS_MODAL_PARAGRAPH)
    documents_meta["submission_02_video_pitch.mp4"] = {
        "modality": "mp4",
        "type": "cross_modal_copy",
        "is_degraded": False,
        "is_ai": False,
        "description": "Candidate video pitch reading aloud the underwriting paragraph from submission_01."
    }

    # 3. submission_03_logistics_strategy.docx (Original DOCX)
    p3 = output_dir / "submission_03_logistics_strategy.docx"
    create_docx(p3, [
        "Cold Chain Logistics and Temperature Assurance Strategy",
        "Establishing a resilient pharmaceutical cold chain requires continuous thermal monitoring between two and eight degrees Celsius across all intermediate warehouse hubs. Active refrigeration containers utilizing automated compressor cycles guarantee temperature stability during transcontinental flights, whereas passive thermal shippers rely on vacuum-insulated panels to protect vaccines during domestic road haulage.",
        "Real-time sensor telemetry triggers automated rerouting protocols whenever ambient temperature excursions exceed regulatory tolerance thresholds."
    ])
    documents_meta["submission_03_logistics_strategy.docx"] = {
        "modality": "docx",
        "type": "original_target",
        "is_degraded": False,
        "is_ai": False,
        "description": "Synthetic (script-generated) logistics strategy describing active and passive cold chain mechanics."
    }

    # 4. submission_04_logistics_rewritten.docx (Paraphrased copy of sub_03)
    p4 = output_dir / "submission_04_logistics_rewritten.docx"
    create_docx(p4, [
        "Strategic Temperature Assurance Framework for Pharmaceutical Transit",
        "Constructing a dependable pharmaceutical thermal supply line demands nonstop temperature tracking between two and eight degrees Celsius across every midpoint depot location. Active refrigerated enclosures deploying computerized cooling mechanisms ensure temperature consistency during international flight segments, while passive temperature-safe boxes depend on vacuum-insulated panels to safeguard vaccine vials throughout ground truck transport.",
        "Live sensor tracking activates dynamic path adjustments whenever surrounding warmth changes surpass government compliance criteria."
    ])
    documents_meta["submission_04_logistics_rewritten.docx"] = {
        "modality": "docx",
        "type": "paraphrased_copy",
        "is_degraded": False,
        "is_ai": False,
        "description": "Synthetic (script-generated) paraphrased copy of submission_03 using synonyms to evade string matching."
    }

    # 5. submission_05_logistics_exact_copy.pdf (Exact Copy of sub_03 in PDF format: Requirement 4)
    p5 = output_dir / "submission_05_logistics_exact_copy.pdf"
    create_pdf(p5, [
        [
            "Cold Chain Logistics and Temperature Assurance Strategy",
            "Establishing a resilient pharmaceutical cold chain requires continuous thermal monitoring between two and eight degrees Celsius across all intermediate warehouse hubs. Active refrigeration containers utilizing automated compressor cycles guarantee temperature stability during transcontinental flights, whereas passive thermal shippers rely on vacuum-insulated panels to protect vaccines during domestic road haulage.",
            "Real-time sensor telemetry triggers automated rerouting protocols whenever ambient temperature excursions exceed regulatory tolerance thresholds."
        ]
    ])
    documents_meta["submission_05_logistics_exact_copy.pdf"] = {
        "modality": "pdf",
        "type": "exact_copy",
        "is_degraded": False,
        "is_ai": False,
        "description": "Synthetic (script-generated) cross-format exact copy of submission_03_logistics_strategy.docx in PDF format."
    }

    # 6. submission_06_corrupt_empty.pdf (Degraded empty: Requirement 3)
    p6 = output_dir / "submission_06_corrupt_empty.pdf"
    p6.write_bytes(b"")
    documents_meta["submission_06_corrupt_empty.pdf"] = {
        "modality": "pdf",
        "type": "degraded_empty",
        "is_degraded": True,
        "is_ai": False,
        "expected_status": "SKIPPED_EMPTY",
        "description": "Zero-byte empty PDF submission to test non-crashing status handling."
    }

    # 7. submission_07_silent_video.mp4 (Degraded silent: Requirement 3)
    p7 = output_dir / "submission_07_silent_video.mp4"
    create_silent_mp4(p7)
    documents_meta["submission_07_silent_video.mp4"] = {
        "modality": "mp4",
        "type": "degraded_silent",
        "is_degraded": True,
        "is_ai": False,
        "expected_status": "SKIPPED_SILENT",
        "description": "Silent MP4 video with no audible audio track."
    }

    # 8. submission_08_corrupted.docx (Degraded corrupt: Requirement 3)
    p8 = output_dir / "submission_08_corrupted.docx"
    p8.write_bytes(b"\x00\xFF\xAA\xBB\xCC\xDDMALFORMED_NON_ZIP_STREAM")
    documents_meta["submission_08_corrupted.docx"] = {
        "modality": "docx",
        "type": "degraded_corrupt",
        "is_degraded": True,
        "is_ai": False,
        "expected_status": "SKIPPED_CORRUPT",
        "description": "Malformed corrupt binary file simulating upload corruption."
    }

    # 9-13. Scenario 4 (Five documents sharing 150-word prompt header with unique answers)
    ev_docs = [
        ("submission_09_ev_depot_charging.pdf", "pdf", [
            [
                PROMPT_HEADER_150_WORDS,
                "Municipal Bus Depot Megawatt-Scale Fast Charging Interconnect Architecture.",
                "Our analysis prioritizes 350-kilowatt direct current fast chargers configured in sequential overhead pantograph layouts at central bus garages. Utility tariff negotiations must establish dedicated industrial sub-stations to minimize coincident peak demand surcharges during evening replenishment windows."
            ]
        ]),
        ("submission_10_ev_battery_degradation.docx", "docx", [
            PROMPT_HEADER_150_WORDS,
            "Lithium Iron Phosphate Battery Thermal Degradation Dynamics.",
            "Operating heavy-duty electric buses in sub-tropical climates requires active liquid thermal management loops to maintain cell temperatures below thirty-five degrees Celsius. Solid-electrolyte interphase layer growth is mitigated through restricted state-of-charge operating windows between twenty and eighty percent."
        ]),
        ("submission_11_ev_municipal_debt.pdf", "pdf", [
            [
                PROMPT_HEADER_150_WORDS,
                "Green Municipal Bond Structuring for Transit Fleet Electrification.",
                "Capital expenditures for six hundred electric transit buses are amortized through twenty-year municipal green revenue bonds supported by dedicated state tax credits. Carbon offset monetizations generate additional revenue buffers to service senior tranche coupon payments."
            ]
        ]),
        ("submission_12_ev_route_energy.docx", "docx", [
            PROMPT_HEADER_150_WORDS,
            "Dynamic Route Telemetry and Regenerative Braking Optimization.",
            "Empirical telemetry from urban bus routes demonstrates that regenerative braking captures up to twenty-eight percent of kinetic braking energy along hilly topographical gradients. Route scheduling algorithms optimize fleet deployment based on real-time kilowatt-hour consumption per passenger kilometer."
        ]),
        ("submission_13_ev_grid_balancing.pdf", "pdf", [
            [
                PROMPT_HEADER_150_WORDS,
                "Grid Integration and Depot Solar Microgrid Peak-Shaving.",
                "Co-locating two-megawatt rooftop solar photovoltaic arrays with containerized lithium battery stationary storage at municipal bus depots cushions localized substation transformers from sudden thermal overloading during synchronous late-night depot recharging."
            ]
        ])
    ]

    for fname, modality, content in ev_docs:
        path = output_dir / fname
        if modality == "pdf":
            create_pdf(path, content)
        else:
            create_docx(path, content)
        documents_meta[fname] = {
            "modality": modality,
            "type": "benign_common_template",
            "is_degraded": False,
            "is_ai": False,
            "description": "Case study containing the shared 150-word competition prompt with original analysis."
        }

    # 14. submission_14_llm_generated_essay.docx (LLM Sample #1: Synthesized by Antigravity)
    p14 = output_dir / "submission_14_llm_generated_essay.docx"
    create_docx(p14, [
        "Business Case Analysis: EV Bus Fleet Charging Costs",
        "The transition from diesel-powered buses to electric vehicle (EV) buses presents a significant opportunity for public transportation operators to reduce operating costs, improve energy efficiency, and achieve sustainability targets. However, the financial viability of an EV bus fleet depends heavily on charging costs, electricity tariffs, infrastructure investment, and fleet utilisation.",
        "1. Cost Structure and Financial Considerations",
        "The primary advantage of EV buses is their lower energy cost compared to diesel consumption. While diesel buses incur recurring fuel expenses, EV buses rely on electricity, which is generally cheaper per kilometre. For example, assuming an EV bus consumes 1.2 kWh per kilometre and electricity costs ₹8 per kWh, the energy cost is approximately ₹9.60 per kilometre. In comparison, a diesel bus consuming 0.35 litres per kilometre at ₹90 per litre incurs a fuel cost of ₹31.50 per kilometre.",
        "However, electricity costs vary depending on charging schedules, commercial tariffs, demand charges, and peak-hour pricing. Therefore, operators must evaluate the total cost of electricity rather than relying solely on the per-unit tariff.",
        "2. Charging Infrastructure Investment",
        "Establishing an EV bus charging network requires substantial initial investment. Costs include installing charging stations, upgrading electrical connections, transformers, power distribution systems, and battery management infrastructure. Depot-based charging is generally more economical for fleets with predictable operating schedules, while opportunity charging may be necessary for longer routes.",
        "Operators must balance infrastructure investment against expected long-term savings. Poorly planned charging infrastructure can increase operational expenses and reduce fleet availability.",
        "3. Strategies to Optimise Charging Costs",
        "Several strategies can improve financial efficiency:\n- Off-peak charging: Schedule charging during low-tariff periods to reduce electricity expenses.\n- Smart charging: Use software to distribute charging loads and avoid unnecessary peak-demand charges.\n- Renewable energy: Integrate rooftop solar or renewable electricity procurement to reduce grid dependency.\n- Battery optimisation: Monitor battery health and charging cycles to minimise degradation and replacement costs.\n- Fleet scheduling: Align charging schedules with bus routes, operational hours, and battery requirements.",
        "4. Financial Viability and Business Impact",
        "Although EV buses involve higher upfront acquisition and infrastructure costs, their lower energy and maintenance expenses can generate substantial long-term savings. A detailed Total Cost of Ownership (TCO) analysis should consider vehicle purchase price, electricity, charging infrastructure, maintenance, battery replacement, financing, and government incentives.",
        "Conclusion",
        "EV bus fleet electrification is a financially promising investment when supported by efficient charging infrastructure and intelligent energy management. Transportation operators should adopt phased electrification, optimise charging schedules, and evaluate electricity tariffs before scaling operations. A data-driven charging strategy can reduce operating expenditure, improve fleet utilisation, and strengthen the long-term economic and environmental sustainability of public transportation."
    ])
    documents_meta["submission_14_llm_generated_essay.docx"] = {
        "modality": "docx",
        "type": "ai_generated_synthetic",
        "is_degraded": False,
        "is_ai": True,
        "llm_generator": "Antigravity (Gemini)",
        "provenance": "Synthesized by Antigravity (Gemini assistant) simulating an LLM response to the prompt: 'Write a comprehensive business case analysis for EV bus fleet charging costs'. Genuine ChatGPT outputs were not used. The user can optionally replace this file with a genuine ChatGPT output following the prompt provided in README.md.",
        "description": "Antigravity (Gemini) generated analysis simulating an LLM response on EV bus fleet charging costs."
    }

    # 15. submission_15_llm_generated_synthesis.pdf (LLM Sample #2: Synthesized by Antigravity)
    p15 = output_dir / "submission_15_llm_generated_synthesis.pdf"
    create_pdf(p15, [
        [
            "Business Case Analysis: EV Bus Fleet Charging Costs",
            "The transition from diesel-powered buses to electric vehicles (EVs) presents a significant opportunity for public transportation operators to reduce operating expenses, improve environmental sustainability, and modernize fleet operations. However, charging infrastructure, electricity tariffs, and energy management introduce new financial considerations that must be evaluated before large-scale implementation.",
            "1. Cost Structure and Key Considerations",
            "The primary advantage of EV buses is their lower energy cost compared to diesel consumption. While diesel buses incur recurring fuel expenses, EV buses require electricity for daily operations. The total charging cost depends on battery capacity, distance travelled, energy consumption per kilometre, electricity tariffs, and charging efficiency.",
            "For example, consider a fleet of 100 electric buses, each travelling approximately 200 km daily with an average energy consumption of 1.2 kWh per kilometre. The fleet would require approximately 24,000 kWh of electricity per day. At an assumed electricity tariff of ₹8 per kWh, the daily charging expense would be ₹1.92 lakh, translating to approximately ₹5.76 crore annually, assuming 300 operating days."
        ],
        [
            "2. Infrastructure and Operational Costs",
            "Beyond electricity expenses, operators must invest in charging stations, transformers, grid connections, battery management systems, and maintenance. Depot-based charging offers relatively lower costs because buses can be charged overnight during off-peak hours. However, high-power opportunity charging may be necessary for routes with longer operating hours or limited downtime.",
            "Demand charges and peak-hour electricity tariffs can significantly increase operating costs. Therefore, charging schedules must be designed around electricity pricing and fleet availability.",
            "3. Cost Optimisation Strategies",
            "Operators can reduce charging expenses through several strategies:\n- Smart Charging: Schedule charging during off-peak electricity tariff periods.\n- Load Management: Distribute charging demand to avoid excessive peak electricity consumption.\n- Route Optimisation: Allocate buses efficiently based on battery range and energy requirements.\n- Renewable Integration: Use rooftop solar installations and battery storage to reduce grid dependency.\n- Fleet Monitoring: Track energy consumption, charging efficiency, and battery health to identify operational inefficiencies.",
            "4. Business Impact and Recommendations",
            "Although EV buses require higher initial investments, their lower energy and maintenance costs can generate long-term savings. A detailed Total Cost of Ownership (TCO) analysis should compare electricity, infrastructure, maintenance, battery replacement, financing, and residual value against conventional diesel buses.",
            "Conclusion",
            "EV fleet charging costs are not determined by electricity consumption alone but by infrastructure planning, tariff structures, and operational efficiency. Implementing smart charging systems, renewable energy integration, and data-driven fleet management can significantly improve financial viability. A phased EV adoption strategy, supported by careful cost modelling, is recommended to achieve sustainable and economically efficient public transportation."
        ]
    ])
    documents_meta["submission_15_llm_generated_synthesis.pdf"] = {
        "modality": "pdf",
        "type": "ai_generated_synthetic",
        "is_degraded": False,
        "is_ai": True,
        "llm_generator": "Antigravity (Gemini)",
        "provenance": "Synthesized by Antigravity (Gemini assistant) simulating an LLM response to the prompt: 'Write a comprehensive business case analysis for EV bus fleet charging costs'. Genuine Claude outputs were not used. The user can optionally replace this file with a genuine Claude output following the prompt provided in README.md.",
        "description": "Antigravity (Gemini) generated analysis simulating an LLM response on EV bus fleet charging costs."
    }

    # 16. submission_16_quantum_hardware.pdf (Hard Negative Control #1)
    p16 = output_dir / "submission_16_quantum_hardware.pdf"
    create_pdf(p16, [
        [
            "Neutral-Atom Quantum Computing Architecture for Cryptographic Simulation.",
            "Neutral-atom quantum processors exploit optical tweezer arrays to trap individual rubidium and ytterbium atoms within ultra-high vacuum chambers. Two-qubit gate operations are mediated via laser excitation to high-lying Rydberg states, providing strong, switchable dipole-dipole interactions with high physical fidelity.",
            "Our research benchmarks surface code lattice error thresholds against coherent laser phase noise and spontaneous atomic emission events across a two-dimensional grid of one hundred physical qubits."
        ]
    ])
    documents_meta["submission_16_quantum_hardware.pdf"] = {
        "modality": "pdf",
        "type": "genuine_original_control",
        "is_degraded": False,
        "is_ai": False,
        "description": "Synthetic (script-generated) technical paper on neutral-atom quantum processors."
    }

    # 17. submission_17_quantum_algorithms.docx (Hard Negative Control #2 - Same domain as sub_16, no copy!)
    p17 = output_dir / "submission_17_quantum_algorithms.docx"
    create_docx(p17, [
        "Variational Quantum Algorithms and Zero-Noise Extrapolation on Noisy Hardware",
        "Executing variational quantum eigensolvers on intermediate-scale quantum devices demands rigorous mitigation of uncorrectable environmental decoherence. Zero-noise extrapolation models hardware gate error channels by systematically scaling microwave pulse amplitudes and extrapolating expectation values back to the zero-noise limit.",
        "We demonstrate that combining Clifford data regression with randomized compiling suppresses coherent cross-talk errors in molecular ground state calculations."
    ])
    documents_meta["submission_17_quantum_algorithms.docx"] = {
        "modality": "docx",
        "type": "genuine_original_control",
        "is_degraded": False,
        "is_ai": False,
        "description": "Synthetic (script-generated) paper on variational quantum error mitigation (hard negative to sub_16)."
    }

    # 18. submission_18_external_plagiarism.pdf (Plagiarized from External KB)
    p18 = output_dir / "submission_18_external_plagiarism.pdf"
    create_pdf(p18, [
        [
            "Circular Packaging Protocols in Consumer Supply Chains.",
            "Transitioning fast-moving consumer goods to circular packaging frameworks requires substituting virgin petroleum polymers with post-consumer recycled polyethylene terephthalate and industrially compostable polyhydroxyalkanoates. Achieving mechanical recyclability without sacrificing barrier properties against moisture and oxygen ingress represents a critical chemical engineering challenge. Successful circular supply loops require closed-loop reverse collection incentives, automated near-infrared optical flake sorting, and decontamination extrusion technologies to meet food-grade contact safety regulations."
        ]
    ])
    documents_meta["submission_18_external_plagiarism.pdf"] = {
        "modality": "pdf",
        "type": "external_copy",
        "is_degraded": False,
        "is_ai": False,
        "description": "Direct copy from external knowledge base circular packaging article."
    }

    # 19. submission_19_video_paraphrase_pitch.mp4 (Cross-Modal Paraphrase match with sub_01 Page 1)
    p19 = output_dir / "submission_19_video_paraphrase_pitch.mp4"
    create_mp4_with_audio(p19, PARAPHRASED_CROSS_MODAL_TEXT, speech_rate=180)
    documents_meta["submission_19_video_paraphrase_pitch.mp4"] = {
        "modality": "mp4",
        "type": "cross_modal_paraphrase",
        "is_degraded": False,
        "is_ai": False,
        "description": "Candidate video pitch reading aloud a paraphrased version of fintech microfinance from submission_01."
    }

    # 20. submission_20_partially_copied.docx (Hard case: Partial copy - 1 of 3 paragraphs copied from sub_01 Page 1)
    p20 = output_dir / "submission_20_partially_copied.docx"
    create_docx(p20, [
        "Digital financial inclusion across Southeast Asia has expanded rapidly with the widespread adoption of standardized interoperable QR code payment networks. Central bank regulatory sandboxes have enabled technology platforms to pilot micro-insurance and merchant working capital facilities without bearing legacy commercial banking compliance costs. In metropolitan commerce corridors, consumer payment frequency has surged, providing granular real-time cash flow records that supplement traditional credit bureau inquiries. Mobile network operators and digital retailers have formed joint ventures to leverage distributed distribution networks, deploying field agents to onboard informal rural merchants.",
        FINTECH_REPORT_P1,
        "Looking forward, sustainable unit economics will require platforms to diversify revenue away from pure payment transaction interchange fees toward recurring software subscriptions and balance sheet syndication. Providing automated inventory tracking, invoice reconciliation, and tax compliance software embeds digital platforms deeply within merchant workflows, drastically lowering customer churn. Furthermore, partnerships with regulated non-banking financial corporations allow platforms to originate asset-backed SME loans while maintaining capital adequacy discipline and shielding equity investors from severe credit cycle downturns."
    ])
    documents_meta["submission_20_partially_copied.docx"] = {
        "modality": "docx",
        "type": "partial_copy",
        "is_degraded": False,
        "is_ai": False,
        "description": "Fintech proposal where exactly 1 of 3 paragraphs is copied verbatim from submission_01 Page 1."
    }

    # 21. submission_21_ev_near_threshold_negative.pdf (Hard case: Near-threshold negative on EV transit)
    p21 = output_dir / "submission_21_ev_near_threshold_negative.pdf"
    create_pdf(p21, [
        [
            "Evaluating Municipal Hydrogen Fuel Cell Transit Alternatives.",
            "While battery-electric buses dominate urban transit electrification dialogues, municipal transit authorities facing sub-zero winter temperatures must evaluate hydrogen fuel cell alternatives. Fuel cell buses offer superior operational range exceeding 450 kilometers without mid-day depot recharging cycles, mitigating auxiliary heating battery drain.",
            "However, green hydrogen supply chains and cryogenic dispensing infrastructure introduce elevated capital expenditures and safety certification hurdles that require dedicated municipal hydrogen distribution hubs."
        ]
    ])
    documents_meta["submission_21_ev_near_threshold_negative.pdf"] = {
        "modality": "pdf",
        "type": "near_threshold_negative",
        "is_degraded": False,
        "is_ai": False,
        "description": "Independently written municipal bus transit analysis (hydrogen alternative) testing near-threshold discrimination."
    }

    # 22. submission_22_wikipedia_urban_transit.pdf (Human public-domain control #1)
    p22 = output_dir / "submission_22_wikipedia_urban_transit.pdf"
    create_pdf(p22, [
        [
            "Bus Rapid Transit Systems and Metropolitan Urban Mobility.",
            "Bus rapid transit (BRT), also called a busway or transitway, is a bus-based public transport system designed to have much more capacity and reliability than a conventional bus system. Typically, a BRT system includes roadways that are dedicated to buses, and gives priority to buses at intersections where buses may interact with other traffic; alongside design features to reduce delays caused by passengers boarding or leaving buses, or purchasing fares. BRT aims to combine the capacity and speed of a light rail or metro system with the flexibility, lower cost and simplicity of a bus system."
        ]
    ])
    documents_meta["submission_22_wikipedia_urban_transit.pdf"] = {
        "modality": "pdf",
        "type": "human_control_public_domain",
        "is_degraded": False,
        "is_ai": False,
        "source": "Wikipedia - Bus rapid transit",
        "source_url": "https://en.wikipedia.org/wiki/Bus_rapid_transit",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "description": "Human-authored public-domain article baseline testing AI detector false positives and similarity negatives."
    }

    # 23. submission_23_rfc_internet_protocol.docx (Human public-domain control #2)
    p23 = output_dir / "submission_23_rfc_internet_protocol.docx"
    create_docx(p23, [
        "DARPA Internet Program Protocol Specification (RFC 791)",
        "The Internet Protocol is designed for use in interconnected systems of packet-switched computer communication networks. The internet protocol provides for transmitting blocks of data called datagrams from sources to destinations, where sources and destinations are hosts identified by fixed length addresses.",
        "The internet protocol also provides for fragmentation and reassembly of long datagrams, if necessary, for transmission through small-packet networks. The internet protocol implements two basic functions: addressing and fragmentation. The internet modules use the addresses carried in the internet header to transmit internet datagrams toward their destinations."
    ])
    documents_meta["submission_23_rfc_internet_protocol.docx"] = {
        "modality": "docx",
        "type": "human_control_public_domain",
        "is_degraded": False,
        "is_ai": False,
        "source": "IETF RFC 791: Internet Protocol Specification (1981)",
        "source_url": "https://datatracker.ietf.org/doc/html/rfc791",
        "license": "Public Domain (IETF RFC Standards Document)",
        "description": "Human-authored technical specification baseline testing AI detector false positives and similarity negatives."
    }

    # 24. submission_24_wikipedia_renewable_energy.pdf (Human public-domain control #3)
    p24 = output_dir / "submission_24_wikipedia_renewable_energy.pdf"
    create_pdf(p24, [
        [
            "Photovoltaic Solar Power and Energy Conversion Principles.",
            "Photovoltaics (PV) is the conversion of light into electricity using semiconducting materials that exhibit the photovoltaic effect, a phenomenon studied in physics, photochemistry, and electrochemistry. A photovoltaic system employs solar modules, each comprising a number of solar cells, which generate electrical power. PV installations may be ground-mounted, rooftop-mounted, wall-mounted or floating. The mount may be fixed or use a solar tracker to follow the sun across the sky."
        ]
    ])
    documents_meta["submission_24_wikipedia_renewable_energy.pdf"] = {
        "modality": "pdf",
        "type": "human_control_public_domain",
        "is_degraded": False,
        "is_ai": False,
        "source": "Wikipedia - Photovoltaics",
        "source_url": "https://en.wikipedia.org/wiki/Photovoltaics",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "description": "Human-authored public-domain article baseline testing AI detector false positives and similarity negatives."
    }

    # Clean old files if present
    for old_file in output_dir.glob("submission_*"):
        if old_file.name not in documents_meta:
            try:
                old_file.unlink()
            except Exception:
                pass

    # Build Exhaustive Pairwise Labels (N * (N-1) / 2 pairs)
    doc_keys = sorted(documents_meta.keys())
    pairwise_manifest = []

    prompt_docs = {
        "submission_09_ev_depot_charging.pdf",
        "submission_10_ev_battery_degradation.docx",
        "submission_11_ev_municipal_debt.pdf",
        "submission_12_ev_route_energy.docx",
        "submission_13_ev_grid_balancing.pdf"
    }

    for doc_a, doc_b in itertools.combinations(doc_keys, 2):
        # Determine pairwise relationship
        pair_set = {doc_a, doc_b}
        if pair_set == {"submission_03_logistics_strategy.docx", "submission_05_logistics_exact_copy.pdf"}:
            label = "exact_copy"
            is_plag = True
        elif pair_set == {"submission_01_fintech_report.pdf", "submission_02_video_pitch.mp4"}:
            label = "cross_modal"
            is_plag = True
        elif pair_set == {"submission_01_fintech_report.pdf", "submission_19_video_paraphrase_pitch.mp4"}:
            label = "cross_modal"
            is_plag = True
        elif pair_set == {"submission_01_fintech_report.pdf", "submission_20_partially_copied.docx"}:
            label = "exact_copy"
            is_plag = True
        elif pair_set == {"submission_19_video_paraphrase_pitch.mp4", "submission_20_partially_copied.docx"}:
            label = "cross_modal"
            is_plag = True
        elif pair_set == {"submission_03_logistics_strategy.docx", "submission_04_logistics_rewritten.docx"}:
            label = "paraphrase"
            is_plag = True
        elif pair_set == {"submission_04_logistics_rewritten.docx", "submission_05_logistics_exact_copy.pdf"}:
            label = "paraphrase"
            is_plag = True
        elif pair_set == {"submission_14_llm_generated_essay.docx", "submission_15_llm_generated_synthesis.pdf"}:
            # Two independent LLMs prompted with the same assignment brief are NOT student-to-student copying
            label = "same_prompt_ai_outputs"
            is_plag = False
        elif "submission_18_external_plagiarism.pdf" in pair_set:
            # External plagiarism is against KB, not peer
            label = "unrelated"
            is_plag = False
        elif doc_a in prompt_docs and doc_b in prompt_docs:
            label = "same_template_only"
            is_plag = False
        else:
            label = "unrelated"
            is_plag = False

        pairwise_manifest.append({
            "doc_a": doc_a,
            "doc_b": doc_b,
            "ground_truth_label": label,
            "is_plagiarized_pair": is_plag
        })

    external_gt = {
        "submission_18_external_plagiarism.pdf": {
            "is_external_plagiarism": True,
            "source_kb_file": "circular_packaging.txt",
            "expected_external_pct_min": 40.0
        }
    }

    full_manifest = {
        "dataset_name": "Unstop Multimodal Integrity Benchmark Dataset (Exhaustive Ground Truth)",
        "version": "2.2.0",
        "total_documents": len(documents_meta),
        "total_pairs": len(pairwise_manifest),
        "valid_pair_labels": ["exact_copy", "paraphrase", "cross_modal", "external", "same_template_only", "same_prompt_ai_outputs", "unrelated"],
        "documents": documents_meta,
        "external_ground_truth": external_gt,
        "pairwise_ground_truth": pairwise_manifest
    }

    manifest_path = output_dir / "dataset_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(full_manifest, f, indent=2)

    logger.info(f"Dataset generated: {len(documents_meta)} submissions, {len(pairwise_manifest)} labeled pairs in {manifest_path}.")

if __name__ == "__main__":
    generate_dataset(Path("./sample_submissions"))
