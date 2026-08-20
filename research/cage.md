## Abstract

레드팀 벤치마크를 다른 언어로 옮길 때 흔히 쓰는 직역은, 그 사회의 문화와 법률에 뿌리내린 취약점을 놓친다. 문장은 번역되지만 위협은 번역되지 않기 때문이다. 그 결과 LLM 안전성 평가에 사각지대가 생긴다.

CAGE(Culturally Adaptive Generation)는 검증된 레드팀 프롬프트에서 **공격 의도만 남기고 문화적 내용물을 갈아끼우는** 프레임워크다. 핵심은 프롬프트의 공격 구조와 문화적 내용을 분리하는 **Semantic Mold**로, 단순한 탈옥 성공 여부가 아니라 특정 사회에서 실제로 성립하는 위협을 모델링한다.

이 프레임워크로 한국어 벤치마크 **KorSET**을 만들었고, 직역 기반 벤치마크보다 취약점을 더 잘 드러냈다.

## Background

기존 레드팀 벤치마크는 대부분 영어권 맥락 위에서 만들어졌다. 이를 다른 언어로 직역하면 표면적인 문장은 옮겨지지만, 그 공격이 기대고 있던 제도·규범·사건은 함께 옮겨지지 않는다. 대상 언어권에서는 애초에 성립하지 않는 위협을 묻게 되는 것이다.

반대로 각 문화권마다 벤치마크를 처음부터 새로 만드는 것은 비용이 크고, 기존 연구가 검증해 둔 공격 구조를 버리게 된다. CAGE는 그 둘 사이를 겨냥한다. 공격의 뼈대는 재사용하고, 살만 그 문화권의 것으로 바꾼다.

## Method

![CAGE 파이프라인](/assets/research/cage/cage_method.png)
*그림 1. 시드 수집 · 정제 · 번역의 3단계 파이프라인*

**1. Seed Prompt Collection.** 참조 데이터셋을 사람이 검토해 위험 분류 체계(CAGE Taxonomy)를 세우고, 위험 유형별로 반드시 포함돼야 하는 의미 요소(Essential Slot)와 선택적 요소(Optional Slot)를 지정한다. 시드 프롬프트는 다섯 개의 LLM이 각자 라벨링해 **전원이 일치한 것만** 채택하고, 하나라도 갈리면 버린다.

**2. Refinement.** 선택된 시드와 슬롯 정의를 Refiner에 넣어 Semantic Mold를 뽑는다. Mold는 `[Action]` `[Target]` `[Method]` `[Condition]` 같은 추상 자리표로 이뤄지며, **무엇이 들어가야 하는지는 규정하되 문장을 어떻게 써야 하는지는 고정하지 않는다.** 고정 템플릿이 아니라 틀이라서, 언어가 달라져도 구조는 유지한 채 자연스러운 문장을 만들 수 있다.

**3. Translation.** 웹 소스에서 수집한 그 문화권의 실제 맥락과 법적 근거를 Mold의 빈칸에 채워 최종 프롬프트를 생성한다.

KorSET은 이 과정을 거쳐 **6,975개 프롬프트**로 구성됐다. 5개 위험 도메인 아래 12개 Level-2 카테고리, 53개 Level-3 유형으로 나뉜다.

## Results

![프롬프트 품질과 레드티밍 효과](/assets/research/cage/cage_prompt_quality.png)
*그림 2. 직역(DirTrans) 대비 프롬프트 품질(좌)과 공격 성공률(우)*

**프롬프트 품질.** 문화적 특수성 점수(3점 만점)와 종합 품질 점수(13점 만점) 모두 직역 대비 크게 올랐다. 예컨대 Toxic Language는 문화적 특수성이 `0.59 → 2.02`, 종합 점수가 `4.91 → 10.46`으로 뛰었다. 직역본의 문화적 특수성이 대부분 1점에 한참 못 미친다는 점이, 직역이 무엇을 잃는지 그대로 보여준다.

**레드티밍 효과.** 같은 공격 기법을 쓰더라도 CAGE 프롬프트의 공격 성공률(ASR)이 모든 조건에서 가장 높았다.

| Llama-3.1 / Direct Request | ASR |
| --- | --- |
| DirTrans (직역) | 28.2% |
| LLM-Adapt | 32.4% |
| Template | 31.9% |
| **CAGE** | **43.8%** |

논문은 이 차이를 두 갈래로 분해한다. 문화적 맥락을 갈아끼운 데서 오는 **Cultural Effect가 평균 +20~35%**로, 표현을 더 구체화한 데서 오는 Specificity Effect(+8~11%)보다 훨씬 크다. 프롬프트가 정교해져서가 아니라 **위협이 그 사회에서 실제로 말이 되기 때문에** 뚫린다는 뜻이다.

![모델별 공격 성공률](/assets/research/cage/cage_main_result.png)
*그림 3. 위험 분류 × 공격 기법 × 모델별 ASR*

**모델과 공격 기법.** Llama-3.1-8B, Qwen2.5-7B, gemma2-9B-it, EXAONE3.5-7.8B-it, gemma3-12B-it를 GCG · TAP · AutoDAN · GPTFuzzer와 Direct Request 기준선으로 평가했다.

- 공격 기법 중에서는 **GPTFuzzer**의 평균 ASR이 가장 높았다
- 모델 중에서는 **Llama-3.1-8B가 가장 취약**했고, 특히 Information & Safety Harms에서 60%대까지 올랐다
- **EXAONE3.5가 가장 견고**했다
- 도메인 중에서는 Toxic Language가 가장 잘 방어됐다

## Generalization

프레임워크가 한국어에만 맞춰진 것인지 확인하기 위해 저자원 언어인 **크메르어**에 그대로 적용했다. 웹 소스 탐색을 LLM이 보조하고 사람이 검증하는 방식으로 문화적 근거를 수집했다.

gemma3-12B-it 기준으로 보안 위협 카테고리의 ASR이 직역 대비 `2.7% → 35.1%`로 뛰었고, 다른 카테고리에서도 `4.9% → 34.4%` 수준의 상승이 나타났다. 학습 데이터가 적은 언어일수록 직역 벤치마크가 취약점을 못 잡아낸다는 뜻이기도 하다.

## Citation

```bibtex
@inproceedings{kim2026cage,
  title     = {{CAGE}: A Framework for Culturally Adaptive Red-Teaming Benchmark Generation},
  author    = {Kim, Chaeyun and Lim, YongTaek and Kim, Kihyun and Kim, Junghwan and Kim, Minwoo},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2026},
  url       = {https://openreview.net/forum?id=gCm55KYiqz}
}
```

데이터셋과 평가 루브릭은 [github.com/selectstar-ai/CAGE-paper](https://github.com/selectstar-ai/CAGE-paper)에 공개돼 있다.
