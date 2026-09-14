#!/usr/bin/env python3
"""작업판(tools/asset-board.html)의 프롬프트를 style/prompts-antigravity.md 에서 채운다.

작업판은 프롬프트를 직접 갖고 있지 않다. md 가 원본이고 작업판은 그걸 보여주는
화면이다. md 를 고쳤으면 이걸 돌려야 작업판이 따라온다.

    python3 tools/build_asset_board.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "style" / "prompts-antigravity.md"
HTML = ROOT / "tools" / "asset-board.html"

BEGIN = "// BUILD:MESSAGES"
END = "// BUILD:END"

# md 에 없는 것들 — 작업판에서만 쓰는 한 줄 설명과 확인 항목.
EXTRA = {
    1: ("밑그림 1장 + 포즈 2장. <b>첫 장이 나머지의 기준</b>이다.",
        ["밑그림 세 장면의 <b>수염·옷·지팡이가 같은가</b>",
         "포즈 둘 다 <b>왼쪽</b>을 보는가",
         "발밑에 그림자·바닥선이 없는가"]),
    2: ("밑그림 1장 + 포즈 4장. <b>첫 장이 나머지의 기준</b>이다.",
        ["밑그림 세 장면이 <b>같은 사람인가</b>",
         "포즈 넷 다 <b>오른쪽</b>을 보는가",
         "네 장의 크기와 여백이 같은가"]),
    3: ("도끼 3자루는 <b>재질만 다른 같은 도끼</b>. 빛은 검정 배경.",
        ["도끼 셋이 <b>같은 방향·같은 크기</b>인가",
         "빛(4번)의 배경이 <b>완전한 검정</b>인가 — 회색 금지",
         "손·그림자가 없는가"]),
    4: ("가로로 긴 배경 4장. 빛나는 연못을 먼저 만들고 낮 연못이 그걸 따라간다.",
        ["<b>사람이 없는가</b>",
         "연못 두 장이 <b>같은 장소로 보이는가</b>",
         "하단 가운데가 비어 있는가"]),
    5: ("글자 없이 그림만으로 고르는 아이콘 6장.",
        ["<b>글자 없이</b> 뭔지 알아보겠는가",
         "1~3끼리, 4~6끼리 크기가 같은가",
         "분홍 배경이 얼룩 없이 고른가"]),
}


def parse():
    text = MD.read_text(encoding="utf-8")
    out = []
    # "## ① 산신령 — 밑그림 + 포즈 2" 다음의 ``` 블록
    for m in re.finditer(r"^## ([①②③④⑤])\s*(.+?)\n+```\n(.*?)\n```",
                         text, re.S | re.M):
        mark, title, body = m.group(1), m.group(2).strip(), m.group(3)
        files = re.findall(r"^Save as:\s*(\S+)", body, re.M)
        if not files:
            sys.exit(f"{mark}: Save as: 줄이 없다")
        desc, qc = EXTRA[len(out) + 1]
        head = title.split("—", 1)
        out.append({
            "mark": mark,
            # "소품 4" 의 4, "산신령" 뒤의 장수는 칩이 보여주므로 제목에서 뺀다
            "title": re.sub(r"\s*\d+$", "", head[0].strip()),
            "sub": head[1].strip() if len(head) > 1 else "",
            "desc": desc,
            "qc": qc,
            "files": files,
            "p": body,
        })
    if len(out) != 5:
        sys.exit(f"메시지 5개여야 하는데 {len(out)}개를 찾았다")
    return out


def main():
    msgs = parse()
    total = sum(len(m["files"]) for m in msgs)
    html = HTML.read_text(encoding="utf-8")
    i, j = html.index(BEGIN), html.index(END)
    block = "%s — style/prompts-antigravity.md 에서 생성. 직접 고치지 말 것.\nconst M = %s;\n" % (
        BEGIN, json.dumps(msgs, ensure_ascii=False, indent=1))
    HTML.write_text(html[:i] + block + html[j:], encoding="utf-8")
    print("작업판 갱신: 메시지 %d개, 그림 %d장" % (len(msgs), total))
    for m in msgs:
        print("  %s %-6s %d장" % (m["mark"], m["title"], len(m["files"])))


if __name__ == "__main__":
    main()
