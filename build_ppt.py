"""Build JourneyFrame hackathon pitch deck."""

import io
import urllib.request
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ── Palette ──────────────────────────────────────────────────────────────────
DARK_BG    = RGBColor(0x0D, 0x0D, 0x1A)   # near-black navy
ACCENT     = RGBColor(0x6C, 0x63, 0xFF)   # electric violet
ACCENT2    = RGBColor(0xFF, 0x6B, 0x6B)   # coral pink
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xCC, 0xCC, 0xDD)
CARD_BG    = RGBColor(0x1A, 0x1A, 0x2E)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

IMG_URLS = {
    "seattle":   "https://images.unsplash.com/photo-1741034793665-64c8afcf6c23?fm=jpg&q=60&w=1600&auto=format&fit=crop",
    "cafe":      "https://images.unsplash.com/photo-1753351057455-b13182da4d03?fm=jpg&q=60&w=1600&auto=format&fit=crop",
    "chat":      "https://images.unsplash.com/photo-1712002641287-f9c8b7161c8f?fm=jpg&q=60&w=1600&auto=format&fit=crop",
    "pnw":       "https://images.unsplash.com/photo-1597157153515-028fa3d4bd69?fm=jpg&q=60&w=1600&auto=format&fit=crop",
    "ai_tech":   "https://images.unsplash.com/photo-1655635949384-f737c5133dfe?fm=jpg&q=60&w=1600&auto=format&fit=crop",
}

def fetch_image(url: str) -> io.BytesIO | None:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            buf = io.BytesIO(r.read())
            buf.seek(0)
            return buf
    except Exception as e:
        print(f"  ⚠ Could not fetch {url}: {e}")
        return None

# ── Helpers ───────────────────────────────────────────────────────────────────
def solid_bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_image_bg(slide, img_bytes: io.BytesIO | None, alpha_rect=True):
    """Place a full-bleed image, then optionally overlay a dark scrim."""
    if img_bytes:
        slide.shapes.add_picture(img_bytes, 0, 0, SLIDE_W, SLIDE_H)
    if alpha_rect:
        from pptx.util import Pt
        from pptx.oxml.ns import qn
        from lxml import etree
        scrim = slide.shapes.add_shape(
            1,  # MSO_SHAPE_TYPE.RECTANGLE
            0, 0, SLIDE_W, SLIDE_H,
        )
        scrim.fill.solid()
        scrim.fill.fore_color.rgb = DARK_BG
        scrim.line.fill.background()
        # Set transparency to 45%
        sp = scrim._element
        spPr = sp.find(qn("p:spPr"))
        solidFill = spPr.find(f".//{qn('a:solidFill')}")
        if solidFill is not None:
            srgb = solidFill.find(qn("a:srgbClr"))
            if srgb is None:
                srgb = solidFill.find(qn("a:sysClr"))
            if srgb is not None:
                alpha_elem = etree.SubElement(srgb, qn("a:alpha"))
                alpha_elem.set("val", "60000")  # 60% opacity = 40% transparent

def add_text(slide, text, x, y, w, h, size=24, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    box = slide.shapes.add_textbox(x, y, w, h)
    box.word_wrap = wrap
    tf = box.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return box

def pill(slide, text, x, y, color=ACCENT):
    """Small colored pill label."""
    box = slide.shapes.add_shape(1, x, y, Inches(2.1), Inches(0.38))
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.fill.background()
    tf = box.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = WHITE

def accent_bar(slide, y=Inches(0.08)):
    bar = slide.shapes.add_shape(1, 0, y, SLIDE_W, Inches(0.055))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()

def card(slide, x, y, w, h, bg=CARD_BG):
    box = slide.shapes.add_shape(1, x, y, w, h)
    box.fill.solid()
    box.fill.fore_color.rgb = bg
    box.line.color.rgb = ACCENT
    box.line.width = Pt(1)
    return box

# ─────────────────────────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H
blank_layout = prs.slide_layouts[6]

print("Fetching images …")
imgs = {k: fetch_image(v) for k, v in IMG_URLS.items()}

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 – Title
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
add_image_bg(s, imgs["seattle"], alpha_rect=True)
accent_bar(s)

add_text(s, "JourneyFrame", Inches(0.8), Inches(1.6), Inches(8), Inches(1.5),
         size=64, bold=True, color=WHITE)
add_text(s, "AI-Powered Relationship-Aware Trip Planner",
         Inches(0.8), Inches(3.1), Inches(9), Inches(0.7),
         size=26, color=LIGHT_GRAY)
add_text(s, "Plan unforgettable outings — through iMessage.",
         Inches(0.8), Inches(3.9), Inches(9), Inches(0.6),
         size=20, italic=True, color=ACCENT)

pill(s, "🏆  HackWithSeattle 2026", Inches(0.8), Inches(5.5), color=ACCENT2)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 – The Problem
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
accent_bar(s)

add_text(s, "The Problem", Inches(0.7), Inches(0.5), Inches(6), Inches(0.8),
         size=38, bold=True, color=WHITE)

problems = [
    ("😩", "Decision Fatigue",
     "\"Where should we go?\" is exhausting.\nMost planners give generic lists, not real plans."),
    ("🤖", "No Relationship Context",
     "Apps don't know if it's a first date,\na reunion with a college friend, or a family day."),
    ("🌧", "Ignores Reality",
     "Weather, time of day, local vibe —\nexisting tools miss what actually matters."),
]

for i, (icon, title, desc) in enumerate(problems):
    cx = Inches(0.7 + i * 4.2)
    card(s, cx, Inches(1.6), Inches(3.9), Inches(4.5))
    add_text(s, icon, cx + Inches(0.2), Inches(1.75), Inches(0.8), Inches(0.8), size=36)
    add_text(s, title, cx + Inches(0.2), Inches(2.55), Inches(3.5), Inches(0.6),
             size=20, bold=True, color=ACCENT)
    add_text(s, desc, cx + Inches(0.2), Inches(3.15), Inches(3.5), Inches(2.5),
             size=16, color=LIGHT_GRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 – Our Solution  (with café image)
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
accent_bar(s)

# Right-side image panel
if imgs["cafe"]:
    s.shapes.add_picture(imgs["cafe"], Inches(7.3), Inches(0.14), Inches(5.9), SLIDE_H - Inches(0.14))

# Dark overlay on right side only
panel = s.shapes.add_shape(1, Inches(7.3), Inches(0.14), Inches(5.9), SLIDE_H)
panel.fill.solid()
panel.fill.fore_color.rgb = DARK_BG
panel.line.fill.background()
from lxml import etree
from pptx.oxml.ns import qn as _qn
sp = panel._element
spPr = sp.find(_qn("p:spPr"))
solidFill = spPr.find(f".//{_qn('a:solidFill')}")
if solidFill is not None:
    for child in list(solidFill):
        srgb = child
        alpha_elem = etree.SubElement(srgb, _qn("a:alpha"))
        alpha_elem.set("val", "55000")

add_text(s, "Our Solution", Inches(0.6), Inches(0.5), Inches(6.5), Inches(0.8),
         size=38, bold=True, color=WHITE)

add_text(s, "Just text the AI like a friend.",
         Inches(0.6), Inches(1.4), Inches(6.8), Inches(0.6),
         size=22, bold=True, color=ACCENT)

example = (
    "\"My friend Sarah is visiting Seattle tomorrow.\n"
    " Plan a cozy rainy-day afternoon for us.\""
)
add_text(s, example, Inches(0.6), Inches(2.1), Inches(6.5), Inches(1.2),
         size=18, italic=True, color=LIGHT_GRAY)

bullets = [
    "✦  Understands relationship type & occasion",
    "✦  Checks live weather & local vibe",
    "✦  Creates a 3–5 stop itinerary with emotional purpose",
    "✦  Sends the plan + scene images via iMessage",
]
for i, b in enumerate(bullets):
    add_text(s, b, Inches(0.6), Inches(3.5 + i * 0.62), Inches(6.5), Inches(0.55),
             size=17, color=WHITE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 – How It Works  (pipeline)
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
accent_bar(s)
add_text(s, "How It Works", Inches(0.7), Inches(0.4), Inches(8), Inches(0.8),
         size=38, bold=True, color=WHITE)
add_text(s, "A 6-stage RocketRide AI pipeline — triggered by one iMessage",
         Inches(0.7), Inches(1.1), Inches(11), Inches(0.5),
         size=18, color=LIGHT_GRAY)

stages = [
    ("1", "Intent\nParser",   "Location · Occasion\nMood · Time · Constraints"),
    ("2", "Context\nEnrich",  "Weather · Preferences\nRelationship · Local Recs"),
    ("3", "Itinerary\nPlanner","3–5 stops · Duration\nEmotional Purpose"),
    ("4", "Experience\nNarrator","Warm conversational\nmessage per stop"),
    ("5", "Image Prompt\nGen", "Cinematic prompts\nper major stop"),
    ("6", "Response\nComposer","iMessage-ready\nmulti-message output"),
]

stage_w = Inches(1.9)
gap = Inches(0.22)
start_x = Inches(0.45)

for i, (num, title, desc) in enumerate(stages):
    cx = start_x + i * (stage_w + gap)
    card(s, cx, Inches(1.85), stage_w, Inches(4.5), bg=CARD_BG)
    # number badge
    badge = s.shapes.add_shape(1, cx + Inches(0.6), Inches(2.05), Inches(0.65), Inches(0.65))
    badge.fill.solid()
    badge.fill.fore_color.rgb = ACCENT
    badge.line.fill.background()
    add_text(s, num, cx + Inches(0.6), Inches(2.0), Inches(0.65), Inches(0.65),
             size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, title, cx + Inches(0.1), Inches(2.8), stage_w - Inches(0.2), Inches(0.8),
             size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    add_text(s, desc, cx + Inches(0.1), Inches(3.65), stage_w - Inches(0.2), Inches(2.2),
             size=12, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
    # arrow between cards
    if i < len(stages) - 1:
        ax = cx + stage_w + Inches(0.02)
        add_text(s, "→", ax, Inches(3.7), gap, Inches(0.5),
                 size=18, color=ACCENT, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 – Tech Stack
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
add_image_bg(s, imgs["ai_tech"], alpha_rect=True)
accent_bar(s)

add_text(s, "Tech Stack", Inches(0.7), Inches(0.4), Inches(6), Inches(0.8),
         size=38, bold=True, color=WHITE)

stack = [
    ("🚀", "RocketRide",        "Core AI orchestration — 6-stage wave pipeline with parallel LLM calls"),
    ("📡", "Photon Spectrum",   "iMessage delivery layer — inbound/outbound message routing"),
    ("⚡", "FastAPI Backend",   "Python webhook server connecting Photon → RocketRide pipeline"),
    ("🌦", "Weather API",       "Real-time conditions for context enrichment"),
    ("🖼", "Image Generation",  "Cinematic scene image prompts per itinerary stop"),
    ("🧠", "Claude / GPT-4o",   "LLM powering intent parsing, narration, and prompt generation"),
]

for i, (icon, name, desc) in enumerate(stack):
    row = i % 3
    col = i // 3
    cx = Inches(0.6 + col * 6.4)
    cy = Inches(1.5 + row * 1.7)
    card(s, cx, cy, Inches(6.0), Inches(1.5), bg=CARD_BG)
    add_text(s, icon + "  " + name, cx + Inches(0.25), cy + Inches(0.15), Inches(5.5), Inches(0.55),
             size=18, bold=True, color=ACCENT)
    add_text(s, desc, cx + Inches(0.25), cy + Inches(0.65), Inches(5.5), Inches(0.7),
             size=14, color=LIGHT_GRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 – Example Journey  (with PNW / chat image)
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
accent_bar(s)

add_text(s, "Example Journey", Inches(0.7), Inches(0.4), Inches(9), Inches(0.8),
         size=38, bold=True, color=WHITE)

add_text(s, "\"My friend Sarah is visiting Seattle tomorrow. Plan a cozy rainy-day afternoon.\"",
         Inches(0.7), Inches(1.2), Inches(12), Inches(0.65),
         size=17, italic=True, color=ACCENT)

stops = [
    ("2:00 PM", "Victrola Coffee Roasters",
     "Warm up with a perfect pour-over. A local institution — perfect for reconnecting."),
    ("3:15 PM", "Elliott Bay Book Company",
     "Browse rain-soaked shelves. Find one book to gift each other."),
    ("4:30 PM", "Pike Place Market",
     "Watch the fish throwers, grab flowers, feel Seattle's heartbeat."),
    ("5:45 PM", "The Pink Door",
     "Hidden gem with Puget Sound view. Share small plates & a bottle of Rosé."),
    ("7:30 PM", "Waterfront Walk",
     "End the night with the city lights reflecting on the water. No agenda needed."),
]

for i, (time, place, note) in enumerate(stops):
    cy = Inches(2.0 + i * 0.98)
    # timeline dot
    dot = s.shapes.add_shape(1, Inches(0.5), cy + Inches(0.18), Inches(0.25), Inches(0.25))
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT
    dot.line.fill.background()
    add_text(s, time, Inches(0.85), cy, Inches(1.4), Inches(0.45),
             size=13, bold=True, color=ACCENT)
    add_text(s, place, Inches(2.35), cy, Inches(4.5), Inches(0.45),
             size=15, bold=True, color=WHITE)
    add_text(s, note, Inches(2.35), cy + Inches(0.44), Inches(9.5), Inches(0.45),
             size=13, color=LIGHT_GRAY)

# Right: chat image
if imgs["chat"]:
    s.shapes.add_picture(imgs["chat"], Inches(9.8), Inches(1.0), Inches(3.2), Inches(5.8))
scrim2 = s.shapes.add_shape(1, Inches(9.8), Inches(1.0), Inches(3.2), Inches(5.8))
scrim2.fill.solid()
scrim2.fill.fore_color.rgb = DARK_BG
scrim2.line.fill.background()

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 – Architecture
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
accent_bar(s)

add_text(s, "Architecture", Inches(0.7), Inches(0.4), Inches(8), Inches(0.8),
         size=38, bold=True, color=WHITE)

boxes = [
    (Inches(0.5),  Inches(1.8), "📱 User\niMessage", ACCENT2),
    (Inches(3.2),  Inches(1.8), "📡 Photon\nSpectrum", ACCENT),
    (Inches(5.9),  Inches(1.8), "⚡ FastAPI\nWebhook", ACCENT),
    (Inches(8.6),  Inches(1.8), "🚀 RocketRide\nPipeline", ACCENT),
    (Inches(11.3), Inches(1.8), "🧠 LLM +\nExternal APIs", ACCENT),
]

for bx, by, label, color in boxes:
    card(s, bx, by, Inches(2.5), Inches(1.5), bg=CARD_BG)
    s.shapes[-1].line.color.rgb = color
    add_text(s, label, bx + Inches(0.15), by + Inches(0.25), Inches(2.2), Inches(1.0),
             size=16, bold=True, color=color, align=PP_ALIGN.CENTER)

# Arrows
arrow_y = Inches(2.38)
for ax in [Inches(3.05), Inches(5.75), Inches(8.45), Inches(11.15)]:
    add_text(s, "→", ax - Inches(0.15), arrow_y, Inches(0.5), Inches(0.4),
             size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Return path
add_text(s, "← iMessage response with text + images",
         Inches(0.5), Inches(3.8), Inches(12.5), Inches(0.5),
         size=16, italic=True, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

# RocketRide stages
rr_stages = ["Intent Parser", "Context Enrichment", "Itinerary Planner",
             "Experience Narrator", "Image Prompt Gen", "Response Composer"]
add_text(s, "RocketRide stages:", Inches(0.5), Inches(4.5), Inches(4), Inches(0.45),
         size=14, bold=True, color=ACCENT)
for i, st in enumerate(rr_stages):
    cx = Inches(0.5 + i * 2.15)
    card(s, cx, Inches(5.0), Inches(2.0), Inches(0.9), bg=CARD_BG)
    add_text(s, st, cx + Inches(0.1), Inches(5.05), Inches(1.8), Inches(0.8),
             size=11, color=WHITE, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 – Why JourneyFrame Wins
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
add_image_bg(s, imgs["pnw"], alpha_rect=True)
accent_bar(s)

add_text(s, "Why JourneyFrame Wins", Inches(0.7), Inches(0.4), Inches(10), Inches(0.8),
         size=38, bold=True, color=WHITE)

wins = [
    ("🎯", "Relationship-First", "The only planner that knows WHO you're going with, not just WHERE."),
    ("💬", "Zero Friction UX",   "No app to download. No sign-up. Just text an iMessage."),
    ("🔁", "Deeply Technical",   "Real RocketRide multi-stage pipeline. Real Photon iMessage delivery."),
    ("🌍", "Infinitely Scalable","Works for any city, any occasion, any relationship."),
]

for i, (icon, title, desc) in enumerate(wins):
    row = i // 2
    col = i % 2
    cx = Inches(0.7 + col * 6.2)
    cy = Inches(1.6 + row * 2.3)
    card(s, cx, cy, Inches(5.8), Inches(2.0), bg=CARD_BG)
    add_text(s, icon + "  " + title, cx + Inches(0.3), cy + Inches(0.2), Inches(5.2), Inches(0.6),
             size=22, bold=True, color=ACCENT)
    add_text(s, desc, cx + Inches(0.3), cy + Inches(0.85), Inches(5.2), Inches(1.0),
             size=16, color=LIGHT_GRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 – Call to Action / Thank You
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
solid_bg(s, DARK_BG)
add_image_bg(s, imgs["seattle"], alpha_rect=True)
accent_bar(s)

add_text(s, "Frame your next journey.", Inches(1), Inches(1.8), Inches(11), Inches(1.2),
         size=52, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_text(s, "Just send a text.", Inches(1), Inches(3.15), Inches(11), Inches(0.8),
         size=34, italic=True, color=ACCENT, align=PP_ALIGN.CENTER)

add_text(s, "Built with  🚀 RocketRide  ·  📡 Photon Spectrum  ·  ⚡ FastAPI  ·  🧠 Claude",
         Inches(1), Inches(5.2), Inches(11), Inches(0.5),
         size=16, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

pill(s, "🏆  HackWithSeattle 2026", Inches(5.6), Inches(6.0), color=ACCENT2)

# ── Save ──────────────────────────────────────────────────────────────────────
out = "/Users/yiqix/Downloads/JourneyFrame/JourneyFrame_Pitch.pptx"
prs.save(out)
print(f"\n✅  Saved: {out}")
