---

name: menu-filter
description: Filter unfamiliar or unsuitable meal candidates from external recipe data.
---------------------------------------------------------------------------------------

# Menu Filter Skill

## Purpose

외부 레시피 데이터에서 가져온 메뉴 후보 중 사용자에게 적합하지 않거나 생소한 메뉴를 걸러낸다.

## Responsibilities

* 메뉴 이름 분석
* 재료 목록 분석
* 장보기 목적과의 적합성 판단
* 생소한 메뉴 및 재료 필터링
* 디저트 메뉴의 목적별 허용 여부 판단

## Input Schema

```json
{
  "menu": "Algerian Kefta",
  "ingredients": ["ground_beef", "plum_tomatoes", "garlic"],
  "purpose": "weekly"
}
```

## Output Schema

```json
{
  "menu": "Algerian Kefta",
  "accepted": false,
  "score": -10,
  "is_dessert": false,
  "reasons": ["unfamiliar keyword: algerian"],
  "source": "menu-filter-mcp"
}
```

## Filtering Criteria

* 국내 사용자에게 익숙하지 않은 메뉴명
* 생소한 식재료
* 재료 수가 지나치게 많은 메뉴
* 장보기 목적과 맞지 않는 디저트 메뉴
* 알레르기 위험 재료 포함 여부

## Notes

이 Skill은 Recipe MCP에서 가져온 외부 레시피 데이터를 바로 사용하지 않고, 실제 장보기 서비스에 적합한 메뉴만 선별하기 위해 사용된다.
