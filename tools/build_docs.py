"""Regenerate docs/food.md, docs/guide.md and food.kml from data/*.json.

Usage: python3 tools/build_docs.py
"""
import json, pathlib
from urllib.parse import quote_plus
from xml.sax.saxutils import escape

GM = "https://www.google.com/maps/search/?api=1&query="
ROOT = pathlib.Path(__file__).resolve().parent.parent
food = json.loads((ROOT / "data/food.json").read_text())
guide = json.loads((ROOT / "data/guide.json").read_text())
grocery = json.loads((ROOT / "data/grocery.json").read_text())
fun = json.loads((ROOT / "data/fun.json").read_text())


def gq(r):
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f"{r['name']} {r['addr']} Montreal")


def dishes(r):
    return "<br>".join(f"{n} **{p}**" if p else n for n, p in r.get("dishes", [])) or "—"


def walk(m):
    return "搭車" if m > 25 else f"~{m} 分"


def food_md():
    near = [r for r in food["restaurants"] if r["area"] == "near"]
    city = [r for r in food["restaurants"] if r["area"] == "city"]
    head = "| 店名 | 類型 | 推薦餐點・價格 | 人均 | Google | 化學館 | Le Cantlie | 重點 |\n|---|---|---|---|---|---|---|---|\n"
    row = lambda r: (f"| [**{r['name']}**]({gq(r)})<br>{r['addr']} | {r['cat']}・{r['cuisine']} | {dishes(r)} | {r.get('price') or '—'} "
                     f"| {r.get('rating') or '—'} | {walk(r['walk'])} | {walk(r['walk_hotel'])} | {r['note']}{' 🍱' if 'bento' in r.get('tags', []) else ''} |\n")
    out = ["# 🍜 McGill 化學館附近與蒙特婁：餐廳\n\n超市請看 [grocery.md](grocery.md)。\n\n",
           f"**{food['checked']} 逐家用 Google Maps 確認仍在營業。** 推薦餐點來自小紅書筆記與 Google Maps「熱門餐點」；",
           "有標價的是筆記或菜單上的價格，「人均」是 Google Maps 使用者回報的每人花費。價格未含稅和小費。",
           "步行時間＝直線距離 × 1.3 ÷ 80 m/分；超過 25 分標「搭車」。🍱＝可以當便當／熟食。\n\n",
           "互動地圖 👉 [生存攻略網站・美食分頁](https://ashur5457.github.io/McGrillChemVisitingScholar/#food)\n\n",
           "## 🍽️ 化學館附近（依步行時間排序）\n\n", head, *map(row, near),
           "\n## 🚇 蒙特婁市區必吃（要搭地鐵／公車）\n\n", head, *map(row, city),
           ]
    out.append("\n## ❌ 已剔除（2026-11 查核）\n\n| 店名 | 原因 |\n|---|---|\n"
               "| Ewha Shiro 梨花月白 | Google Maps 顯示永久停業 |\n| Mae Sri | 暫停營業 |\n| King Bab | Google Maps 找不到 |\n"
               "| Shuyi 書亦燒仙草（McGill 附近）、Chatime（Av. du Parc）、楊國福 | 該分店已不在 |\n"
               "| Thai Express（McGill 附近） | 小紅書提到的分店找不到，附近分店 Google 評價 2.7 |\n"
               "| Papa Jackie、Atlas Uyghur、Bubble Bubble 寶島小吃 | 都在南岸 Brossard，走路到不了；想吃可搭 REM |\n"
               "\n> BeaverTails 老港店已從小紅書寫的 280 de la Commune E 搬到 **123 de la Commune E**。\n")
    return "".join(out)


def guide_md():
    order, out = [], ["# 🧭 McGill 交換生存攻略\n\n",
                      f"小紅書＋網路資料，{guide['checked']} 查核。網站版 👉 [生存攻略](https://ashur5457.github.io/McGrillChemVisitingScholar/)\n\n"]
    def ref(i):
        if i not in order:
            order.append(i)
        return order.index(i) + 1
    for s in guide["sections"]:
        out.append(f"## {s['icon']} {s['title']}\n\n> {s['lead']}\n\n")
        if s["stats"]:
            out.append(" ・ ".join(f"**{b}** {l}" for b, l in s["stats"]) + "\n\n")
        for it in s["items"]:
            refs = "".join(f"[^{ref(i)}]" for i in it["src"])
            pins = "".join(f"<br>📍 [{l}]({GM}{quote_plus(q)})" for l, q in it["places"])
            out.append(f"- **{it['h']}**：{it['t']}{refs}{pins}\n")
        out.append("\n")
    out.append("## 📚 資料來源\n\n小紅書連結需登入 rednote 才能開啟。\n\n")
    out += [f"[^{n}]: [{guide['sources'][i][0]}]({guide['sources'][i][1]})\n" for n, i in enumerate(order, 1)]
    return "".join(out)


def grocery_md():
    order = []
    def refs(ids):
        out = ""
        for i in ids:
            if i not in order:
                order.append(i)
            out += f"[^{order.index(i) + 1}]"
        return out
    out = ["# 🛒 McGill 化學館附近超市\n\n",
           f"{grocery['checked']} 查核（小紅書、網路、Google Maps 評論）。依離 Le Cantlie 步行時間排序。🍱＝有熟食／便當。\n\n",
           "互動地圖 👉 [生存攻略網站・超市分頁](https://ashur5457.github.io/McGrillChemVisitingScholar/#grocery)\n\n## 💡 買菜重點\n\n"]
    out += [f"- {t}{refs(src)}\n" for t, src in grocery["tips"]]
    for s in grocery["stores"]:
        q = GM + quote_plus(s["name"].split("（")[0] + " " + s["addr"].split("（")[0] + " Montreal")
        out.append(f"\n## {s['name']}{' 🍱' if 'bento' in s['tags'] else ''}\n\n"
                   f"{s['kind']} ・ ⭐ {s['rating']} ・ 💰 {s['price']} ・ 🕒 {s['hours']} ・ Le Cantlie {walk(s['walk_hotel'])} ・ 化學館 {walk(s['walk'])}\n\n"
                   f"📍 [{s['addr']}]({q})\n\n{s['lead']}{refs(s['src'])}\n\n")
        out += [f"- {h}\n" for h in s["highlights"]]
        out.append(f"\n**適合買**：{s['best']}　**注意**：{s['caution']}\n")
    out.append("\n## 🚇 要搭車的大型華人超市\n\n")
    out += [f"- **[{f['name']}]({GM + quote_plus(f['q'])})**：{f['t']}{refs(f['src'])}\n" for f in grocery["far"]]
    out.append("\n## 📚 資料來源\n\n")
    out += [f"[^{n}]: [{grocery['sources'][i][0]}]({grocery['sources'][i][1]})\n" for n, i in enumerate(order, 1)]
    return "".join(out)


def fun_md():
    order = []
    def refs(ids):
        out = ""
        for i in ids:
            if i not in order:
                order.append(i)
            out += f"[^{order.index(i) + 1}]"
        return out
    pin = lambda l, q: f"[📍 {l}]({GM + quote_plus(q)})"
    out = ["# 🎡 遊玩：週末、博物館、渥太華、多倫多\n\n",
           f"{fun['checked']} 查核。網站版 👉 [遊玩分頁](https://ashur5457.github.io/McGrillChemVisitingScholar/#fun)\n\n## 🎉 冬季祭典\n\n"
           "| 活動 | 日期（2027） | 票價 | 說明 | 地點 |\n|---|---|---|---|---|\n"]
    out += [f"| **{x['name']}** | {x['dates']} | {x['price']} | {x['t']}{refs(x['src'])} | {pin(*x['place'])} |\n" for x in fun["festivals"]]
    out.append("\n## 📅 週末行事曆\n\n")
    for w in fun["weekends"]:
        out.append(f"### {w['d']}：{w['title']}\n\n")
        out += [f"- {t} {pin(*p)}\n" for t, p in w["items"]]
        out.append("\n")
    out.append("## 🏛️ 博物館・美術館・動物園（成人票）\n\n| 名稱 | 票價 | 優惠 | 時間 |\n|---|---|---|---|\n")
    out += [f"| [{m['name']}]({GM + quote_plus(m['q'])}) | {m['price']} | {m['deal']} | {m['hours']}{refs(m['src'])} |\n" for m in fun["museums"]]
    o = fun["ottawa"]
    out.append(f"\n## 🍁 渥太華週末\n\n{o['lead']}{refs(o['src'])}\n\n" + " ・ ".join(f"**{b}** {l}" for b, l in o["stats"]) + "\n\n")
    for d in o["days"]:
        out.append(f"**{d['d']}：{d['title']}**\n\n")
        out += [f"- {t} {pin(*p)}\n" for t, p in d["items"]]
        out.append("\n")
    t = fun["toronto"]
    out.append(f"## 🏙️ 多倫多：U of T Acceleration Consortium\n\n{t['lead']}\n\n" + " ・ ".join(f"**{b}** {l}" for b, l in t["stats"]) + "\n\n")
    out += [f"- {x}{refs(src)} {' '.join(pin(*p) for p in ps)}\n" for x, ps, src in t["items"]]
    out.append("\n## 📚 資料來源\n\n")
    out += [f"[^{n}]: [{fun['sources'][i][0]}]({fun['sources'][i][1]})\n" for n, i in enumerate(order, 1)]
    return "".join(out)


def kml():
    def folder(name, rows):
        pm = "".join(f"""    <Placemark>
      <name>{escape(r['name'])}</name>
      <description>{escape(r['addr'] + '｜' + '、'.join(n + (' ' + p if p else '') for n, p in r.get('dishes', [])) + '｜' + r['note'])}</description>
      <Point><coordinates>{r['lng']},{r['lat']},0</coordinates></Point>
    </Placemark>
""" for r in rows)
        return f"  <Folder>\n    <name>{escape(name)}</name>\n{pm}  </Folder>\n"
    R = food["restaurants"]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'
            "  <name>McGill 化學館附近美食與超市</name>\n"
            + folder("化學館附近：餐廳・咖啡・甜點", [r for r in R if r["area"] == "near"])
            + folder("蒙特婁市區必吃", [r for r in R if r["area"] == "city"])
            + folder("超市・日用品", [dict(s, dishes=[], note=s["lead"]) for s in grocery["stores"]])
            + "</Document>\n</kml>\n")


(ROOT / "docs/food.md").write_text(food_md())
(ROOT / "docs/guide.md").write_text(guide_md())
(ROOT / "docs/grocery.md").write_text(grocery_md())
(ROOT / "docs/fun.md").write_text(fun_md())
(ROOT / "food.kml").write_text(kml())
print("ok")
