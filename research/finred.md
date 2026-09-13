## Abstract

기존 안전성 벤치마크는 범용적인 위험(universal risks)에 초점을 맞추고 있어 금융 도메인 고유의 위협을 놓친다. 금융 LLM은 규제 준수 위반, 사기 조장, 시스템적 신뢰 침식처럼 그 분야에서만 성립하는 위험에 노출돼 있다.

FinRED는 금융 전문가와 함께 만든 전문가 지도(expert-guided) red-teaming 프레임워크다. FATF, EU DORA 같은 국제 표준을 위협 분류체계에 매핑하는 이원적 taxonomy를 세우고 실제 금융 문서를 전문가 정의 스키마를 거쳐 맥락이 풍부한 red-teaming Behavioral Prompt(시드)로 변환하는 파이프라인을 갖췄다. 전문가 검증을 통해 시드의 타당성과 현실성을 확인했다.

## Background

기존 금융 특화 벤치마크(Pixiu, FinEval, FinanceBench 등)는 정보 추출·추론·도메인 지식 이해 같은 "무엇을 할 수 있는가"에 집중할 뿐 적대적 압력(adversarial pressure) 아래에서 모델이 "어떻게 행동하는가"는 평가하지 않는다. 반대로 일반적인 안전성 평가는 금융 도메인의 맥락 없이 단순 면책 조항 확인 수준에 머문다. FinRED는 그 사이, 즉 금융 규제·범죄·소비자 보호 맥락에 뿌리내린 red-teaming 평가를 겨냥한다.

## Method

![FinRED 파이프라인](/assets/research/finred/fig2.png)
*그림 1. (a) 금융 위험 분류체계·스키마 구축 (b) 문서 청킹과 벡터 검색을 통한 맥락 확보 (c) 맥락 기반 시나리오 생성과 전문가 검증을 거친 최종 시드 생성*

FinRED는 다섯 단계로 구성된다.

- **1단계. 금융 위험 분류체계 구축.** FATF, BIS/BCBS, ISO/IEC 27001, NIST, OWASP, EU DORA 등 국제 감독 프레임워크의 threat-modeling 원칙에 기반해 12명의 금융보안원(FSI) 전문가가 분류체계를 정제했다. Level 1은 5개 범주(사이버 위협, 금융 범죄, 허위정보·기만, 소비자권 침해, 규제 회피 evasion)이며, 그 아래 26개 Level 2 세부 유형이 있다.
- **2단계. 스키마 기반 위협 행동 정의.** attackerProfile·targetTechnology 같은 필수 요소(Essential cues)와 vulnerabilityHypothesis·requesterPersona 같은 선택 요소(Optional cues)로 구성된 JSON 스키마를 세 개 LLM(Gemini 2.5 Pro, GPT-4.1, Claude Sonnet 4)으로 초안 생성한 뒤 FSI 전문가와 세 차례 논의를 거쳐 다듬었다.
- **3단계. 문서 수집 및 맥락 검색.** 규제 프레임워크·감독 지침·감사보고서·위험평가 보고서 등 약 500개 금융 문서를 전문가가 선별했다. 구조적 청킹(제목·표 기준, 최대 2,800자)과 재분할(1,200자 초과 시 150자 오버랩)을 거쳐 OpenAI 임베딩으로 Chroma 벡터DB에 저장하고 Level-2 범주별 전문가 쿼리로 상위 8개 청크를 검색한다.
- **4단계. 행동 시드 자동 생성.** 스키마와 검색된 맥락을 LLM에 넣어 구조화된 JSON 시나리오를 만들고(1단계) 이를 다시 자연어 시드로 변환한다(2단계). 이 과정에서 맥락에 맞는 공격자 페르소나를 부여(Dynamic Persona Assignment)하고 필수 요소는 모두 포함하되 선택 요소는 다양하게 조합(Strategic Combination)한다. 최종적으로 자기 수정 지시로 논리적 일관성을 확인하고, 금융 전문가 focus group interview로 현실성·공격 효과성·해악 명확성을 평가한다.
- **5단계. 평가 루브릭 설계.** Harmfulness, Persuasiveness, Refusal Quality, Factualness, Evasiveness 다섯 차원을 판정하며 다섯 차원 중 하나라도 Unsafe로 판정되면 응답 전체를 Unsafe로 표시하는 보수적 fail-safe 정책을 쓴다.

이 과정을 거쳐 5개 Level-1 범주, 26개 Level-2 범주에 걸쳐 5,805개의 전문가 검증 시드가 만들어졌다.

![FinRED 위험 분류체계](/assets/research/finred/fig1.png)
*그림 2. FinRED Risk Taxonomy — Level 1 5개 범주(R1 사이버 위협, R2 금융 범죄, R3 허위정보·기만, R4 소비자권 침해, R5 금융 ICT 규제 회피)와 그 아래 26개 Level 2 세부 유형, 범주별 시드 수*

## Results

**공격 성공률(ASR).** 화이트박스(GCG, AutoDAN)와 블랙박스(TAP, GPTFuzzer, AutoDAN-Turbo) 공격, Direct Request 기준선으로 일반 소형 LLM 4종, 금융 특화 소형 LLM 3종(FinMA, qqWen-7B, qqWen-32B), 상용 API 기반 LLM 5종(GPT-5, GPT-5-mini, Claude 4 Sonnet, Gemini 2.5 Flash/Pro)을 평가했다.

| 위험 범주 | 공격 방법 | Llama-3.1 | Qwen2.5 | Gemma3 | GPT-5 | Claude-4 | Gemini-Pro |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 사이버위협 | Direct Request | 24.05 | 82.41 | 53.80 | 0.63 | 22.78 | 63.29 |
| R1 사이버위협 | AutoDAN | 37.34 | 98.73 | 73.42 | – | – | – |
| R2 금융범죄 | GPTFuzzer | 75.71 | 82.14 | 68.57 | 0.00 | 2.14 | 52.14 |
| R4 소비자권침해 | GPTFuzzer | **90.80** | 93.68 | 67.24 | 0.00 | 6.90 | 46.44 |

![위험 범주 × 공격 기법 × 모델별 ASR 전체 결과](/assets/research/finred/fig3.png)
*그림 3. R1~R5 전 범주에 대한 일반 소형 LLM·금융 특화 소형 LLM·API 기반 LLM의 공격 방법별 ASR(%) 전체 결과*

개방형 소형 LLM이 가장 취약했고(예: R1에서 Qwen2.5 + AutoDAN 98.73%) API 기반 모델 중 GPT 계열은 Direct Request 기준 10% 미만으로 매우 견고했으나 Gemini 및 Claude 계열은 R1 등 일부 위험 범주에서 Direct Request만으로도 20%~63% 수준의 높은 취약점을 보였다. 공격 기법 중에서는 GPTFuzzer가 전반적으로 가장 강력했고 R1(사이버 위협)이 가장 취약한 반면 R2(금융 범죄)는 상대적으로 저항력이 높았다.

**생성 파이프라인 비교.** 맥락 없이 생성한 파이프라인(P1), 맥락만 반영한 파이프라인(P2), 스키마 기반의 제안 파이프라인(P3, FinRED)을 비교하면 ASR이 일관되게 상승했다.

| 파이프라인 | 일반 소형 LLM | 금융 특화 소형 LLM | API 기반 LLM |
| --- | --- | --- | --- |
| P1 (맥락 없음) | 41.32% | 52.47% | 28.91% |
| P2 (맥락 기반) | 49.86% | 61.73% | 36.58% |
| **P3 (스키마 기반, 제안)** | **58.05%** | **70.28%** | **44.44%** |

**판정 루브릭 검증.** FinRED 판정 루브릭을 HarmBench 기준선과 비교하면 인간 전문가 판단과의 합의율이 76.92%에서 88.46%로 오르고 치명적 거짓 음성(critical false negative)이 28건에서 12건으로 57% 줄었다(쌍 t-검정 p=0.0024, McNemar 검정 p=0.0041). 분류체계와 판정 루브릭 모두 전문가 합의율 83% 이상, Cohen's κ 0.79 이상을 기록했다.

FinRED는 현재 한국 금융보안원(FSI)의 규제 샌드박스에 실제 배포되어 금융 서비스 생성형 AI의 보안 평가에 쓰이고 있다.

## Citation

```bibtex
@article{finred2026,
  title   = {FinRED: An Expert-Guided Benchmark Generation and Evaluation Framework for Financial LLM Red-Teaming},
  author  = {Kim, Chaeyun and Park, Daeyoung and Kim, Junghwan and Jeong, Jinyoung and Song, Eunji and Lim, Yongtaek and Kim, Minwoo},
  journal = {arXiv preprint arXiv:2606.19887},
  year    = {2026}
}
```
