---
name: connected-tutorials
description: Create illustrated browser-based tutorials and technical documentation in a Making Software-inspired editorial style, with a sticky left diagram tray, scrolling prose, and live connections between concepts and diagram parts. Use for connected visual explainers from a topic, article, or codebase. Does not replace ordinary text documentation or static PDF/Word workflows.
---

# Connected Tutorials

Create a readable technical explanation whose prose and diagrams teach together. Reproduce the approved OSI example's visual language and interaction using the bundled template; adapt the explanation and diagram to the actual topic.

## Start from the working reference

Read [authoring.md](references/authoring.md) before editing. It describes the small DOM contract used by the renderer.

Create an editable copy in a new or empty output directory:

```sh
python3 <skill-dir>/scripts/scaffold.py <output-directory>
```

The result contains `index.html`, `style.css`, and `guide.js`. The starter is a complete OSI reference example. For other topics, replace its content and diagram before delivery. Edit copied assets, not the installed skill. Do not copy an existing Site's identity, Git history, credentials, or deployment metadata into a new document.

Use a browser-based document for the interactive result. If the user requests PDF or print, provide a static adaptation and explain that scrolling interactions live in the browser version. Use the environment's applicable website/publishing workflow when hosting is part of the task; this skill itself does not require a particular host.

## Plan the explanation and visual together

- Read the supplied material or relevant code. Infer the reader's starting knowledge and intended takeaway from context. Ask only when a missing choice materially changes the tutorial.
- Write an original, attributed explanation grounded in the source. Keep claims accurate; distinguish conceptual models from real implementations. Do not copy an entire linked article. Cite primary sources in the document.
- Make a concept-to-passage map before drawing: what does each passage explain, and exactly which object or relationship makes it visible?
- Choose the diagram from the subject. A stack fits layers; a pipeline fits stages; a graph fits relationships; a memory layout fits bytes and addresses. Do not force every subject into seven plates.
- Keep object identities and positions recognizable as the reader progresses. Use one persistent scene when it stays legible. For a complex chapter, change scene states deliberately and remeasure ports after state changes.

## Preserve the approved visual direction

The bundled CSS is the default design system: warm paper, a slightly darker diagram tray, charcoal line work, fine rules, restrained vermilion emphasis, monospace labels, and generous editorial spacing. Use large, tightly set headings and readable body text. Preserve the hierarchy and spacing as well as the colors.

On desktop, keep a roughly 48/52 split: diagram left, article right. The tray is **sticky under the masthead for the full article**. Use normal page scrolling, not two separately scrolling panes. Keep the tray's ancestors free of overflow/transform rules that break sticky positioning. Fit the diagram and caption within the available height.

Use SVG for addressable diagrams. Give meaningful parts semantic IDs and explicit connection ports. Keep diagram labels readable and connection routes clear of text. Original geometry and illustrations should serve the explanation; do not copy the reference site's branding or artwork.

Use compact technical specimens when useful: a packet layout, bit pattern, code fragment, timeline, or equation. Avoid unrelated dashboard controls, decorative metric cards, marketing sections, and repeated explanation of how the interface works.

## Keep connections honest

Reuse `guide.js` for scrolling, selection, highlighting, and geometry. Most topics require changes only to the HTML and diagram. Its inputs are named SVG ports and annotated prose; there is no OSI-specific layer count or label array.

- Each connected paragraph identifies its exact diagram port(s).
- Draw from the port to the paragraph's margin anchor. Both endpoints are measured in viewport coordinates.
- Update during scrolling, resize, font loading, and diagram transitions. Batch updates through animation frames.
- Hide a connection whose endpoint is offscreen; do not clamp it to a false location at the viewport edge.
- Show one active passage by default. Use several targets only when the passage explains their relationship.
- Give diagram navigation native links and visible keyboard focus. Respect reduced motion. The article must remain readable without JavaScript.

On narrow screens the starter keeps a compact diagram above the text and hides cross-column lines. Check its labels and jump links; tailor the compact diagram when needed. Do not squeeze the desktop composition until text becomes unreadable.

## Verify the result

Run the structural check after authoring:

```sh
python3 <skill-dir>/scripts/check_anchors.py <output-directory>/index.html
```

Check JavaScript syntax if it changed. Then open a working local preview and verify actual browser behavior: scroll from early to late content and back, select a diagram object, resize to a narrow viewport, and check for clipped text or broken links. In the desktop view, verify the tray's top stays fixed and the connector endpoints match the active port and paragraph after scrolling. A structural check alone cannot prove this.

Deliver the working document or its verified hosted URL, with a short invitation to scroll or select a concept. Keep implementation details out of the tutorial unless they are its subject.
