from __future__ import annotations

INTRO = [
    "{region}에서 대리운전을 부를 때는 출발 위치를 얼마나 구체적으로 전달하느냐가 배차와 기사 합류 속도에 큰 영향을 줍니다. {landmarks}처럼 사람이 몰리는 지점에서는 상호명만 말하기보다 출구·주차장·도로 방향까지 함께 알려주는 편이 좋습니다.",
    "{region}은 {area_type}의 성격이 뚜렷해 시간대에 따라 차량 흐름과 기사 접근 경로가 달라집니다. 특히 {busy}에는 호출이 겹칠 수 있으므로 출발지와 목적지를 먼저 정리한 뒤 요청하는 것이 효율적입니다.",
    "{region} 대리운전을 알아볼 때 가장 먼저 확인할 것은 현재 차량이 있는 정확한 위치입니다. {landmarks} 주변은 같은 이름의 건물이나 출입구가 여럿일 수 있어 도로명·건물명·주차장 출구를 함께 전달해야 혼선을 줄일 수 있습니다.",
    "{region}에서 늦은 시간 귀가를 준비한다면 호출 전 차량 위치, 목적지, 동승 인원, 결제 방식을 미리 확인해 두는 것이 좋습니다. {area_type} 특성상 {busy}에 기사 도착 시간이 평소보다 길어질 수 있습니다.",
    "{region}은 주변 생활권으로 이동하는 수요가 많은 지역입니다. {routes} 방면처럼 이동 방향이 여러 갈래일 때는 목적지의 동·읍·구까지 정확히 말해야 예상 요금과 배차 가능 여부를 안내받기 쉽습니다.",
    "{region} 대리운전 이용 시에는 ‘어디에서 어디까지 이동하는지’를 한 문장으로 정확히 전달하는 것이 핵심입니다. {landmarks} 인근에서는 차량이 실제로 정차된 장소와 기사와 만날 장소가 다를 수 있으니 두 위치를 구분해 주세요.",
]

ROUTES = [
    "{region}에서 자주 검토하는 이동 방향은 {routes} 방면입니다. 같은 방향이라도 목적지의 세부 주소, 유료도로 이용 여부, 경유지 유무에 따라 거리와 시간이 달라질 수 있습니다.",
    "{routes} 쪽으로 이동할 때는 출발 직전에 최종 목적지를 확정하는 것이 좋습니다. 중간에 경유지를 추가하면 기사 배차 조건이나 요금 안내가 달라질 수 있습니다.",
    "{region} 출발 후 {routes} 방면은 시간대별 정체 차이가 큽니다. 호출할 때 목적지뿐 아니라 원하는 이동 경로나 경유 여부까지 미리 알려주세요.",
    "주요 이동권은 {routes}입니다. 가까워 보이는 지역도 강·터널·교량·간선도로 진입 여부에 따라 실제 주행거리가 달라질 수 있으므로 예상 요금은 호출 시 다시 확인해야 합니다.",
]

PICKUP = [
    "{pickup}",
    "기사와의 합류가 늦어지는 가장 흔한 이유는 출발 지점이 모호하기 때문입니다. {pickup}",
    "호출 위치는 지도 핀만 보내기보다 말로도 한 번 확인하는 것이 안전합니다. {pickup}",
    "차량이 지하주차장에 있다면 주차장 층과 출구 방향도 함께 알려주세요. {pickup}",
]

FARES = [
    "대리운전 요금은 직선거리만으로 정해지지 않습니다. 실제 주행거리, 심야 시간대, 기상 상황, 기사 복귀가 어려운 외곽 목적지, 경유지와 대기 시간 등이 함께 반영될 수 있습니다.",
    "예상 요금을 비교할 때는 출발지와 목적지를 동일하게 입력해야 합니다. 호출 시각, 우천·폭설, 주말·연휴, 장거리 또는 외곽 이동 여부에 따라 안내 금액이 달라질 수 있습니다.",
    "짧은 거리라도 혼잡한 상권이나 차량 진입이 어려운 장소에서는 배차 조건이 달라질 수 있습니다. 반대로 먼 거리라도 기사 수요와 이동 경로에 따라 금액 차이가 생기므로 호출 전 최종 금액을 확인하세요.",
    "요금 안내를 받을 때는 기본요금만 묻기보다 경유지·주차장 출차·톨게이트 비용·대기 시간 포함 여부를 함께 확인하는 편이 좋습니다. 실제 결제 전 기사 또는 업체의 안내 금액을 다시 확인하세요.",
]

SAFETY = [
    "기사 도착 후 차량 번호와 목적지를 다시 확인하고, 운행이 시작되기 전에 결제 방식과 예상 경로를 합의하세요.",
    "차량 상태에 특이사항이 있거나 운전 보조장치 사용법이 복잡하다면 출발 전에 기사에게 알려주세요.",
    "귀중품은 직접 챙기고, 도착 후 차량 문 잠금과 주차 위치를 확인한 뒤 운행을 종료하는 것이 좋습니다.",
    "음주 상태가 심하거나 동승자가 있는 경우 안전벨트 착용과 하차 위치를 미리 정해 두세요.",
]

CSS = """@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
:root{--navy:#10233f;--blue:#245bb8;--gold:#c69335;--ink:#172033;--muted:#5e6878;--bg:#f5f7fb;--card:#fff;--line:#dde3ed}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:'Noto Sans KR',sans-serif;color:var(--ink);background:var(--bg);line-height:1.72;word-break:keep-all}a{color:inherit;text-decoration:none}.site-header{min-height:68px;padding:0 max(20px,5vw);display:flex;align-items:center;justify-content:space-between;gap:20px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}.brand{font-weight:900;color:var(--navy)}nav{display:flex;gap:18px;font-size:14px;font-weight:700;color:var(--muted)}main{overflow:hidden}.hero{padding:88px max(20px,8vw) 76px;background:linear-gradient(135deg,var(--navy),#173c70);color:#fff}.hero>*{max-width:850px;margin-left:auto;margin-right:auto}.eyebrow{margin-top:0;color:#f2c66f;font-weight:800;letter-spacing:.08em;font-size:13px}.hero h1{font-size:clamp(36px,6vw,64px);line-height:1.18;margin:16px auto 24px;letter-spacing:-.055em}.lead{font-size:clamp(17px,2.2vw,21px);color:#dce6f6;max-width:850px}.hero-actions{display:flex;gap:10px;margin-top:32px}.btn{display:inline-flex;min-height:48px;align-items:center;padding:12px 20px;border:1px solid rgba(255,255,255,.35);border-radius:12px;font-weight:800}.btn.primary{background:var(--gold);border-color:var(--gold);color:var(--navy)}.quick-grid{max-width:1100px;margin:-28px auto 0;padding:0 20px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;position:relative}.quick-grid article{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 12px 35px rgba(16,35,63,.09)}.quick-grid span{display:block;font-size:12px;color:var(--blue);font-weight:800;margin-bottom:8px}.quick-grid strong{font-size:15px}.content-section{padding:78px max(20px,5vw)}.content-section>*{max-width:1000px;margin-left:auto;margin-right:auto}.content-section.alt{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.section-head p{color:var(--blue);font-size:12px;font-weight:900;letter-spacing:.16em;margin:0 0 8px}.section-head h2{font-size:clamp(26px,4vw,38px);line-height:1.3;margin:0 0 30px;letter-spacing:-.04em}.prose{font-size:18px}.prose p{margin:0 0 18px}.steps{padding:0;list-style:none;display:grid;grid-template-columns:repeat(5,1fr);gap:13px}.steps li{background:var(--bg);border:1px solid var(--line);border-radius:15px;padding:22px}.steps strong{display:block;margin-bottom:8px;color:var(--navy)}.steps span{font-size:14px;color:var(--muted)}.notice{background:#fff8e9;border:1px solid #ead7aa;border-radius:18px;padding:28px;font-size:17px}.notice p{margin:0 0 12px}.notice p:last-child{margin:0;color:var(--muted);font-size:14px}.near-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.near-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px;transition:.2s}.near-card:hover{transform:translateY(-3px);border-color:var(--blue)}.near-card strong,.near-card span{display:block}.near-card span{font-size:13px;color:var(--muted);margin-top:6px}.faq details{background:#fff;border:1px solid var(--line);border-radius:13px;padding:18px 20px;margin-bottom:10px}.faq summary{font-weight:800;cursor:pointer}.faq details p{color:var(--muted);margin:14px 0 0}.disclosure{max-width:1000px;margin:0 auto 70px;padding:30px;background:var(--navy);color:#fff;border-radius:20px}.disclosure h2{margin-top:0}.disclosure p{color:#dce6f6}.partner{display:inline-flex;margin-top:8px;background:#fee500;color:#191919;padding:12px 18px;border-radius:10px;font-weight:800}footer{padding:28px max(20px,5vw);background:#0a172a;color:#bcc8d8;display:flex;gap:18px;justify-content:center;flex-wrap:wrap;font-size:13px}
@media(max-width:900px){.quick-grid{grid-template-columns:repeat(2,1fr)}.steps{grid-template-columns:repeat(2,1fr)}.near-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.site-header{align-items:flex-start;padding-top:14px;padding-bottom:14px}.site-header nav{gap:10px;font-size:12px}.hero{padding-top:64px}.hero-actions{flex-direction:column;align-items:stretch}.btn{justify-content:center}.quick-grid{grid-template-columns:1fr}.steps{grid-template-columns:1fr}.near-grid{grid-template-columns:1fr}.content-section{padding-top:58px;padding-bottom:58px}.prose{font-size:16px}}"""
