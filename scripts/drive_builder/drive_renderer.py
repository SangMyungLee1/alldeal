from __future__ import annotations

from datetime import date
from urllib.parse import quote
import html
import json

from drive_assets import CSS


BASE = "https://life-helper.co.kr/misc/drive/"
KAKAO = "https://open.kakao.com/o/sDx5mkHi"
TODAY = date.today().isoformat()


def filename_for(region: str) -> str:
    """Return the physical asset filename used by Cloudflare."""
    return f"{region}대리운전.html"


def slug_for(region: str) -> str:
    """Return the one canonical, extensionless URL slug."""
    return f"{region}대리운전"


def encoded_url_for(region: str) -> str:
    return BASE + quote(slug_for(region))


def href_for(region: str) -> str:
    return "./" + quote(slug_for(region))


def build_maps(groups: dict[str, list[str]]) -> tuple[dict[str, str], list[str]]:
    region_group = {region: group for group, regions in groups.items() for region in regions}
    all_regions = [region for regions in groups.values() for region in regions]
    return region_group, all_regions


def neighbors(region: str, groups: dict[str, list[str]], region_group: dict[str, str], count: int = 4) -> list[str]:
    regions = groups[region_group[region]]
    index = regions.index(region)
    return [regions[(index + offset) % len(regions)] for offset in range(1, min(count + 1, len(regions)))]


def pick(items: tuple[str, ...], index: int, step: int = 1) -> str:
    return items[(index * step) % len(items)]


INTRO_PATTERNS = (
    "{region}에서 대리운전을 부를 때는 {landmark0}이라는 지명만 보내기보다 차량이 서 있는 도로와 출차 방향을 함께 적는 편이 낫습니다. {area_type} 특성상 {busy}에는 보행자와 차량이 한곳에 몰릴 수 있으므로 만남 지점을 먼저 정해 두세요.",
    "{region}은 {landmark0}와 {landmark1}을 중심으로 출발 위치가 나뉩니다. 같은 {area_type} 안에서도 주차장 출구와 도로 방향이 다르면 기사 이동 경로가 달라지므로, {busy}에는 차량 위치를 한 번 더 확인하는 것이 좋습니다.",
    "{landmark0} 인근에서 출발하는 {region} 대리운전은 ‘어느 건물인가’보다 ‘어느 출구로 차가 나오는가’를 정확히 전하는 것이 핵심입니다. 특히 {busy}에는 {route0} 방면 차량과 주변 교통이 겹칠 수 있습니다.",
    "{region}의 {area_type}에서 호출을 준비한다면 출발지는 {landmark0}, 이동 방향은 {route0}처럼 두 단계로 나눠 전달해 보세요. {landmark1} 주변까지 범위를 좁혀 주면 기사와 서로 다른 골목에서 기다리는 일을 줄일 수 있습니다.",
    "{region}에서는 {landmark0}과 {landmark1} 사이의 실제 차량 위치를 먼저 확인해야 합니다. {busy}에는 호출량뿐 아니라 출차 정체도 생길 수 있어, {route0} 방면으로 나갈 도로까지 정한 뒤 요청하는 편이 효율적입니다.",
    "{area_type}인 {region}은 목적지가 같아도 출발 지점에 따라 초반 이동이 달라질 수 있습니다. {landmark0} 근처인지 {landmark1} 쪽인지, 그리고 {route0} 방향인지까지 적으면 현장 합류가 한결 분명해집니다.",
    "{region} 대리운전 이용 전에는 차량이 {landmark0} 주변의 지상 도로에 있는지, 별도 주차장 안에 있는지부터 살펴보세요. {busy}에는 짧은 위치 확인 차이가 대기 시간으로 이어질 수 있습니다.",
    "{landmark0}을 기준으로 움직이는 {region}에서는 호출 메시지에 건물명, 출차 지점, {route0} 방면 목적지를 순서대로 적는 것이 실용적입니다. 이 지역은 {area_type}이라 시간대에 따라 만남 장소를 큰길 쪽으로 조정할 필요가 있습니다.",
)


MEETING_PATTERNS = (
    "{pickup} 차량은 {landmark0}에서 {landmark1} 쪽으로 이동할 수 있으므로 기사에게 현재 보이는 상호나 주차 구역도 덧붙이세요.",
    "{pickup} 호출을 넣은 뒤에는 {landmark0} 기준 어느 편 도로인지 확인해 두면 {landmark1} 주변에서 엇갈릴 가능성을 줄일 수 있습니다.",
    "{pickup} 기사 도착 알림을 받으면 {landmark0} 주변의 정차 가능 지점으로 이동할 수 있는지도 확인하세요.",
    "{pickup} 특히 {landmark1}과 연결되는 골목에서는 차량 번호와 진행 방향을 함께 확인하는 편이 안전합니다.",
    "{pickup} {landmark0}처럼 출입구가 나뉘는 곳에서는 호출 후 임의로 반대편 도로로 이동하지 말고 변경 위치를 다시 알려주세요.",
    "{pickup} {landmark1} 주변에서 위치를 바꿔야 한다면 새 만남 지점을 건물명과 도로명으로 다시 전달하는 것이 좋습니다.",
    "{pickup} 현장에서는 {landmark0}을 등지고 있는지 마주 보고 있는지처럼 방향 정보를 더하면 합류가 빨라집니다.",
    "{pickup} {landmark0}과 {landmark1} 중 어느 쪽에 가까운지 한 번 더 말하면 기사 위치 확인에 도움이 됩니다.",
)


ROUTE_PATTERNS = (
    "{region}에서 많이 확인하는 이동 방향은 {route0}, {route1}, {route2}입니다. 목적지의 동·읍·구와 함께 경유지 여부를 먼저 말해야 실제 주행 조건을 기준으로 안내받을 수 있습니다.",
    "출발 뒤 {route0} 또는 {route1} 쪽으로 이동한다면 유료도로 이용 여부와 원하는 경유지를 호출 단계에서 정하세요. {route2} 방면은 목적지 범위가 넓을 수 있어 상세 주소가 필요합니다.",
    "{region}에서 {route0} 방향으로 갈 때와 {route2} 방향으로 갈 때는 진입 도로가 달라질 수 있습니다. 출발 후 목적지를 바꾸기보다 호출 전에 최종 도착지를 확정하는 편이 좋습니다.",
    "주요 이동권은 {route0}·{route1}·{route2}로 나뉩니다. {region} 출발이라고만 적지 말고 최종 목적지와 중간 정차 여부를 함께 전달해야 예상 요금과 기사 수락 조건을 비교하기 쉽습니다.",
    "{route0} 방면 목적지라면 {region}의 어느 출구에서 출발하는지에 따라 첫 진입로가 달라질 수 있습니다. {route1}이나 {route2}로 이동할 때도 정확한 주소를 기준으로 견적을 확인하세요.",
    "{region}에서 이어지는 대표 방향은 {route0}, {route1}, {route2}입니다. 같은 방향 표기라도 실제 목적지가 외곽이면 거리와 기사 복귀 여건이 달라지므로 시·군·구까지 분명히 알려주세요.",
    "목적지가 {route0} 쪽인지 {route2} 쪽인지 먼저 정하면 {region} 현장에서 어느 도로로 출차할지도 판단하기 쉽습니다. 경유지가 있다면 기사 배정 전에 순서대로 공유하세요.",
    "{region} 출발 후 {route1} 또는 {route2}로 이동할 계획이라면 예상 경로만 보고 요금을 단정하지 마세요. 실제 주소, 호출 시각, 경유 조건을 같은 기준으로 놓고 확인해야 합니다.",
)


TIMING_PATTERNS = (
    "{busy}에는 {landmark0} 주변 호출과 일반 차량 이동이 겹칠 수 있습니다. 급하게 위치를 바꾸기보다 정차 가능한 한 지점을 정해 기사에게 유지해 주세요.",
    "{region}에서 대기 시간이 길어질 가능성이 큰 때는 {busy}입니다. 이 시간에는 {landmark1}보다 차량 진입이 쉬운 큰길을 만남 지점으로 잡는 방법도 고려할 수 있습니다.",
    "{busy}에는 {landmark0} 인근의 출차 속도가 평소와 다를 수 있습니다. 기사 도착 예정 시간과 주차장 출차 시간을 따로 생각해 여유 있게 호출하세요.",
    "{landmark0} 기준으로는 {busy}에 현장 혼잡이 커질 수 있습니다. 호출이 잡힌 뒤 만남 지점을 바꾸면 기사도 우회할 수 있으니 변경 사항을 바로 공유하세요.",
    "{region}의 혼잡 가능 시간은 {busy}입니다. 이때는 {landmark0} 앞 정차가 어려울 수 있어 가까운 주차장 출구나 교차로를 대안으로 정해 두면 좋습니다.",
    "{busy}에는 {landmark0}과 {landmark1} 사이의 짧은 이동도 오래 걸릴 수 있습니다. 배차 완료 시각과 실제 승차 시각이 다를 수 있다는 점을 감안하세요.",
    "{region}에서는 {busy}에 호출 수요와 도로 정체를 함께 살펴야 합니다. 목적지 도착 시간을 맞춰야 한다면 {landmark0}에서의 출차 시간을 넉넉히 잡으세요.",
    "{landmark1} 주변을 포함해 {busy}에는 기사 접근 경로가 달라질 수 있습니다. 호출 후에는 휴대전화 알림을 확인하고 차량 위치 설명을 바로 보완할 수 있게 준비하세요.",
)


FARE_PATTERNS = (
    "{region}에서 {route0} 방면으로 이동할 때의 요금은 거리만으로 고정되지 않습니다. {busy}의 기사 수급, {landmark0} 주변 대기, 경유지와 유료도로 선택을 포함해 배차 전에 최종 금액을 확인하세요.",
    "{landmark0} 출발과 {landmark1} 출발은 같은 {region} 안에서도 실제 주행 시작점이 다릅니다. 목적지가 {route1} 쪽이라면 상세 주소와 결제 수단, 추가 정차 여부를 같은 조건으로 전달해 예상 금액을 확인하세요.",
    "{region}의 {area_type}에서는 출차 대기와 심야 수요가 요금 안내에 함께 반영될 수 있습니다. {route0} 또는 {route2} 이동 전 업체가 제시한 금액에 경유·대기 비용이 포함됐는지 물어보세요.",
    "{route0}·{route1} 방면을 비교할 때는 직선거리보다 실제 출발 도로와 목적지 주소가 중요합니다. {region}에서 호출한 뒤 목적지를 바꾸면 요금도 달라질 수 있으니 배차 전에 확정하세요.",
    "{busy}의 {region}에서는 기사 수급에 따라 평소와 다른 금액이 안내될 수 있습니다. {landmark0}에서 출발해 {route2}로 갈 경우 유료도로와 경유지 포함 여부까지 확인한 뒤 요청하세요.",
    "{region} 출발 요금은 {landmark0} 주변의 대기 여건, {route1} 방면 거리, 호출 시각에 따라 달라질 수 있습니다. 카드나 현금 등 결제 방식도 배차 전 안내 내용과 일치하는지 확인하세요.",
    "{area_type}에서 출발하는 만큼 {landmark0} 주차장 출차 시간과 {route0} 방면 실제 이동 조건을 함께 봐야 합니다. 앱이나 업체의 최초 표시 금액이 최종 금액인지 반드시 확인하세요.",
    "{region}에서 {route2} 쪽으로 장거리 이동하거나 중간 정차를 추가하면 처음 안내받은 조건이 바뀔 수 있습니다. 출발지는 {landmark0}, 목적지는 상세 주소로 입력해 최종 요금을 비교하세요.",
)


SAFETY_PATTERNS = (
    "{landmark0}에서 기사와 만난 뒤 차량 번호와 최종 목적지를 서로 확인하세요. {region}에서 출발하기 전 결제 방식과 예상 경로까지 맞춰 두면 운행 종료 후 혼선을 줄일 수 있습니다.",
    "{region}의 {landmark1} 주변에서는 차량 문을 열기 전에 배정된 기사와 차량 정보가 맞는지 확인하세요. 차 안의 귀중품과 주차권도 출발 전에 직접 챙기는 편이 좋습니다.",
    "{landmark0} 주차장에서 출차한다면 주차요금 정산 여부와 차량 특이사항을 기사에게 먼저 알려주세요. {route0} 방면 운행을 시작하기 전 안전벨트도 확인하세요.",
    "{region} 호출이 완료돼도 보험 적용 범위와 운행 조건은 이용 업체에서 확인해야 합니다. {landmark1}에서 승차할 때 배정 정보가 다르면 운행을 시작하기 전에 업체에 문의하세요.",
    "{landmark0} 인근의 어두운 골목보다 조명이 있고 차량 정차가 가능한 곳에서 만나는 편이 안전합니다. {region} 출발 후 목적지를 변경할 때는 기사와 요금 조건을 다시 확인하세요.",
    "{region}에서 동승자가 있거나 차량 조작에 특이사항이 있다면 {landmark0}을 출발하기 전에 기사에게 알리세요. 운행이 끝난 뒤에는 주차 위치와 문 잠금 상태를 직접 확인하세요.",
    "기사 도착 알림만 보고 바로 출발하지 말고 {region} 호출 내역의 기사 정보와 차량을 대조하세요. {landmark1} 주변에서 다른 기사와 혼동되지 않도록 목적지도 다시 확인하는 것이 좋습니다.",
    "{landmark0}에서 만남 장소가 바뀌었다면 앱이나 업체에 기록이 남도록 새 위치를 전달하세요. {region} 운행 시작 전 보험과 결제 조건을 확인하는 책임은 이용자에게 있습니다.",
)


def render_page(region: str, index: int, groups: dict, meta: dict, region_group: dict) -> str:
    item = meta[region]
    area_type = item["area_type"]
    landmarks = item["landmarks"]
    routes = item["routes"]
    busy = item["busy"]
    pickup = item["pickup"]
    values = {
        "region": region,
        "area_type": area_type,
        "landmark0": landmarks[0],
        "landmark1": landmarks[1],
        "landmark2": landmarks[2],
        "route0": routes[0],
        "route1": routes[1],
        "route2": routes[2],
        "busy": busy,
        "pickup": pickup,
    }
    canonical = encoded_url_for(region)
    title = f"{region} 대리운전 | {landmarks[0]} 출발·{routes[0]} 이동 전 확인"
    description = (
        f"{region} {area_type}에서 대리운전을 이용할 때 필요한 {landmarks[0]} 인근 만남 위치, "
        f"{routes[0]} 방면 이동, {busy} 호출 요금 확인 방법을 정리했습니다."
    )
    intro = pick(INTRO_PATTERNS, index).format(**values)
    meeting_text = pick(MEETING_PATTERNS, index, 3).format(**values)
    route_text = pick(ROUTE_PATTERNS, index, 5).format(**values)
    timing_text = pick(TIMING_PATTERNS, index, 7).format(**values)
    fare_text = pick(FARE_PATTERNS, index, 3).format(**values)
    safety_text = (
        pick(SAFETY_PATTERNS, index, 5).format(**values)
        + f" {landmarks[2]} 주변에서 {routes[0]} 방면으로 나가기 전에는 배정 정보와 실제 출차 방향이 맞는지도 살펴보세요."
    )
    landmarks_text = "·".join(landmarks)
    routes_text = "·".join(routes)

    near_links = "\n".join(
        f'<a class="near-card" href="{href_for(name)}"><strong>{html.escape(name)} 대리운전</strong><span>{html.escape(meta[name]["landmarks"][0])} 출발 안내</span></a>'
        for name in neighbors(region, groups, region_group)
    )

    checklist = [
        (f"{landmarks[0]} 차량 위치", f"{landmarks[0]}의 어느 도로·주차장·출구에 차가 있는지 확인하고 {region} 호출 정보에 적습니다."),
        (f"{landmarks[1]} 만남 지점", pickup),
        (f"{routes[0]} 목적지 방향", f"{routes[0]} 방면의 상세 목적지와 {routes[1]} 경유 여부를 기사 배정 전에 확정합니다."),
        (f"{busy} 시간 확인", f"{busy}에는 {landmarks[2]} 주변 접근이 늦어질 수 있으므로 출차와 대기 시간을 따로 계산합니다."),
        (f"{region} 요금·결제 확인", f"{region}에서 {routes[2]} 쪽으로 이동할 최종 금액, 결제 수단, 대기·경유 비용 포함 여부를 확인합니다."),
    ]
    checklist_html = "".join(
        f"<li><strong>{html.escape(label)}</strong><span>{html.escape(text)}</span></li>" for label, text in checklist
    )

    faq = [
        (
            f"{landmarks[0]} 근처에서는 어디를 만남 지점으로 잡나요?",
            f"{pickup} 호출 후에는 {landmarks[1]} 쪽인지 {landmarks[2]} 쪽인지도 기사에게 알려주세요.",
        ),
        (
            f"{region}에서 {routes[0]} 방면 요금은 무엇을 확인해야 하나요?",
            f"{landmarks[0]} 출발 위치와 {routes[0]} 방면 상세 주소, {routes[1]} 경유 여부, 결제 수단을 같은 조건으로 전달하고 최종 금액을 확인해야 합니다.",
        ),
        (
            f"{busy}에 호출하면 무엇이 달라질 수 있나요?",
            f"{busy}에는 {landmarks[2]} 주변의 차량 접근과 기사 수급이 평소와 다를 수 있습니다. {region}에서 출차할 시간까지 포함해 여유 있게 요청하세요.",
        ),
        (
            f"{landmarks[1]}에서 출발 전 확인할 안전 항목은 무엇인가요?",
            f"{region} 호출 내역의 기사 정보, 차량 번호, 목적지, 보험·결제 조건을 확인하세요. "
            f"{area_type}인 {landmarks[1]}에서 {routes[2]} 방면으로 출발하기 전에는 차량 특이사항을 알리고, "
            f"운행을 마친 뒤 주차 위치와 문 잠금도 직접 살펴야 합니다.",
        ),
    ]
    faq_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq
        ],
    }
    breadcrumb_json = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "올딜", "item": "https://life-helper.co.kr/"},
            {"@type": "ListItem", "position": 2, "name": "대리운전 지역 가이드", "item": BASE},
            {"@type": "ListItem", "position": 3, "name": f"{region} 대리운전", "item": canonical},
        ],
    }
    web_json = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "dateModified": TODAY,
        "inLanguage": "ko-KR",
        "isPartOf": {"@type": "WebSite", "name": "올딜", "url": "https://life-helper.co.kr/"},
    }
    faq_html = "\n".join(
        f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in faq
    )

    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(description, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="article"><meta property="og:site_name" content="올딜"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://life-helper.co.kr/favicon.webp">
<link rel="stylesheet" href="/misc/drive/drive-guide.css">
<script type="application/ld+json">{json.dumps(web_json, ensure_ascii=False, separators=(',', ':'))}</script><script type="application/ld+json">{json.dumps(breadcrumb_json, ensure_ascii=False, separators=(',', ':'))}</script><script type="application/ld+json">{json.dumps(faq_json, ensure_ascii=False, separators=(',', ':'))}</script></head>
<body><header class="site-header"><a class="brand" href="/misc/drive/">올딜 대리운전 지역 가이드</a><nav><a href="/">올딜 홈</a><a href="/misc/drive/">전체 지역</a></nav></header><main>
<section class="hero"><p class="eyebrow">{html.escape(region_group[region])} · {html.escape(area_type)}</p><h1>{html.escape(region)} 대리운전<br>{html.escape(landmarks[0])} 출발 준비</h1><p class="lead">{html.escape(intro)}</p><div class="hero-actions"><a class="btn primary" href="#checklist">{html.escape(region)} 호출 순서</a><a class="btn" href="#nearby">{html.escape(region_group[region])} 인근 보기</a></div></section>
<section class="quick-grid"><article><span>{html.escape(region)} 지역 성격</span><strong>{html.escape(area_type)}</strong></article><article><span>출발 기준점</span><strong>{html.escape(landmarks_text)}</strong></article><article><span>목적지 방향</span><strong>{html.escape(routes_text)}</strong></article><article><span>주의할 시간</span><strong>{html.escape(busy)}</strong></article></section>
<section class="content-section"><div class="section-head"><p>{html.escape(region.upper())} MEETING GUIDE</p><h2>{html.escape(landmarks[0])} 근처에서 기사와 엇갈리지 않는 법</h2></div><div class="prose"><p>{html.escape(meeting_text)}</p><p>{html.escape(route_text)}</p><p>{html.escape(safety_text)}</p></div></section>
<section class="content-section alt" id="checklist"><div class="section-head"><p>{html.escape(region.upper())} BEFORE CALL</p><h2>{html.escape(region)}에서 {html.escape(routes[0])} 방면으로 출발하기 전</h2></div><ol class="steps">{checklist_html}</ol></section>
<section class="content-section"><div class="section-head"><p>{html.escape(region.upper())} FARE CHECK</p><h2>{html.escape(landmarks[0])} 출발 요금을 확인하는 기준</h2></div><div class="notice"><p>{html.escape(fare_text)}</p><p>{html.escape(region)} 페이지의 안내는 고정 요금표가 아닙니다. 실제 배차 전에 이용 업체가 제시하는 최종 금액과 결제 조건을 확인하세요.</p></div></section>
<section class="content-section alt"><div class="section-head"><p>{html.escape(region.upper())} TIMING NOTE</p><h2>{html.escape(busy)}에 늦어질 수 있는 지점</h2></div><div class="prose"><p>{html.escape(timing_text)}</p><p>{html.escape(region)}에서는 {html.escape(landmarks[2])} 주변 상황과 차량 출차 시간을 함께 보고 호출 시점을 정하는 편이 좋습니다.</p></div></section>
<section class="content-section" id="nearby"><div class="section-head"><p>{html.escape(region_group[region].upper())} NEARBY AREAS</p><h2>{html.escape(region)} 다음으로 확인할 인근 출발지</h2></div><div class="near-grid">{near_links}</div></section>
<section class="content-section faq"><div class="section-head"><p>{html.escape(region.upper())} FAQ</p><h2>{html.escape(landmarks[0])} 출발 기준 자주 묻는 내용</h2></div>{faq_html}</section>
<section class="disclosure"><h2>안내 사항</h2><p>이 페이지는 {html.escape(region)} 지역의 대리운전 이용 방법을 설명하는 정보성 콘텐츠입니다. 특정 업체의 직접 배차를 보장하지 않으며 실제 운행 가능 여부, 기사 보험, 요금과 결제 조건은 이용 업체에서 확인해야 합니다.</p><a class="partner" href="{KAKAO}" target="_blank" rel="nofollow noopener">이 페이지 광고·제휴 문의</a></section></main>
<footer><a href="/misc/drive/">대리운전 지역 가이드</a><span>최종 수정 {TODAY}</span><span>© 올딜</span></footer></body></html>"""


def render_hub(groups: dict, meta: dict) -> str:
    sections = []
    for group, regions in groups.items():
        cards = "".join(
            f'<a class="region-card" href="{href_for(region)}"><strong>{html.escape(region)} 대리운전</strong><span>{html.escape(meta[region]["landmarks"][0])} 출발 · {html.escape(meta[region]["area_type"])}</span></a>'
            for region in regions
        )
        sections.append(f'<section class="region-group"><h2>{html.escape(group)}</h2><div class="region-grid">{cards}</div></section>')
    title = "부산·경남·울산 대리운전 지역별 이용 가이드 | 올딜"
    description = "부산, 양산, 김해, 울산, 창원, 진주, 거제 53개 지역의 대리운전 호출 위치와 요금 확인 방법을 지역별로 정리했습니다."
    extra = "<style>.hub-hero{padding:82px max(20px,7vw);background:linear-gradient(135deg,#10233f,#245bb8);color:#fff}.hub-hero>*{max-width:1000px;margin:auto}.hub-hero h1{font-size:clamp(36px,6vw,62px);line-height:1.2}.hub-main{max-width:1100px;margin:auto;padding:60px 20px}.hub-guide{background:#fff;border:1px solid #dde3ed;border-radius:18px;padding:28px;margin-bottom:48px}.region-group{margin-bottom:52px}.region-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.region-card{background:#fff;border:1px solid #dde3ed;border-radius:13px;padding:18px}.region-card strong,.region-card span{display:block}.region-card span{color:#5e6878;font-size:13px}@media(max-width:900px){.region-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.region-grid{grid-template-columns:1fr}}</style>"
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": description, "url": BASE, "dateModified": TODAY, "inLanguage": "ko-KR"}
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{description}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{BASE}"><link rel="stylesheet" href="/misc/drive/drive-guide.css">{extra}<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script></head><body><header class="site-header"><a class="brand" href="/misc/drive/">올딜 대리운전 지역 가이드</a><nav><a href="/">올딜 홈</a></nav></header><main><section class="hub-hero"><p>LOCAL DRIVER GUIDE</p><h1>대리운전 호출 전<br>53개 지역별 확인 사항</h1><p>각 지역의 실제 기준점, 차량 만남 위치, 주요 이동 방향과 혼잡 시간을 기준으로 필요한 내용을 골라 보세요.</p></section><div class="hub-main"><section class="hub-guide"><h2>지역 페이지 이용 방법</h2><p>출발 지역을 고른 뒤 차량이 있는 건물·주차장·도로 방향을 확인하세요. 목적지와 경유지를 확정하고 이용 업체에서 최종 요금, 보험, 결제 조건을 확인해야 합니다.</p></section>{"".join(sections)}<section class="disclosure"><h2>안내 사항</h2><p>실제 배차 가능 여부, 기사 보험, 요금과 결제 조건은 이용 업체 또는 앱에서 확인해야 합니다.</p><a class="partner" href="{KAKAO}" target="_blank" rel="nofollow noopener">이 페이지 광고·제휴 문의</a></section></div></main><footer><a href="/">올딜 홈</a><span>최종 수정 {TODAY}</span><span>© 올딜</span></footer></body></html>'


def render_invalid() -> str:
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>잘못 생성된 대리운전 지역 주소 안내 | 올딜</title><meta name="description" content="지역명을 확인할 수 없어 검색 대상에서 제외한 주소입니다."><meta name="robots" content="noindex,follow"><link rel="canonical" href="{BASE}"><meta http-equiv="refresh" content="5;url={BASE}"><link rel="stylesheet" href="/misc/drive/drive-guide.css"></head><body><header class="site-header"><a class="brand" href="/misc/drive/">올딜 대리운전 지역 가이드</a></header><main><section class="hero"><p class="eyebrow">ADDRESS NOTICE</p><h1>지역명을 확인할 수 없는 주소입니다</h1><p class="lead">잘못된 지역명으로 생성되어 검색 대상에서 제외했습니다. 전체 지역 가이드로 이동해 주세요.</p><div class="hero-actions"><a class="btn primary" href="/misc/drive/">전체 지역 가이드 보기</a></div></section></main><footer><span>© 올딜</span></footer></body></html>'
