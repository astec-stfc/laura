"""Interactive HTML explorer for a LAURA machine model and the LinkML schema.

Writes one self-contained page -- no CDN, no JavaScript library, no extra
Python dependency -- so it opens from a file:// URL on a control-room machine
with no network.  It has five tabs:

``Ontology``
    The LinkML class hierarchy, read straight from ``laura/schema/YAML``.
``Machine``
    Lattices, the sections in each, and the elements in each section.
``Controls``
    Machine areas, the elements in them that have a control interface, and
    every process variable that interface exposes.
``Quality``
    Checks for fields the schema declares but a lattice never populates.
``PVs``
    A filterable table of every process variable in the machine.

Usage::

    from laura.explorer import write_explorer

    write_explorer(machine, "clara.html")
"""

from __future__ import annotations

import html
import json
import pathlib
from collections import Counter, defaultdict
from typing import Any

# The schema chunks that gen-* reads; the ontology tab reads the same source.
_SCHEMA_DIR = pathlib.Path(__file__).parent / "schema" / "YAML"

# Longest sample list shown under a failing quality check.  The counts are
# exact; only the drill-down is truncated.
_SAMPLE_LIMIT = 250


# -- data extraction ---------------------------------------------------------


def _schema_classes(schema_dir: str | pathlib.Path | None = None) -> dict[str, dict]:
    """Every LinkML class in the schema chunks, keyed by class name.

    Reads the YAML directly rather than through ``linkml_runtime`` so the
    explorer works without the schema-authoring dependency group.
    """
    import yaml  # noqa: PLC0415 -- pyyaml is a hard dependency, but only needed here

    directory = pathlib.Path(schema_dir or _SCHEMA_DIR)
    classes: dict[str, dict] = {}
    for path in sorted(directory.glob("*.yaml")):
        document = yaml.safe_load(path.read_text()) or {}
        for name, body in (document.get("classes") or {}).items():
            body = body or {}
            classes[name] = {
                "file": path.name,
                "parent": body.get("is_a"),
                "mixins": body.get("mixins") or [],
                "description": " ".join((body.get("description") or "").split()),
                "n_slots": len(body.get("attributes") or {}) + len(body.get("slots") or []),
                "abstract": bool(body.get("abstract")),
            }
    return classes


def _ontology_tree(classes: dict[str, dict]) -> list[dict]:
    """Forest of the ``is_a`` hierarchy.  Roots are classes with no parent."""
    children: dict[str | None, list[str]] = defaultdict(list)
    for name, info in classes.items():
        parent = info["parent"] if info["parent"] in classes else None
        children[parent].append(name)

    def node(name: str) -> dict:
        info = classes[name]
        meta = f"{info['n_slots']} slots · {info['file']}"
        if info["mixins"]:
            meta += " · mixins: " + ", ".join(info["mixins"])
        return {
            "n": name,
            "k": "abstract" if info["abstract"] else "class",
            "m": meta,
            "d": info["description"],
            "c": [node(child) for child in sorted(children[name])],
        }

    def size(built: dict) -> int:
        return 1 + sum(size(child) for child in built["c"])

    # Deepest hierarchies first: most roots are standalone value classes with no
    # subclasses, and they would otherwise bury AcceleratorElement in the list.
    roots = [node(name) for name in sorted(children[None])]
    roots.sort(key=lambda built: (-size(built), built["n"]))
    return roots


def _element_node(element: Any, name: str) -> dict:
    """Leaf node for one element: its class, where it sits, how many PVs."""
    if element is None:
        return {"n": name, "k": "missing", "m": "named by a section, not in the element list"}
    parts = [type(element).__name__]
    s = getattr(getattr(element, "physical", None), "s", None)
    if isinstance(s, (int, float)):
        parts.append(f"s={s:.3f} m")
    n_variables = len(_variables(element))
    if n_variables:
        parts.append(f"{n_variables} PVs")
    return {"n": name, "k": "element", "m": " · ".join(parts)}


def _machine_tree(machine: Any) -> list[dict]:
    """Lattice -> section -> element."""
    roots = []
    for lattice_name in sorted(machine.lattices):
        lattice = machine.lattices[lattice_name]
        sections = []
        for entry in lattice.sections:
            section_name = entry if isinstance(entry, str) else getattr(entry, "name", str(entry))
            section = machine.sections.get(section_name)
            names = list(section.names) if section is not None else []
            sections.append(
                {
                    "n": section_name,
                    "k": "section",
                    "m": f"{len(names)} elements",
                    "c": [_element_node(machine.elements.get(n), n) for n in names],
                }
            )
        roots.append(
            {
                "n": lattice_name,
                "k": "lattice",
                "m": f"{len(sections)} sections · {len(lattice.elements)} elements",
                "c": sections,
            }
        )
    return roots


def _variables(element: Any) -> dict:
    """The element's process variables, or an empty mapping if it has none."""
    return getattr(getattr(element, "controls", None), "variables", None) or {}


def _pv_rows(machine: Any) -> list[dict]:
    """One flat record per process variable, shared by the Controls and PVs tabs."""
    rows = []
    for element_name in sorted(machine.elements):
        element = machine.elements[element_name]
        for key, variable in _variables(element).items():
            dtype = getattr(variable, "dtype", None)
            rows.append(
                {
                    "e": element_name,
                    "k": key,
                    "id": getattr(variable, "identifier", "") or "",
                    "t": getattr(variable, "control_type", "") or "",
                    "u": getattr(variable, "units", "") or "",
                    "p": getattr(variable, "protocol", "") or "",
                    "r": bool(getattr(variable, "read_only", False)),
                    "g": getattr(variable, "target", "") or "",
                    "y": getattr(dtype, "__name__", "") or "",
                    "d": getattr(variable, "description", "") or "",
                }
            )
    return rows


def _control_tree(machine: Any, rows: list[dict]) -> list[dict]:
    """Machine area -> element -> PV.  PVs are index references into *rows*."""
    by_element: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        by_element[row["e"]].append(index)

    by_area: dict[str, list[tuple[str, list[int]]]] = defaultdict(list)
    for element_name, indices in by_element.items():
        area = getattr(machine.elements[element_name], "machine_area", "") or "(no area)"
        by_area[area].append((element_name, indices))

    tree = []
    for area in sorted(by_area):
        elements = sorted(by_area[area])
        tree.append(
            {
                "n": area,
                "k": "area",
                "m": f"{len(elements)} elements · "
                f"{sum(len(i) for _, i in elements)} PVs",
                "c": [
                    {
                        "n": name,
                        "k": "element",
                        "m": f"{type(machine.elements[name]).__name__} · {len(indices)} PVs",
                        "c": [{"p": i} for i in indices],
                    }
                    for name, indices in elements
                ],
            }
        )
    return tree


def _is_all_zero(model: Any) -> bool:
    """True if *model* is absent or every number anywhere inside it is zero.

    Used to spot sub-models that exist only because they have defaults -- a
    survey block of zeros means nobody ever measured the element.
    """
    if model is None:
        return True

    def walk(value: Any) -> bool:
        if isinstance(value, bool) or value is None:
            return True
        if isinstance(value, (int, float)):
            return value == 0
        if isinstance(value, dict):
            return all(walk(v) for v in value.values())
        if isinstance(value, (list, tuple)):
            return all(walk(v) for v in value)
        return True

    return walk(model.model_dump())


def _quality(machine: Any, rows: list[dict]) -> list[dict]:
    """Checks for what the schema can hold but this lattice does not fill in."""
    elements = machine.elements
    n_elements = len(elements)
    in_a_lattice = {name for lattice in machine.lattices.values() for name in lattice.elements}

    def check(title: str, why: str, hits: list[str], total: int) -> dict:
        return {
            "n": title,
            "d": why,
            "c": len(hits),
            "t": total,
            "s": sorted(hits)[:_SAMPLE_LIMIT],
        }

    duplicates = Counter(row["id"] for row in rows if row["id"])

    return [
        check(
            "Elements with no control interface",
            "The element exists in the model but exposes no process variables, so "
            "nothing in the control system can read or drive it.",
            [name for name, element in elements.items() if not _variables(element)],
            n_elements,
        ),
        check(
            "PVs with no model target",
            "``target`` is what ties a PV back to a field of the physics model. "
            "Without it a reading cannot be written into the model automatically.",
            [row["id"] or f"{row['e']}:{row['k']}" for row in rows if not row["g"]],
            len(rows),
        ),
        check(
            "Elements never surveyed",
            "``physical.survey`` is all zeros, i.e. the as-built position was never "
            "recorded and only the design position is known.",
            [
                name
                for name, element in elements.items()
                if _is_all_zero(getattr(getattr(element, "physical", None), "survey", None))
            ],
            n_elements,
        ),
        check(
            "Elements with no longitudinal position",
            "``physical.s`` is unset, so the element cannot be placed on a floor "
            "plan or ordered along the beamline.",
            [
                name
                for name, element in elements.items()
                if getattr(getattr(element, "physical", None), "s", None) is None
            ],
            n_elements,
        ),
        check(
            "Elements in no lattice",
            "The element is defined and sectioned but no lattice walks through it, "
            "so no simulation export will ever see it.",
            [name for name in elements if name not in in_a_lattice],
            n_elements,
        ),
        check(
            "PVs with placeholder units",
            "``Arb. Units`` is the fallback, not a real unit -- these cannot be "
            "converted or plotted with an axis label.",
            [row["id"] for row in rows if row["u"] == "Arb. Units"],
            len(rows),
        ),
        check(
            "Duplicate PV identifiers",
            "The same channel is claimed by more than one element, so a write "
            "through one of them silently affects the other.",
            [identifier for identifier, n in duplicates.items() if n > 1],
            len(rows),
        ),
        check(
            "Elements with no manufacturer record",
            "Neither manufacturer nor serial number is recorded, so a failed "
            "component cannot be traced to a batch.",
            [
                name
                for name, element in elements.items()
                if not (
                    getattr(getattr(element, "manufacturer", None), "manufacturer", "")
                    or getattr(getattr(element, "manufacturer", None), "serial_number", "")
                )
            ],
            n_elements,
        ),
    ]


# -- rendering ---------------------------------------------------------------


def _quality_html(checks: list[dict]) -> str:
    """The Quality tab, rendered in Python -- it is static, so it needs no JS."""
    blocks = []
    for chk in checks:
        pct = 100.0 * chk["c"] / chk["t"] if chk["t"] else 0.0
        severity = "ok" if chk["c"] == 0 else ("warn" if pct < 50 else "bad")
        samples = "".join(f"<li><code>{html.escape(s)}</code></li>" for s in chk["s"])
        more = (
            f"<p class='more'>&hellip; and {chk['c'] - len(chk['s'])} more</p>"
            if chk["c"] > len(chk["s"])
            else ""
        )
        drill = (
            f"<details><summary>show {len(chk['s'])}</summary><ul>{samples}</ul>{more}</details>"
            if chk["s"]
            else ""
        )
        blocks.append(
            f"<div class='check {severity}'>"
            f"<div class='chead'><span class='ctitle'>{html.escape(chk['n'])}</span>"
            f"<span class='cnum'>{chk['c']} / {chk['t']} ({pct:.1f}%)</span></div>"
            f"<p class='cwhy'>{html.escape(chk['d'])}</p>{drill}</div>"
        )
    return "\n".join(blocks)


_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>__TITLE__ &mdash; LAURA explorer</title>
<style>
:root{--line:#d0d7de;--muted:#6a737d;--bg:#fff;--hover:#f0f4f8}
*{box-sizing:border-box}
body{margin:0;font:13px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#24292f;background:var(--bg)}
header{padding:12px 18px;border-bottom:1px solid var(--line)}
h1{margin:0;font-size:16px;font-weight:600}
h1 small{font-weight:400;color:var(--muted);margin-left:8px}
nav{display:flex;gap:2px;padding:0 12px;border-bottom:1px solid var(--line);background:#f6f8fa}
nav button{border:0;background:none;padding:8px 14px;font:inherit;cursor:pointer;color:var(--muted);
  border-bottom:2px solid transparent}
nav button.on{color:#24292f;border-bottom-color:#0969da;font-weight:600}
main{padding:12px 18px}
.pane{display:none}.pane.on{display:block}
.bar{display:flex;gap:10px;align-items:center;margin-bottom:10px;position:sticky;top:0;
  background:var(--bg);padding:6px 0;z-index:1}
input[type=search]{flex:0 0 340px;padding:5px 8px;border:1px solid var(--line);border-radius:6px;font:inherit}
.count{color:var(--muted)}
button.link{border:0;background:none;color:#0969da;cursor:pointer;font:inherit;padding:0}
.tree ul{list-style:none;margin:0;padding-left:16px;border-left:1px solid var(--line)}
.tree>ul{border-left:0;padding-left:0}
.tree li{position:relative}
.tree li::before{content:"";position:absolute;left:-16px;top:.85em;width:12px;border-top:1px solid var(--line)}
.tree>ul>li::before{display:none}
.tree .row{display:flex;gap:8px;align-items:baseline;padding:1px 4px;border-radius:4px}
.tree .row:hover{background:var(--hover)}
.tree .tog{width:1em;flex:0 0 1em;color:var(--muted);cursor:pointer;user-select:none;text-align:center}
.tree .lbl{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;cursor:pointer}
.tree .meta{color:var(--muted);font-size:12px}
.k-abstract{color:#8250df;font-style:italic}.k-class{color:#0550ae}
.k-lattice{color:#0550ae;font-weight:600}.k-section{color:#1a7f37;font-weight:600}
.k-area{color:#1a7f37;font-weight:600}.k-element{color:#24292f}
.k-missing{color:#cf222e}.k-pv{color:#953800}
table{border-collapse:collapse;width:100%;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
th{text-align:left;border-bottom:2px solid var(--line);padding:4px 8px;position:sticky;top:44px;background:var(--bg)}
td{border-bottom:1px solid #eaeef2;padding:3px 8px;vertical-align:top}
tr:hover td{background:var(--hover)}
.check{border:1px solid var(--line);border-left-width:4px;border-radius:6px;padding:10px 12px;margin-bottom:10px}
.check.ok{border-left-color:#1a7f37}.check.warn{border-left-color:#bf8700}.check.bad{border-left-color:#cf222e}
.chead{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.ctitle{font-weight:600}.cnum{font-family:ui-monospace,monospace;color:var(--muted)}
.cwhy{margin:4px 0 6px;color:var(--muted)}
.check ul{columns:3;font-size:12px;margin:6px 0 0;padding-left:18px}
.more{color:var(--muted);font-size:12px}
summary{cursor:pointer;color:#0969da}
</style></head><body>
<header><h1>__TITLE__<small>__SUBTITLE__</small></h1></header>
<nav id="tabs"></nav>
<main>
  <section class="pane" id="p-ontology"></section>
  <section class="pane" id="p-machine"></section>
  <section class="pane" id="p-controls"></section>
  <section class="pane" id="p-quality">__QUALITY__</section>
  <section class="pane" id="p-pvs"></section>
</main>
<script>
const D = __DATA__;

/* A PV leaf carries only its index into D.pvs; expand it to a display node. */
function view(node){
  if(node.p === undefined) return node;
  const pv = D.pvs[node.p];
  return {n: pv.id || (pv.e + ":" + pv.k), k: "pv", d: pv.d,
          m: [pv.k, pv.t, pv.y, pv.u, pv.r ? "read-only" : "writable",
              pv.g ? "\\u2192 " + pv.g : ""].filter(Boolean).join(" \\u00b7 ")};
}
const kids = node => node.p === undefined ? (node.c || []) : [];

function makeNode(node, open){
  const v = view(node), children = kids(node);
  const li = document.createElement("li");
  const row = document.createElement("div"); row.className = "row";
  const tog = document.createElement("span"); tog.className = "tog";
  tog.textContent = children.length ? "\\u25b8" : "\\u00b7";
  const lbl = document.createElement("span"); lbl.className = "lbl k-" + v.k; lbl.textContent = v.n;
  row.append(tog, lbl);
  if(v.m){ const m = document.createElement("span"); m.className = "meta"; m.textContent = v.m; row.append(m); }
  if(v.d) row.title = v.d;
  li.append(row);

  let ul = null, shown = false;
  const toggle = want => {
    if(!children.length) return;
    shown = want === undefined ? !shown : want;
    tog.textContent = shown ? "\\u25be" : "\\u25b8";
    if(shown && !ul){
      ul = document.createElement("ul");
      for(const child of children) ul.append(makeNode(child, open));
      li.append(ul);
    }
    if(ul) ul.style.display = shown ? "" : "none";
  };
  tog.onclick = lbl.onclick = () => toggle();
  if(open) toggle(true);
  return li;
}

function countNodes(nodes){
  let n = 0;
  for(const node of nodes) n += 1 + countNodes(kids(node));
  return n;
}

/* Keep a node if it matches, or if any descendant does; a matching node with no
   matching descendant keeps all its children so you can see what is under it. */
function filterTree(nodes, q){
  const out = [];
  for(const node of nodes){
    const v = view(node);
    const hit = (v.n + " " + (v.m || "")).toLowerCase().includes(q);
    const matched = filterTree(kids(node), q);
    if(hit || matched.length)
      out.push(node.p !== undefined ? node
               : Object.assign({}, node, {c: matched.length ? matched : kids(node)}));
  }
  return out;
}

function mountTree(pane, roots, label){
  pane.innerHTML =
    "<div class='bar'><input type=search placeholder='filter " + label + "\\u2026'>" +
    "<span class='count'></span><button class='link' data-all='1'>expand all</button>" +
    "<button class='link' data-all='0'>collapse all</button></div><div class='tree'></div>";
  const box = pane.querySelector(".tree"), search = pane.querySelector("input"),
        count = pane.querySelector(".count");
  let forced = null;

  function draw(){
    const q = search.value.trim().toLowerCase();
    const shown = q.length >= 2 ? filterTree(roots, q) : roots;
    const total = countNodes(shown);
    /* Auto-expanding a filter hit is the point of filtering, but a loose query
       can match thousands of PVs -- past that it is faster left collapsed. */
    const open = forced !== null ? forced : (q.length >= 2 && total < 2000);
    forced = null;
    count.textContent = total + " nodes" + (q.length >= 2 ? " matching" : "");
    const ul = document.createElement("ul");
    for(const node of shown) ul.append(makeNode(node, open));
    box.replaceChildren(ul);
  }
  search.oninput = draw;
  for(const button of pane.querySelectorAll("[data-all]"))
    button.onclick = () => { forced = button.dataset.all === "1"; draw(); };
  draw();
}

const PV_COLUMNS = [["id","identifier"],["e","element"],["k","key"],["t","type"],
                    ["y","dtype"],["u","units"],["p","protocol"],["g","target"],["d","description"]];
const PV_LIMIT = 500;

function mountPVs(pane){
  pane.innerHTML =
    "<div class='bar'><input type=search placeholder='filter process variables\\u2026'>" +
    "<span class='count'></span><label><input type=checkbox id='wo'> writable only</label>" +
    "<label><input type=checkbox id='tg'> has target</label></div><div class='rows'></div>";
  const box = pane.querySelector(".rows"), search = pane.querySelector("input[type=search]"),
        count = pane.querySelector(".count"),
        writable = pane.querySelector("#wo"), targeted = pane.querySelector("#tg");

  function draw(){
    const q = search.value.trim().toLowerCase();
    const hits = D.pvs.filter(pv =>
      (!writable.checked || !pv.r) && (!targeted.checked || pv.g) &&
      (!q || (pv.id + " " + pv.e + " " + pv.k + " " + pv.t + " " + pv.g + " " + pv.d)
              .toLowerCase().includes(q)));
    count.textContent = hits.length > PV_LIMIT
      ? "showing " + PV_LIMIT + " of " + hits.length : hits.length + " PVs";
    const head = "<tr>" + PV_COLUMNS.map(c => "<th>" + c[1] + "</th>").join("") + "</tr>";
    const body = hits.slice(0, PV_LIMIT).map(pv =>
      "<tr>" + PV_COLUMNS.map(c => "<td>" + esc(String(pv[c[0]] ?? "")) + "</td>").join("") +
      "</tr>").join("");
    box.innerHTML = "<table>" + head + body + "</table>";
  }
  const esc = s => s.replace(/[&<>]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[ch]));
  search.oninput = writable.onchange = targeted.onchange = draw;
  draw();
}

const TABS = [["ontology","Ontology"],["machine","Machine"],["controls","Controls"],
              ["quality","Quality"],["pvs","PVs"]];
const nav = document.getElementById("tabs");
const built = {};
for(const [id, label] of TABS){
  const button = document.createElement("button");
  button.textContent = label;
  button.onclick = () => {
    for(const other of nav.children) other.classList.toggle("on", other === button);
    for(const [pid] of TABS)
      document.getElementById("p-" + pid).classList.toggle("on", pid === id);
    if(!built[id]){                       /* build on first view: the trees are big */
      built[id] = true;
      const pane = document.getElementById("p-" + id);
      if(id === "ontology") mountTree(pane, D.ontology, "classes");
      else if(id === "machine") mountTree(pane, D.machine, "elements");
      else if(id === "controls") mountTree(pane, D.controls, "PVs");
      else if(id === "pvs") mountPVs(pane);
    }
  };
  nav.append(button);
}
nav.firstChild.click();
</script></body></html>
"""


def write_explorer(
    machine: Any,
    path: str | pathlib.Path,
    title: str = "LAURA",
    schema_dir: str | pathlib.Path | None = None,
) -> pathlib.Path:
    """Write the explorer for *machine* to *path* and return the path.

    Parameters
    ----------
    machine:
        :class:`~laura.models.elementList.MachineModel` to describe.
    path:
        Output ``.html`` file.  Overwritten if it exists.
    title:
        Machine name shown in the header.
    schema_dir:
        Directory of LinkML chunks for the ontology tab.  Defaults to the
        schema shipped with this package.
    """
    rows = _pv_rows(machine)
    classes = _schema_classes(schema_dir)
    checks = _quality(machine, rows)
    data = {
        "ontology": _ontology_tree(classes),
        "machine": _machine_tree(machine),
        "controls": _control_tree(machine, rows),
        "pvs": rows,
    }
    subtitle = (
        f"{len(machine.elements)} elements · {len(machine.lattices)} lattices · "
        f"{len(machine.sections)} sections · {len(rows)} PVs · "
        f"{len(classes)} schema classes"
    )
    page = (
        _PAGE.replace("__TITLE__", html.escape(title))
        .replace("__SUBTITLE__", subtitle)
        .replace("__QUALITY__", _quality_html(checks))
        # ``</script>`` inside the data would close the tag early.
        .replace("__DATA__", json.dumps(data, default=str).replace("</", "<\\/"))
    )
    out = pathlib.Path(path)
    out.write_text(page, encoding="utf-8")
    return out
