#!/usr/bin/env python3

from collections import defaultdict
from html import unescape
from itertools import combinations
from pathlib import Path
from urllib.parse import quote, unquote
import json
import re

from drive_assets import CSS
from drive_renderer import (
    BASE,
    TODAY,
    build_maps,
    encoded_url_for,
    filename_for,
    render_hub,
    render_invalid,
    render_page,
    slug_for,
)


ROOT = Path(__file__).resolve().parents[2]
DRIVE = ROOT / "misc" / "drive"
DATA = json.loads((Path(__file__).with_name("drive_regions.json")).read_text(encoding="utf-8"))
GROUPS, META = DATA["groups"], DATA["regions"]
REGION_GROUP, ALL_REGIONS = build_maps(GROUPS)


def build_redirects() -> str:
    lines = [
        f"/misc/drive/{quote(filename_for(region))} /misc/drive/{quote(slug_for(region))} 301"
        for region in ALL_REGIONS
    ]
    lines.extend(
        [
            f"/misc/drive/jgdrive.html /misc/drive/{quote(slug_for('정관'))} 301",
            f"/misc/drive/jgdrive /misc/drive/{quote(slug_for('정관'))} 301",
            "/misc/drive/%EC%84%B1%EC%9D%B8%EA%B0%80%EB%8C%80%EB%A6%AC%EC%9A%B4%EC%A0%84.html /misc/drive/ 301",
            "/misc/drive/%EC%84%B1%EC%9D%B8%EA%B0%80%EB%8C%80%EB%A6%AC%EC%9A%B4%EC%A0%84 /misc/drive/ 301",
            "/misc/drive/index.html /misc/drive/ 301",
        ]
    )
    return "\n".join(lines) + "\n"


def sync_root_sitemap(urls: list[str]) -> str:
    sitemap_path = ROOT / "sitemap.xml"
    current = sitemap_path.read_text(encoding="utf-8")
    drive_block = re.compile(
        r"\s*<url>\s*<loc>https://life-helper\.co\.kr/misc/drive/.*?</url>",
        re.DOTALL,
    )
    current = drive_block.sub("", current)
    blocks = "\n".join(
        f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{TODAY}</lastmod>\n  </url>" for url in urls
    )
    return current.replace("</urlset>", f"\n{blocks}\n</urlset>")


def text_blocks_without_disclosure(content: str) -> list[str]:
    content = re.sub(r'<section class="disclosure">.*?</section>', "", content, flags=re.DOTALL)
    blocks = []
    for match in re.findall(r"<(?:p|span)\b[^>]*>(.*?)</(?:p|span)>", content, flags=re.DOTALL):
        text = unescape(re.sub(r"<[^>]+>", "", match)).strip()
        if len(text) >= 70:
            blocks.append(re.sub(r"\s+", " ", text))
    return blocks


def validate(output: dict[Path, str]) -> None:
    assert len(ALL_REGIONS) == 53 and len(set(ALL_REGIONS)) == 53
    assert set(ALL_REGIONS) == set(META)

    titles: set[str] = set()
    descriptions: set[str] = set()
    canonicals: set[str] = set()
    normalized_block_owners: dict[str, list[str]] = defaultdict(list)
    page_fivegrams: dict[str, set[tuple[str, ...]]] = {}

    for region in ALL_REGIONS:
        content = output[DRIVE / filename_for(region)]
        assert content.count("<h1>") == 1
        assert '<meta name="robots" content="index,follow' in content
        assert 'href="./' in content and 'href="./' + quote(slug_for(region)) not in content
        assert ".html\"" not in re.sub(r'<section class="disclosure">.*?</section>', "", content)
        assert "010-0000-0000" not in content
        assert ">NO.1<" not in content and "15,000+" not in content and ">98%<" not in content
        assert content.count("이 페이지 광고·제휴 문의") == 1
        assert (
            f"이 페이지는 {region} 지역의 대리운전 이용 방법을 설명하는 정보성 콘텐츠입니다. "
            "특정 업체의 직접 배차를 보장하지 않으며 실제 운행 가능 여부, 기사 보험, 요금과 결제 조건은 이용 업체에서 확인해야 합니다."
        ) in content

        title = re.search(r"<title>(.*?)</title>", content).group(1)
        description = re.search(r'<meta name="description" content="(.*?)">', content).group(1)
        canonical = re.search(r'<link rel="canonical" href="(.*?)">', content).group(1)
        assert not canonical.endswith(".html")
        assert canonical == encoded_url_for(region)
        titles.add(title)
        descriptions.add(description)
        canonicals.add(canonical)

        for block in text_blocks_without_disclosure(content):
            normalized = block.replace(region, "{지역}")
            normalized_block_owners[normalized].append(region)

        comparison_text = re.sub(r'<section class="disclosure">.*?</section>', "", content, flags=re.DOTALL)
        comparison_text = unescape(re.sub(r"<[^>]+>", " ", comparison_text)).lower()
        words = re.findall(r"[가-힣a-z0-9]+", comparison_text)
        page_fivegrams[region] = set(zip(*(words[offset:] for offset in range(5))))

    assert len(titles) == len(descriptions) == len(canonicals) == 53
    duplicates = {text: owners for text, owners in normalized_block_owners.items() if len(owners) > 1}
    assert not duplicates, f"Repeated substantive copy found: {duplicates}"
    similarities = [
        (
            len(page_fivegrams[left] & page_fivegrams[right])
            / max(1, len(page_fivegrams[left] | page_fivegrams[right])),
            left,
            right,
        )
        for left, right in combinations(ALL_REGIONS, 2)
    ]
    max_similarity, left, right = max(similarities)
    assert max_similarity < 0.50, f"Pages are too similar: {left}/{right}={max_similarity:.3f}"
    print(f"Highest cross-page five-word similarity: {left}/{right}={max_similarity:.3f}")

    invalid = output[DRIVE / "성인가대리운전.html"]
    assert "noindex,follow" in invalid

    for path, content in output.items():
        if path.parent != DRIVE or path.suffix != ".html":
            continue
        for href in re.findall(r'href="(\./[^"#?]+)"', content):
            linked_file = DRIVE / f"{unquote(href.removeprefix('./'))}.html"
            assert linked_file in output, f"Broken regional link in {path.name}: {href}"

    drive_sitemap = output[DRIVE / "sitemap.xml"]
    assert drive_sitemap.count("<url>") == 54
    assert ".html</loc>" not in drive_sitemap
    assert encoded_url_for("정관") in drive_sitemap
    assert "jgdrive" not in drive_sitemap and "%EC%84%B1%EC%9D%B8%EA%B0%80" not in drive_sitemap

    root_sitemap = output[ROOT / "sitemap.xml"]
    root_drive_urls = re.findall(r"<loc>(https://life-helper\.co\.kr/misc/drive/.*?)</loc>", root_sitemap)
    assert len(root_drive_urls) == 54
    assert all(not url.endswith(".html") for url in root_drive_urls)

    redirects = output[ROOT / "_redirects"]
    assert redirects.count(" 301\n") == 58


def main() -> None:
    urls = [BASE] + [encoded_url_for(region) for region in ALL_REGIONS]
    output = {
        DRIVE / "drive-guide.css": CSS,
        DRIVE / "index.html": render_hub(GROUPS, META),
        DRIVE / "성인가대리운전.html": render_invalid(),
        ROOT / "_redirects": build_redirects(),
    }
    for index, region in enumerate(ALL_REGIONS):
        output[DRIVE / filename_for(region)] = render_page(region, index, GROUPS, META, REGION_GROUP)
    output[DRIVE / "sitemap.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>" for url in urls)
        + "\n</urlset>\n"
    )
    output[ROOT / "sitemap.xml"] = sync_root_sitemap(urls)
    output[ROOT / "robots.txt"] = (
        "User-agent: *\nAllow: /\n\n"
        "Sitemap: https://life-helper.co.kr/sitemap.xml\n"
        "Sitemap: https://life-helper.co.kr/misc/drive/sitemap.xml\n"
    )
    validate(output)
    for path, content in output.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated {len(output)} files for {len(ALL_REGIONS)} valid regions.")


if __name__ == "__main__":
    main()
