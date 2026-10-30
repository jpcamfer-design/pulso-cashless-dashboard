"""Inyecta data.json en template.html -> index.html (archivo único para GitHub Pages)."""
import json

data = json.load(open("data.json", encoding="utf-8"))
html = open("template.html", encoding="utf-8").read()
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
open("index.html", "w", encoding="utf-8").write(html.replace("__DATA__", payload))
print("index.html listo,", len(html) // 1024, "KB de plantilla")
