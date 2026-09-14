## Abstract

LLM이 벤치마크에서 높은 정확도를 보인다고 해서 인간과 비슷하게 반응한다는 뜻은 아니다. 정확도가 비슷한 모델도 어떤 문항을 어려워하는지, 틀렸을 때 어떤 오답을 고르는지는 서로 다를 수 있다. 이 연구는 이를 진단하기 위해 **CAPE(Choice-Distribution Alignment and Performance Evaluation)** 프레임워크를 제안한다. CAPE는 인구 규모의 인간 선택 분포를 이용해 인간-LLM 반응 정렬을 outcome 수준의 난이도 정렬과 response-distribution 수준의 정렬로 분리하고 이를 OA·MAE·PA·DA 네 지표로 측정한다.

문항당 약 30만 명의 응시자 반응 분포가 있는 한국 수능 국어 영역 609문항에 CAPE를 적용해 16개 LLM을 평가했다. 평가한 모델군 안에서는 모델 성능(정확도)이 정렬과 강하게 연관돼 있어 정답 선택뿐 아니라 오답 선택(distractor)에서도 정확도와 밀접했다. 다만 집단 수준 점수는 집계 크기와 모델 구성에 영향을 받았고 reasoning 증강이나 한국어 특화 튜닝이 일관된 추가 이득을 주지는 않았다. Bloom 분류 수준별 분석은 능력-정렬 관계가 문항 유형에 따라 달라짐을 보여준다. CAPE는 정확도를 넘어 모델의 성공·실패 패턴이 인간 집단의 반응과 어떻게 관련되는지 진단할 수 있게 한다.

## Background

LLM은 점점 높은 벤치마크 정확도를 달성하지만 높은 정확도가 곧 인간과 유사한 반응 행동을 뜻하지는 않는다. 기존 평가는 대부분 정확도·F1 같은 스칼라 지표에 의존하고 reasoning-trace 분석도 모델이 인간과 비슷한 난이도 패턴이나 오답 선호를 재현하는지는 보여주지 않는다. 인간-LLM 정렬을 다룬 선행 연구들도 제한된 인간 표본이나 요약 통계에 의존해 왔고, 선택지 수준(choice-level)의 반응 패턴은 충분히 탐구되지 않았다.

## Method

**데이터셋 - 한국 수능(CSAT) 국어 영역.** 대한민국의 대학수학능력시험(CSAT) 국어 영역은 매년 약 45개의 5지선다 문항으로, 문학·독서·화법·작문·문법·고전문법 6개 하위 영역을 다룬다. 2020~2024년 공식 수능 및 한국교육과정평가원(KICE) 모의고사에서 609문항을 분석했다. 이 시험은 모든 문항이 동일한 5지선다 답안 공간을 공유하고 실제 응시자의 오답을 유도하도록 설계된 매력적인 distractor를 포함하고 있어 인간-LLM 정렬 분석에 적합한 테스트베드다.

**인구 규모 인간 반응 분포.** 매년 약 50만 명이 응시하는 수능의 특성과 한국 주요 입시 플랫폼들이 문항별 반응 통계를 공개하는 관행 덕분에 정답뿐 아니라 5개 선택지 전체에 대한 경험적 인간 선택 분포를 구성할 수 있다. 이 연구는 한국 주요 입시 플랫폼 메가스터디가 제공한 문항별 반응 통계를 사용했으며 문항당 약 30만 명의 선택 분포를 확보했다. 다만 이 데이터는 플랫폼 이용자의 자발적 제출에 기반하므로 전체 응시자의 완전한 census가 아니라 대규모 행동적 baseline으로 취급했다.

**인지 수준 주석(Bloom's Taxonomy).** 모델 능력이 언제 인간과 유사한 반응 분포로 이어지고 언제 그렇지 않은지 살펴보기 위해 개정된 Bloom 분류체계(Remembering, Understanding, Applying, Analyzing, Evaluating, Creating) 6단계로 전 문항에 주석을 달았다. 수능 국어의 공식 출제 체계(어휘·개념, 사실적 이해, 추론적 이해, 비판적 이해, 응용/창의)를 Bloom 단계에 매핑했고, 현직 국어 교사 2인이 독립적으로 주석해 Cohen's κ = 0.84의 높은 일치도를 보였다.

**평가 모델.** 접근성(proprietary/open-source), reasoning 증강 여부, 모델 규모, 한국어 특화 튜닝 여부라는 네 축을 기준으로 16개 LLM을 선정했다 - Claude 3.5 Sonnet, GPT-4o, Gemini 2.0 Flash, CLOVA HCX-DASH-001, GPT-o1, Gemini 2.0 Flash Thinking, 그리고 Llama·Qwen 계열의 light(≤3B)·small(4~8B)·middle(9~32B)·big(33~72B) 오픈소스 모델과 그 한국어 파인튜닝 버전들이다. 모든 모델은 동일한 0-shot 프롬프트로 평가했다.

![평가 모델 목록과 CSAT 국어 정확도](/assets/research/cape/fig1.png)
*그림 1. 평가에 사용된 16개 LLM과 그룹, CSAT 국어 문항 정확도(Acc.). 별표(*)는 한국어 파인튜닝 모델*

**CAPE의 네 지표.** 문항 i에 대해 인간과 LLM의 정확도를 h_i, l_i, 다섯 선택지에 대한 반응 분포를 p_h^(i), p_l^(i)라 할 때:

- **OA (Outcome Alignment)**: 문항별 난이도의 순위 상관(Spearman's ρ)으로, 인간과 모델이 같은 문항을 어려워하는지를 본다.
- **MAE (Mean Absolute Error)**: 인간-LLM 정확도 격차의 절댓값 평균.
- **PA (Process Alignment)**: 1 − JSD(p_h, p_l)로, 정답을 포함한 5개 선택지 전체 분포의 유사도를 측정한다.
- **DA (Distractor Alignment)**: 정답을 제거하고 나머지 4개 오답 분포를 재정규화한 뒤 1 − JSD로 계산한다. 정답을 맞힌 문항은 오답 질량이 없으므로 개별 모델의 DA 계산에서 제외되며, 이 때문에 DA는 오차 조건부(error-conditional) 지표가 된다.

PA는 정답 여부와 오답 선호를 모두 반영하는 전체 정렬을, DA는 모델이 틀렸을 때 인간과 같은 오답을 고르는지(정답 여부와 독립적인 오답 선호의 정렬)를 각각 포착한다.

## Results

**모델별 정확도.** 16개 모델의 정확도는 0.20~0.88로 폭넓게 분포했다. Proprietary 모델과 reasoning 증강 모델이 대체로 높은 성능을 보였고 오픈소스 모델 중에서는 대체로 큰 모델이 더 나은 성능을 보였지만 파라미터 수나 한국어 파인튜닝에 따라 단조롭게 증가하지는 않았다(예: Claude 3.5 Sonnet 0.88, GPT-o1 0.86, Qwen 2.5 32B 0.75, Llama 3.1 8B 0.27, Llama 3.2 3B 0.20).

**Bloom 수준별 정확도 격차.** 전체 AI 그룹은 인간보다 전반적으로 낮은 정확도를 보였는데 그 격차는 인지 수준이 높아질수록 단조롭게 커지지 않았다. 오히려 최하위 단계인 Remembering에서 격차가 가장 컸다 - 인간 정확도 71.5% vs AI 그룹 37.5%로 34.0%p 차이가 났다(Understanding, Applying, Analyzing, Evaluating은 16~21%p 격차, Creating은 격차 없음).

![Bloom 수준별 인간-AI 정확도 격차](/assets/research/cape/fig2.png)
*그림 2. Bloom 분류 수준별 인간 정확도, 전체 AI 그룹 정확도, 그 격차(Gap = Full AI − Human)*

![모델군별 CAPE 정렬 지표](/assets/research/cape/fig3.png)
*그림 3. 모델군별 OA·MAE·PA·DA 원점수(raw score). OA는 순열검정 기준 유의성 표시(*** p < .001)*

**능력과 정렬의 관계.** 16개 모델 각각의 정확도와 PA·DA를 상관분석한 결과, 정확도는 PA와 거의 완벽하게 상관됐고(r = 1.00, p < .001) DA와도 강하게 상관됐다(r = 0.90, p < .001). Leave-one-model-out 분석에서도 이 관계는 특정 모델 하나에 좌우되지 않았다(Accuracy–DA: r = .879~.926, Accuracy–PA: r = .997~.998 범위 유지). PA는 정답을 포함하므로 정확도와 구조적으로 얽혀 있지만 정답을 제거한 DA도 강하게 상관된다는 것은 능력이 높은 모델이 오답을 고를 때조차 인간이 그럴듯하다고 느끼는 오답을 고르는 경향이 있음을 시사한다.

**집단 크기 효과 통제.** 그룹에 모델을 더 많이 모을수록 반응 분포가 매끄러워져 인간 분포와의 유사도가 기계적으로 올라갈 수 있다. 같은 크기의 무작위 모델 집합을 1,000회 샘플링해 만든 group-size-matched null 분포와 비교한 결과, 한국어 파인튜닝 그룹은 기대보다 높은 DA를 보였으나(z = +2.03, 편측 p = .020) small 그룹도 비슷한 경향을 보였다(z = +1.58, p = .034). 다만 이 편차들은 다중비교 보정을 거치면 유의성이 사라져 안정적인 그룹 고유 효과로 해석하지 않았다.

**능력을 통제한 잔차 분석.** 정확도로 예측한 DA 대비 각 모델의 잔차를 보면 reasoning 증강 모델 두 개(Gemini-2.0-Thinking, GPT-o1)가 회귀선을 기준으로 서로 반대 방향에 위치했고 한국어 특화 모델 중에서도 CLOVA-HCX만 뚜렷하게 예측치를 웃돌았다. 즉 reasoning 증강이나 한국어 적응이 능력을 통제한 뒤에도 일관되게 인간과 유사한 오답 정렬을 높인다는 증거는 없었다.

**Bloom 수준이 능력-정렬 관계를 조절한다.**
- **Remembering - 성공적 인출 없는 인간형 오답 선호.** Remembering은 부트스트랩 표본의 93.5%에서 DA가 PA를 웃돈(DA−PA = +0.025) 유일한 Bloom 단계였다(다른 단계는 모두 PA가 DA보다 큼). 즉 최하위 인지 단계에서는 인간과 비슷한 오답 선호가 올바른 정답 인출로 이어지지 않을 수 있다. 한 예시 문항(중세 국어 문법)에서는 인간 정확도 84.0% vs 모델 정확도 18.8%로 격차가 컸지만 오답 중 인간의 절반과 모델 오류의 53.8%가 같은 distractor에 몰려 매우 높은 DA(.989)를 기록했다.
- **Evaluating - 능력-DA 연관의 (탐색적) 약화.** PA는 모든 Bloom 단계에서 정확도와 거의 완벽히 상관됐지만(r = .98~1.00), DA는 Remembering~Analyzing까지는 정확도와 강하게 상관되다가(r = .69~.84) Evaluating에서는 그 관계가 크게 약해졌다(r = .39, 95% CI [−.13, .74], 신뢰구간이 0을 포함해 확정적 결론은 아님). 한 예시 문항(작문 첨삭)에서는 인간·모델 정확도(90.1% vs 75.0%)와 PA(.900) 모두 높았지만 인간과 모델이 가장 많이 고른 오답이 서로 달라 DA는 상대적으로 낮았다(.576).
- **Understanding·Applying·Analyzing - 안정적인 능력-정렬 구간.** 이 세 단계에서는 PA가 DA를 일관되게 웃돌면서도 정확도가 PA·DA 모두와 유의하게 양의 상관을 보여 Remembering의 인출 역전이나 Evaluating의 약화된 DA 연관 없이 안정적인 패턴을 보였다. Understanding이 전체 데이터셋에서 가장 큰 비중을 차지한다는 점에서 이 안정성은 특히 중요하다.

## Citation

```bibtex
@inproceedings{park2026cape,
  title     = {When Accuracy Aligns and Fails: Diagnosing Human--LLM Response Alignment at Population Scale},
  author    = {Park, Seoyoon and Choi, Hyeji and An, Subin and Wang, Xiaonan and Kim, Heejae and Kang, Joeun and Kim, Hansaem},
  booktitle = {Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year      = {2026}
}
```
