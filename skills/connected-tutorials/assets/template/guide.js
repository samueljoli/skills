(() => {
  'use strict';
  const svgNS = 'http://www.w3.org/2000/svg';
  const steps = [...document.querySelectorAll('[data-step]')];
  const overlay = document.getElementById('connections');
  const focusLabel = document.getElementById('focus-label');
  const progress = document.getElementById('progress');
  const tray = document.querySelector('.tray');
  const header = document.querySelector('.masthead');
  const mobileNav = document.querySelector('.mobile-layers');
  if (!steps.length || !overlay || !tray || !header) return;
  const passages = steps.flatMap(step => [...step.querySelectorAll('[data-connect]')].map(el => ({ step, el })));
  if (!passages.length) return;
  const mobile = matchMedia('(max-width:760px)');
  const reduced = matchMedia('(prefers-reduced-motion:reduce)');
  let active = null;
  let frame = 0;
  let animateUntil = 0;
  let connections = [];
  const label = step => step.dataset.label || step.querySelector('h2,h3')?.textContent || step.dataset.step;
  const targets = passage => [...new Set(passage.dataset.connect.trim().split(/\s+/).filter(Boolean))];
  const getPort = name => [...tray.querySelectorAll('[data-port]')].find(el => el.dataset.port === name);
  function svg(tag, attrs = {}) {
    const el = document.createElementNS(svgNS,tag);
    Object.entries(attrs).forEach(([key,value]) => el.setAttribute(key,value));
    return el;
  }
  if (mobileNav) {
    mobileNav.replaceChildren();
    steps.forEach((step,index) => {
      const link = document.createElement('a');
      link.href = `#${step.id}`;
      link.dataset.jump = step.dataset.step;
      link.setAttribute('aria-label',label(step));
      link.textContent = step.dataset.number || String(index+1).padStart(2,'0');
      mobileNav.append(link);
    });
  }
  overlay.replaceChildren();
  function activate(selected) {
    if (active === selected.el) return;
    active = selected.el;
    steps.forEach(step => step.classList.toggle('active',step === selected.step));
    passages.forEach(p => p.el.classList.toggle('passage-active',p.el === active));
    const names = targets(active);
    document.dispatchEvent(new CustomEvent('connected-tutorial:step', {detail:{step:selected.step.dataset.step,ports:names}}));
    const owners = names.map(name => getPort(name)?.closest('[data-layer]')).filter(Boolean);
    tray.querySelectorAll('[data-layer]').forEach(el => {
      const chosen = owners.includes(el);
      el.classList.toggle('active',chosen);
      chosen ? el.setAttribute('aria-current','true') : el.removeAttribute('aria-current');
    });
    mobileNav?.querySelectorAll('[data-jump]').forEach(el => el.setAttribute('aria-current',String(el.dataset.jump === selected.step.dataset.step)));
    if (focusLabel) focusLabel.textContent = [selected.step.dataset.number,label(selected.step).toUpperCase()].filter(Boolean).join(' / ');
    overlay.replaceChildren();
    connections = names.map(name => {
      const group = svg('g');
      const halo = svg('path',{class:'connector-halo'});
      const line = svg('path',{class:'connector-line'});
      const start = svg('circle',{class:'connector-start',r:4});
      const end = svg('circle',{class:'connector-end',r:4});
      group.append(halo,line,start,end);overlay.append(group);
      return {name,group,halo,line,start,end};
    });
    animateUntil = performance.now() + (reduced.matches ? 0 : 350);
  }
  function update() {
    frame = 0;
    const headBottom = header.getBoundingClientRect().bottom;
    const readingTop = mobile.matches ? tray.getBoundingClientRect().bottom : headBottom;
    const readingLine = readingTop + (innerHeight-readingTop)*.35;
    let selected = passages[0];
    let distance = Infinity;
    // Prefer a visible passage over a nearer but already offscreen anchor.
    for (const item of passages) {
      const rect = item.el.getBoundingClientRect();
      const visible = rect.bottom > readingTop + 12 && rect.top < innerHeight - 16;
      const score = Math.abs(rect.top-readingLine) + (visible ? 0 : innerHeight * 2);
      if (score < distance) {distance=score;selected=item;}
    }
    activate(selected);
    const range = document.documentElement.scrollHeight-innerHeight;
    if (progress) progress.style.width = `${range > 0 ? Math.max(0,Math.min(100,scrollY/range*100)) : 0}%`;
    const target = active.querySelector('.text-port')?.getBoundingClientRect();
    connections.forEach(connection => {
      const port = getPort(connection.name)?.getBoundingClientRect();
      if (!target || !port || mobile.matches) {connection.group.style.display='none';return;}
      const x1=port.left+port.width/2, y1=port.top+port.height/2;
      const x2=target.left+target.width/2, y2=target.top+target.height/2;
      const visible = y2 > headBottom+12 && y2 < innerHeight-16 && y1 > headBottom && y1 < innerHeight;
      connection.group.style.display=visible?'':'none';
      if (!visible) return;
      const bend=Math.max(20,Math.abs(x2-x1)*.48);
      const d=`M${x1},${y1} C${x1+bend},${y1} ${x2-bend},${y2} ${x2},${y2}`;
      connection.line.setAttribute('d',d);connection.halo.setAttribute('d',d);
      connection.start.setAttribute('cx',x1);connection.start.setAttribute('cy',y1);
      connection.end.setAttribute('cx',x2);connection.end.setAttribute('cy',y2);
    });
    if (performance.now() < animateUntil) schedule();
  }
  function schedule() {if (!frame) frame=requestAnimationFrame(update);}
  function jump(event) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
    const anchor=event.target.closest('a[href^="#"]');
    if (!anchor || anchor.target === '_blank') return;
    const fragment=anchor.getAttribute('href');
    let id;
    try {id=decodeURIComponent(fragment.slice(1));} catch {return;}
    const target=document.getElementById(id);
    if (!target) return;
    event.preventDefault();
    const offset=header.getBoundingClientRect().height+(mobile.matches?tray.getBoundingClientRect().height+24:38);
    if (event.detail === 0) {
      const hadTabindex=target.hasAttribute('tabindex');
      if (!hadTabindex) target.setAttribute('tabindex','-1');
      target.focus({preventScroll:true});
      if (!hadTabindex) target.addEventListener('blur',()=>target.removeAttribute('tabindex'),{once:true});
    }
    try {history.replaceState(null,'',fragment);} catch { /* file:// still supports reading and scrolling. */ }
    scrollTo({top:id==='top'?0:target.getBoundingClientRect().top+scrollY-offset,behavior:reduced.matches?'auto':'smooth'});
    schedule();
  }
  document.addEventListener('click',jump);
  document.addEventListener('connected-tutorial:layout',()=>{animateUntil=performance.now()+350;schedule();});
  window.addEventListener('scroll',schedule,{passive:true});
  window.addEventListener('resize',schedule);
  window.addEventListener('pageshow',schedule);
  mobile.addEventListener('change',schedule);
  reduced.addEventListener('change',schedule);
  const observer=new ResizeObserver(schedule);
  observer.observe(document.querySelector('article'));observer.observe(tray);
  ['pointerover','pointerout','focusin','focusout'].forEach(type=>tray.addEventListener(type,()=>{animateUntil=performance.now()+350;schedule();}));
  document.fonts?.ready.then(schedule);
  schedule();
})();
