# Authoring contract

The template is an editable reference, not a generator that assumes seven layers. Preserve the layout shell and replace its technical content. `guide.js` has no external dependencies.

## Required shell

Keep `.masthead`, `.spread`, `.tray`, `article`, `#focus-label`, `.mobile-layers`, `#progress`, and the empty `svg#connections`. The tray is the grid's first child and remains sticky throughout the article. Its `svg#stack` is a name retained from the reference; its contents may be any diagram.

Keep useful diagram `title` and `desc` elements, hatch definitions only when used, and a `viewBox` suited to the actual geometry. Update the page title, description, masthead, figure heading, figure caption, sources, and reading-time estimate alongside the prose. OSI-specific construction lines and the DATA→BITS caption are sample content, not universal decoration.

## Explanatory passages

Each section is a reading step with a unique ID and short label. The optional number is an editorial label, not an array index.

```html
<section id="resolve-name" class="layer-section"
         data-step="resolve-name" data-label="DNS lookup" data-number="01">
  <div class="section-meta"><span>01</span><span>FIND THE SERVER</span></div>
  <h2>Resolve the name</h2>
  <p class="connected" data-connect="resolver-out">
    <span class="text-port" aria-hidden="true"></span>
    The resolver returns the address needed for the next step.
  </p>
</section>
```

`data-connect` is a whitespace-separated list of **port IDs**, not CSS selectors or step IDs. Multiple passages may refer to the same port. A section may contain several connected paragraphs; the renderer follows the paragraph nearest the reading line. Use stable lowercase hyphenated identifiers without whitespace. Each paragraph needs its own `.text-port` child, positioned beside the first line.

## Diagram objects and ports

```html
<a class="layer-link" data-layer="resolver" href="#resolve-name"
   aria-label="Read about the DNS resolver">
  <g class="layer-shape">
    <rect class="layer-top" x="70" y="100" width="230" height="80"/>
    <text class="layer-name" x="95" y="147">DNS resolver</text>
    <circle class="layer-port" data-port="resolver-out"
            cx="300" cy="140" r="3"/>
  </g>
</a>
```

Each `data-layer` is a unique semantic object ID. The names `layer-link`, `layer-top`, etc. are styling hooks from the reference, not a requirement to depict layers. A component can have several ports, each with a unique `data-port` value. Put the port inside the transformed group so it moves with its object. Do not use `display:none` on measured ports; an invisible but measurable circle is fine.

The renderer measures the centers of the circles' screen bounding boxes. This handles SVG scaling and translated groups without mixing SVG user units with page pixels. Keep the overlay viewport-fixed, without a scaled viewBox or transformed ancestor. If changing that coordinate model, explicitly convert both endpoints into overlay coordinates.

Use a real SVG `a` with a section fragment URL for keyboard and pointer navigation. Each object links to its primary explanation; repeated mentions can still connect to it. The renderer derives compact jump navigation from the document's steps.

## Shared state

The active section gets `.active`; the active connected paragraph gets `.passage-active`. Diagram objects owning a requested port get `.active` and `aria-current="true"`. The caption uses `data-label` (or the section heading) and optional `data-number`.

The renderer dispatches `connected-tutorial:step` on `document` with:

```js
{ step: 'resolve-name', ports: ['resolver-out'] }
```

For optional scene changes, listen to that event, update the SVG, then dispatch `connected-tutorial:layout`. Avoid rebuilding the document or changing semantic port IDs on every scroll frame. Keep expected ports measurable whenever their paragraph is active. The default engine follows short CSS transitions; longer custom animation must request layout updates while moving.

## Style and responsive changes

Start with the shipped CSS. The palette and typography reproduce the approved OSI example. Google Fonts are optional enhancements with local fallbacks; the document does not depend on an API or build system.

The desktop breakpoint is 760px in CSS and JavaScript. Change both if adjusting it. Below that size the tray becomes a sticky top figure and cross-column connectors are hidden. For complex diagrams provide a simpler compact view, preserving meaning and native jump links. Print styles remove sticky positioning and connections.

For long labels or large diagrams, resize or rearrange geometry rather than shrinking all text. Test actual viewport height as well as width. Attribution belongs in sources at the end, not interactive implementation callouts.
