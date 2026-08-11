from schemas.content import CardNewsData, CoverSlide, SlideBase, CTASlide
from services.renderer import _sync_render_card_news

mock_data = CardNewsData(
    category="세계엽기동물",
    source_name="BBC News",
    source_url="https://www.bbc.com/news/test",
    is_historical_fallback=False,
    cover=CoverSlide(
        tagline="😱 BBC News 엽기 보도",
        title="18캔 맥주 마신 오스트레일리아 수돼지 폭동!",
        subtitle="캠핑장에서 맥주 서리 후 소와 육탄전 벌인 미스터리한 돼지 사건",
        image_prompt="drunk pig running in campsite night Australia photorealistic"
    ),
    body_slides=[
        SlideBase(
            title="사건의 발단: 수수께끼의 캔 맥주 실종",
            subtitle="캠핑객들이 잠든 사이 벌어진 엽기 범행",
            story_text="호주 데번포트의 한 평화로운 캠핑장. 밤사이에 캠핑객들이 보관해 둔 맥주 18캔이 흔적도 없이 사라지는 이상한 사건이 발생했습니다. 텐트 주변에는 날카로운 이빨 자국으로 찢어진 empty 맥주 캔만 굴러다니고 있었습니다.",
            bullet_points=["캠핑장 보관 캔맥주 18개 연쇄 절도", "피해 캠핑객들 집단 멘붕 상황 발생"],
            key_tip="돼지는 알코올 분해 능력이 인간보다 3배 이상 빠르다고 합니다.",
            image_prompt="pig drinking beer near camping tents Australia detailed"
        ),
        SlideBase(
            title="절정: 젖소와의 거친 난투극",
            subtitle="취기에 휩싸인 수돼지의 거침없는 도발",
            story_text="알코올 기운이 올라온 돼지는 캠핑장 주변을 거닐던 거대한 젖소와 눈이 마주치자 갑자기 광기 어린 돌진을 시작했습니다. 돼지는 소의 다리를 받고 주변을 빙빙 돌며 약 15분간 일대 난투극을 벌였습니다.",
            bullet_points=["젖소 상대로 15분간 난투극 지속", "목격자들 shock 상태로 경찰에 신고"],
            key_tip="체중 120kg의 암돼지가 술에 취하면 극도로 호전적으로 변합니다.",
            image_prompt="drunk pig fighting big cow in pasture night action shot"
        ),
        SlideBase(
            title="결말: 나무 밑에서의 기절",
            subtitle="난투극 끝에 찾아온 맥주 폭음의 후폭풍",
            story_text="젖소와의 격렬한 격투를 마친 돼지는 숙취와 피로감을 견디지 못하고 커다란 유칼립투스 나무 밑으로 쓰러졌습니다. 수색대가 현장에 도착했을 때 돼지는 혀를 내민 채 깊은 코골이를 하며 잠들어 있었습니다.",
            bullet_points=["유칼립투스 나무 아래서 기절한 채 발견", "동물 구조대가 안전하게 야생으로 이송"],
            key_tip="해당 사건은 호주 주요 일간지 1면을 장식했습니다.",
            image_prompt="pig sleeping soundly under big eucalyptus tree funny shot"
        )
    ],
    cta=CTASlide(
        title="더 놀라운 세계 동물이 궁금하다면?",
        content="팔로우하고 매주 세계에서 벌어지는 기이한 동물 실화를 받아보세요!",
        image_prompt="cute funny surprised pig looking at camera full quality"
    ),
    caption="🍺 맥주 18캔 마시고 소와 싸운 호주 돼지 실화 😱",
    hashtags=["#세계엽기동물", "#동물실화", "#카드뉴스"]
)

print("Starting mock render test...")
paths = _sync_render_card_news(mock_data, "output/mock_story_test")
print("Render complete! Generated files:", paths)
