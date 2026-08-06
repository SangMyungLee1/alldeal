#!/usr/bin/env python3
from pathlib import Path
import json
from drive_assets import CSS
from drive_renderer import BASE, TODAY, build_maps, encoded_url_for, filename_for, render_hub, render_invalid, render_page

ROOT = Path(__file__).resolve().parents[2]
DRIVE = ROOT / "misc" / "drive"
DATA = json.loads((Path(__file__).with_name("drive_regions.json")).read_text(encoding="utf-8"))
GROUPS, META = DATA["groups"], DATA["regions"]
REGION_GROUP, ALL_REGIONS = build_maps(GROUPS)

def validate(output: dict[Path, str]) -> None:
    assert len(ALL_REGIONS) == 53 and len(set(ALL_REGIONS)) == 53
    for region in ALL_REGIONS:
        content = output[DRIVE / filename_for(region)]
        assert content.count("<h1>") == 1
        assert '<meta name="robots" content="index,follow' in content
        assert '<link rel="canonical"' in content
        assert "010-0000-0000" not in content
        assert ">NO.1<" not in content and "15,000+" not in content and ">98%<" not in content
    assert "noindex,follow" in output[DRIVE / "성인가대리운전.html"]

def main() -> None:
    output = {
        DRIVE / "drive-guide.css": CSS,
        DRIVE / "index.html": render_hub(GROUPS, META),
        DRIVE / "성인가대리운전.html": render_invalid(),
    }
    for index, region in enumerate(ALL_REGIONS):
        output[DRIVE / filename_for(region)] = render_page(region, index, GROUPS, META, REGION_GROUP)
    urls = [BASE] + [encoded_url_for(region) for region in ALL_REGIONS]
    output[DRIVE / "sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>" for url in urls) + "\n</urlset>\n"
    output[ROOT / "robots.txt"] = "User-agent: *\nAllow: /\n\nSitemap: https://life-helper.co.kr/sitemap.xml\nSitemap: https://life-helper.co.kr/misc/drive/sitemap.xml\n"
    validate(output)
    for path, content in output.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated {len(output)} files for {len(ALL_REGIONS)} valid regions.")

if __name__ == "__main__":
    main()
