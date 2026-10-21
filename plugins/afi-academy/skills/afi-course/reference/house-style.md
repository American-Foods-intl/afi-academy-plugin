# House style for drawn images

Drawn images are for concepts only (diagrams, flows, story scenes, covers), as the kit's imagery rule allows. Anything a
learner must recognise or copy is a real photo, screenshot or official image (`gather.md`). This page says how a drawn
image looks. Send it with `academy_request_render` kind `image` (`write.md` § 3); the spec format is in the kit's block
catalog (Render tools).

## Rules

- **Colours: only the brand tokens.**

  | Use | Colour |
  |---|---|
  | structure, outlines, main shapes | navy `#273a6d` |
  | accents | cyan `#37b0c9`, green `#9fc868`, yellow `#fed857` |
  | hazards only (never decoration) | red `#e74035` |
  | neutrals | greys `#f1f3f7`, `#e6e9ef`, `#d3d8e0`, `#b3bac6`, `#8b94a5`, `#667085`, `#4b5567`, `#333c4c`, and white `#ffffff` |

  Paper or white ground. At most two accent colours in one image (red doesn't count: it marks a hazard).
- **Flat shapes**, outlined with **2 px rounded strokes** (`stroke-width="2"`, `stroke-linecap="round"`,
  `stroke-linejoin="round"`). Every stroke is 2 px; a thicker line is a filled shape. No gradients, shadows, glows,
  filters, patterns or photo textures.
- **No words**: no `<text>`, no letters, digits or logos drawn as shapes. Writing on a sheet or a screen is grey bars
  (filled rounded rectangles). The words live in the course, in both languages.
- **People** are simple faceless figures: a round head with no face, a rounded body. They wear the **correct PPE** for
  the task (safety glasses, hi-vis vest, gloves, boots: whatever the source requires), and nothing unsafe is in the
  background.
- **Never draw** vendor or AFI product packaging, a real label, an official symbol (hazard pictograms, safety signs)
  or a screen: those are real images.
- **SVG conventions:** `viewBox="0 0 1600 900"` (16:9), with `"size": [1600, 900]` in the spec, unless the block needs
  another ratio (for example a square `viewBox="0 0 1200 1200"`). One `<svg>`, no scripts, no external files, no
  fonts. **The subject stays inside the middle 80%** (x 160 to 1440, y 90 to 810 at 1600×900) so the player can crop;
  only the ground (the paper and the floor) runs to the edges.
- **Alt text** in the spec, in both languages, says what the image explains ("A worker reports a problem to the
  supervisor, who writes it down").

## Example: "report it up the line" (a concept: tell your supervisor, who records it)

Two accents (yellow, cyan), every stroke 2 px, writing as grey bars, subject inside x 366 to 1250 and y 220 to 696.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" stroke-linecap="round" stroke-linejoin="round">
  <!-- ground: white paper, grey floor (background, may run edge to edge) -->
  <rect width="1600" height="900" fill="#ffffff"/>
  <rect y="696" width="1600" height="204" fill="#f1f3f7"/>
  <!-- subject: inside x 160-1440, y 90-810 -->
  <g stroke="#273a6d" stroke-width="2">
    <!-- worker: faceless, safety glasses, yellow hi-vis vest -->
    <circle cx="420" cy="360" r="46" fill="#d3d8e0"/>
    <rect x="378" y="346" width="84" height="18" rx="9" fill="#273a6d"/>
    <rect x="366" y="420" width="108" height="172" rx="34" fill="#fed857"/>
    <rect x="366" y="500" width="108" height="16" rx="4" fill="#ffffff"/>
    <rect x="374" y="586" width="40" height="110" rx="16" fill="#273a6d"/>
    <rect x="426" y="586" width="40" height="110" rx="16" fill="#273a6d"/>
    <!-- speech bubble: no words, three dots -->
    <path d="M540 220 h200 a40 40 0 0 1 40 40 v50 a40 40 0 0 1 -40 40 h-150 l-60 40 l10 -40 a40 40 0 0 1 -40 -40 v-50 a40 40 0 0 1 40 -40 z" fill="#ffffff"/>
    <circle cx="590" cy="285" r="13" fill="#8b94a5"/>
    <circle cx="640" cy="285" r="13" fill="#8b94a5"/>
    <circle cx="690" cy="285" r="13" fill="#8b94a5"/>
    <!-- arrow: the report goes to the supervisor -->
    <path d="M700 460 h120 v-40 l80 70 l-80 70 v-40 h-120 z" fill="#37b0c9"/>
    <!-- supervisor: faceless, safety glasses, cyan vest, clipboard -->
    <circle cx="1080" cy="360" r="46" fill="#d3d8e0"/>
    <rect x="1038" y="346" width="84" height="18" rx="9" fill="#273a6d"/>
    <rect x="1026" y="420" width="108" height="172" rx="34" fill="#37b0c9"/>
    <rect x="1026" y="500" width="108" height="16" rx="4" fill="#ffffff"/>
    <rect x="1034" y="586" width="40" height="110" rx="16" fill="#273a6d"/>
    <rect x="1086" y="586" width="40" height="110" rx="16" fill="#273a6d"/>
    <rect x="1140" y="430" width="110" height="140" rx="10" fill="#ffffff"/>
    <rect x="1170" y="418" width="50" height="22" rx="6" fill="#273a6d"/>
    <!-- writing on the clipboard as grey bars, never words -->
    <rect x="1158" y="464" width="74" height="12" rx="6" fill="#b3bac6"/>
    <rect x="1158" y="492" width="74" height="12" rx="6" fill="#b3bac6"/>
    <rect x="1158" y="520" width="50" height="12" rx="6" fill="#b3bac6"/>
  </g>
</svg>
```

Before you send a spec, check: only colours from the table, at most two accents, every stroke 2 px, no `<text>`, no
gradient, the subject inside the middle 80%, nothing a learner would copy.
