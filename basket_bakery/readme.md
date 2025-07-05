## Streamlit 활용 베이커리 운영 대시보드 및 장바구니 분석 기반 마케팅 전략 요약 카드
- **주요 기능**
  - **일/주/월 단위 필터링**: 시간 기반 트렌드 탐색 가능
  - 필터링된 기간의 csv 데이터 다운로드 가능
  - **핵심 지표**: 총 거래수, 피크 타임, 인기 제품 실시간 표시
  - Lift ,Confidence 기반 마케팅 전략 문구
- **비즈니스 활용**
  - 운영 현황 직관적으로 파악 가능
  - 판매 트렌드 기반 프로모션 시기 및 품목 선정
  - 재고 배치 및 상품 구성 전략 수립
  - 조합 추천을 통한 세트 상품 제안 및 매출 상승 유도
- **KPT 회고**
  - Keep
    - UX향상을 위해 날짜별 필터링 기능은 슬라이더 기능으로 한 점
    - 팀에서 데이터 활용할 수 있도록 csv다운로드 버튼 추가한 점 
  - Problem
    - 증감률은 일별 기준으로만 동작(주/월 기준 비교 미반영)
  - Try
    - Page나 Session State같은 동적 기능의 활용 방안을 좀 더 연구해야겠다.
    - UI를 더 대시보드답게 구성해야겠다.
<p align='center'>
<img src="https://github.com/user-attachments/assets/924f0620-b81c-4106-a041-ea11828569a5"  width=600 height=800 ></img><br/>
</p>

<p align='center'>
<img src="https://github.com/user-attachments/assets/15d7f54c-8e8f-4cc0-9b18-e9de8434e8e9"  width=600 height=800 ></img><br/>
</p>
