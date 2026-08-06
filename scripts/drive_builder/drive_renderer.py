from __future__ import annotations
from urllib.parse import quote
import html
import json
from drive_assets import INTRO, ROUTES, PICKUP, FARES, SAFETY

BASE = "https://life-helper.co.kr/misc/drive/"
KAKAO = "https://open.kakao.com/o/sDx5mkHi"
TODAY = "2026-08-06"

def filename_for(region: str) -> str:
    return "jgdrive.html" if region == "정관" else f"{region}대리운전.html"

def encoded_url_for(region: str) -> str:
    return BASE + quote(filename_for(region))

def href_for(region: str) -> str:
    return "./" + quote(filename_for(region))

def build_maps(groups: dict[str, list[str]]) -> tuple[dict[str, str], list[str]]:
    region_group = {region: group for group, regions in groups.items() for region in regions}
    all_regions = [region for regions in groups.values() for region in regions]
    return region_group, all_regions

def neighbors(region: str, groups: dict[str, list[str]], region_group: dict[str, str], count: int = 4) -> list[str]:
    regions = groups[region_group[region]]
    index = regions.index(region)
    return [regions[(index + offset) % len(regions)] for offset in range(1, min(count + 1, len(regions)))]

def render_page(region: str, index: int, groups: dict, meta: dict, region_group: dict) -> str:
    item = meta[region]
    area_type, landmarks, routes = item["area_type"], item["landmarks"], item["routes"]
    busy, pickup = item["busy"], item["pickup"]
    canonical = encoded_url_for(region)
    title = f"{region} 대리운전 이용 가이드 | 호출 위치·요금·심야 이동"
    description = f"{region} 대리운전 호출 전 확인할 출발 위치, 주요 이동 방향, 요금 변동 요소와 심야 이용 주의사항을 정리한 지역별 안내입니다."
    landmarks_text, routes_text = "·".join(landmarks), "·".join(routes)
    intro = INTRO[index % len(INTRO)].format(region=region, area_type=area_type, landmarks=landmarks_text, routes=routes_text, busy=busy)
    route_text = ROUTES[(index * 3) % len(ROUTES)].format(region=region, routes=routes_text)
    pickup_text = PICKUP[(index * 5) % len(PICKUP)].format(pickup=pickup)
    fare_text, safety_text = FARES[(index * 7) % len(FARES)], SAFETY[(index * 11) % len(SAFETY)]
    near_links = "\n".join(
        f'<a class="near-card" href="{href_for(name)}"><strong>{html.escape(name)} 대리운전</strong><span>{html.escape(meta[name]["area_type"])} 안내 보기</span></a>'
        for name in neighbors(region, groups, region_group)
    )
    faq = [
        (f"{region}에서 호출 위치는 어떻게 전달하나요?", pickup),
        (f"{region} 대리운전 요금은 언제 달라지나요?", "거리와 시간대뿐 아니라 날씨, 경유지, 대기 시간, 외곽 목적지와 기사 수급 상황에 따라 달라질 수 있습니다. 호출 전에 최종 예상 금액을 확인하세요."),
        (f"{region}에서 기사 도착이 늦어질 수 있는 시간은 언제인가요?", f"{busy}에는 호출이 몰릴 수 있습니다. 차량이 있는 위치와 만남 지점을 정확히 전달하면 합류 지연을 줄이는 데 도움이 됩니다."),
        ("이 페이지에서 직접 대리운전을 배차하나요?", "아닙니다. 이 페이지는 지역별 이용 정보를 제공하는 안내 페이지이며, 실제 배차·요금·보험·결제 조건은 이용하려는 대리운전 업체나 앱에서 확인해야 합니다."),
    ]
    faq_json = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
    breadcrumb_json = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"올딜","item":"https://life-helper.co.kr/"},{"@type":"ListItem","position":2,"name":"대리운전 지역 가이드","item":BASE},{"@type":"ListItem","position":3,"name":f"{region} 대리운전","item":canonical}]}
    web_json = {"@context":"https://schema.org","@type":"WebPage","name":title,"description":description,"url":canonical,"dateModified":TODAY,"inLanguage":"ko-KR","isPartOf":{"@type":"WebSite","name":"올딜","url":"https://life-helper.co.kr/"}}
    faq_html = "\n".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q,a in faq)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(description, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="article"><meta property="og:site_name" content="올딜"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://life-helper.co.kr/favicon.webp">
<link rel="stylesheet" href="/misc/drive/drive-guide.css">
<script type="application/ld+json">{json.dumps(web_json,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(breadcrumb_json,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(faq_json,ensure_ascii=False,separators=(',',':'))}</script></head>
<body><header class="site-header"><a class="brand" href="/misc/drive/">올딜 대리운전 지역 가이드</a><nav><a href="/">올딜 홈</a><a href="/misc/drive/">전체 지역</a></nav></header><main>
<section class="hero"><p class="eyebrow">{html.escape(region_group[region])} · 지역 이용 정보</p><h1>{html.escape(region)} 대리운전<br>호출 전에 확인할 내용</h1><p class="lead">{html.escape(intro)}</p><div class="hero-actions"><a class="btn primary" href="#checklist">호출 체크리스트</a><a class="btn" href="#nearby">인근 지역 보기</a></div></section>
<section class="quick-grid"><article><span>지역 성격</span><strong>{html.escape(area_type)}</strong></article><article><span>주요 기준점</span><strong>{html.escape(landmarks_text)}</strong></article><article><span>이동 방향</span><strong>{html.escape(routes_text)}</strong></article><article><span>혼잡 가능 시간</span><strong>{html.escape(busy)}</strong></article></section>
<section class="content-section"><div class="section-head"><p>LOCAL GUIDE</p><h2>{html.escape(region)}에서 기사와 빠르게 만나는 방법</h2></div><div class="prose"><p>{html.escape(pickup_text)}</p><p>{html.escape(route_text)}</p><p>{html.escape(safety_text)}</p></div></section>
<section class="content-section alt" id="checklist"><div class="section-head"><p>BEFORE CALL</p><h2>호출 전에 준비할 다섯 가지</h2></div><ol class="steps"><li><strong>차량 위치 확인</strong><span>지하주차장 층, 주차 구역, 출차할 게이트를 확인합니다.</span></li><li><strong>만남 지점 지정</strong><span>차량 접근이 가능한 큰길·역 출구·주차장 출구를 정합니다.</span></li><li><strong>목적지 확정</strong><span>동·읍·구와 상세 주소, 경유지 여부를 미리 정리합니다.</span></li><li><strong>요금과 결제 확인</strong><span>예상 금액, 카드·현금 결제, 추가 비용 포함 여부를 확인합니다.</span></li><li><strong>운행 조건 공유</strong><span>차량 특이사항, 동승자, 유료도로 이용 여부를 기사에게 알립니다.</span></li></ol></section>
<section class="content-section"><div class="section-head"><p>FARE GUIDE</p><h2>예상 요금이 달라지는 이유</h2></div><div class="notice"><p>{html.escape(fare_text)}</p><p>표시되는 금액은 업체별로 다를 수 있으며, 최종 요금은 실제 배차 전에 확인해야 합니다.</p></div></section>
<section class="content-section alt" id="nearby"><div class="section-head"><p>NEARBY AREAS</p><h2>{html.escape(region)} 인근 지역 가이드</h2></div><div class="near-grid">{near_links}</div></section>
<section class="content-section faq"><div class="section-head"><p>FAQ</p><h2>{html.escape(region)} 대리운전 자주 묻는 질문</h2></div>{faq_html}</section>
<section class="disclosure"><h2>안내 사항</h2><p>이 페이지는 {html.escape(region)} 지역의 대리운전 이용 방법을 설명하는 정보성 콘텐츠입니다. 특정 업체의 직접 배차를 보장하지 않으며 실제 운행 가능 여부, 기사 보험, 요금과 결제 조건은 이용 업체에서 확인해야 합니다.</p><a class="partner" href="{KAKAO}" target="_blank" rel="nofollow noopener">이 페이지 광고·제휴 문의</a></section></main>
<footer><a href="/misc/drive/">대리운전 지역 가이드</a><span>최종 수정 {TODAY}</span><span>© 올딜</span></footer></body></html>"""

def render_hub(groups: dict, meta: dict) -> str:
    sections = []
    for group, regions in groups.items():
        cards = "".join(f'<a class="region-card" href="{href_for(region)}"><strong>{html.escape(region)} 대리운전</strong><span>{html.escape(meta[region]["area_type"])}</span></a>' for region in regions)
        sections.append(f'<section class="region-group"><h2>{html.escape(group)}</h2><div class="region-grid">{cards}</div></section>')
    title = "부산·경남·울산 대리운전 지역별 이용 가이드 | 올딜"
    description = "부산, 양산, 김해, 울산, 창원, 진주, 거제 지역의 대리운전 호출 위치와 요금 확인 방법을 지역별로 정리했습니다."
    extra = "<style>.hub-hero{padding:82px max(20px,7vw);background:linear-gradient(135deg,#10233f,#245bb8);color:#fff}.hub-hero>*{max-width:1000px;margin:auto}.hub-hero h1{font-size:clamp(36px,6vw,62px);line-height:1.2}.hub-main{max-width:1100px;margin:auto;padding:60px 20px}.hub-guide{background:#fff;border:1px solid #dde3ed;border-radius:18px;padding:28px;margin-bottom:48px}.region-group{margin-bottom:52px}.region-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.region-card{background:#fff;border:1px solid #dde3ed;border-radius:13px;padding:18px}.region-card strong,.region-card span{display:block}.region-card span{color:#5e6878;font-size:13px}@media(max-width:900px){.region-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.region-grid{grid-template-columns:1fr}}</style>"
    schema = {"@context":"https://schema.org","@type":"CollectionPage","name":title,"description":description,"url":BASE,"dateModified":TODAY,"inLanguage":"ko-KR"}
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{description}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{BASE}"><link rel="stylesheet" href="/misc/drive/drive-guide.css">{extra}<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(",",":"))}</script></head><body><header class="site-header"><a class="brand" href="/misc/drive/">올딜 대리운전 지역 가이드</a><nav><a href="/">올딜 홈</a></nav></header><main><section class="hub-hero"><p>LOCAL DRIVER GUIDE</p><h1>대리운전 호출 전<br>지역별 체크포인트</h1><p>지역별로 기사와 만나기 쉬운 위치, 호출 전 확인할 내용, 요금이 달라지는 요소를 정리한 이용 가이드입니다.</p></section><div class="hub-main"><section class="hub-guide"><h2>빠르게 이용하는 방법</h2><p>차량 위치, 기사와 만날 장소, 최종 목적지, 경유지와 결제 방식을 먼저 정리하세요. 혼잡한 곳에서는 큰길이나 주차장 출구를 지정하는 것이 좋습니다.</p></section>{"".join(sections)}<section class="disclosure"><h2>안내 사항</h2><p>실제 배차 가능 여부, 기사 보험, 요금과 결제 조건은 이용 업체 또는 앱에서 확인해야 합니다.</p><a class="partner" href="{KAKAO}" target="_blank" rel="nofollow noopener">이 페이지 광고·제휴 문의</a></section></div></main><footer><a href="/">올딜 홈</a><span>최종 수정 {TODAY}</span><span>© 올딜</span></footer></body></html>'

def render_invalid() -> str:
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>잘못 생성된 대리운전 지역 주소 안내 | 올딜</title><meta name="description" content="지역명이 확인되지 않아 검색 대상에서 제외된 주소입니다."><meta name="robots" content="noindex,follow"><link rel="canonical" href="{BASE}"><meta http-equiv="refresh" content="5;url={BASE}"><link rel="stylesheet" href="/misc/drive/drive-guide.css"></head><body><header class="site-header"><a class="brand" href="/misc/drive/">올딜 대리운전 지역 가이드</a></header><main><section class="hero"><p class="eyebrow">ADDRESS NOTICE</p><h1>지역명이 확인되지 않은 주소입니다</h1><p class="lead">잘못된 지역명으로 생성되어 검색 대상에서 제외했습니다. 전체 지역 가이드로 이동해 주세요.</p><div class="hero-actions"><a class="btn primary" href="/misc/drive/">전체 지역 가이드 보기</a></div></section></main><footer><span>© 올딜</span></footer></body></html>'
