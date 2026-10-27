/* VRA assistant photos -- two layouts off one data source.

   #vaSpotlight: one assistant at a time, cycling, for a block with enough
   running prose to wrap around it.
   #vaStrip: a scrolling row of assistants, for a section that has no body
   copy to carry a single large photo.

   Data comes from the same published sheet the homepage gallery reads, so it
   shows who is actually on the bench rather than a fixed lineup. Names render
   as "First L."; nothing about where an assistant is based is read or shown.

   Motion: this is illustrative, not a control, so there is nothing to click.
   Cycling pauses on hover, on keyboard focus and when the tab is hidden, and
   never starts for visitors who have asked for reduced motion -- they simply
   see one assistant. Photos are preloaded so a change never flashes. */
(function(){
  var SHEET = 'https://docs.google.com/spreadsheets/d/1S2oToaS9ltgvkL9rsWRKls5UlQO8CgQWOnqdPf_xaX8/gviz/tq?tqx=out:csv&gid=0';
  var LOCAL = {
  "aldrin|bandarlipe": "/photos/aldrin-bandarlipe-headshot-sharp.png",
  "brillian|pelayo": "/photos/brillian-pelayo-sharp.png",
  "buen|talabon": "/photos/buen-talabon-plain.png",
  "danica|austria": "/photos/danica-austria-sharp.png",
  "hannah|mirabete": "/photos/hannah-mirabete-sharp.png",
  "jahaziel|dimas": "/photos/jahaziel-dimas-plain.png",
  "jayvee|guiruela": "/photos/jayvee-guiruela-plain.png",
  "jerico|burdios": "/photos/jerico-burdios-plain.png",
  "jervyn|guianan": "/photos/jervyn-guianan-sharp.png",
  "jesswin|siegel": "/photos/jesswin-siegel-plain.png",
  "john|ilagan": "/photos/john-ilagan-sharp.png",
  "junada|palman": "/photos/junada-palman-plain.png",
  "kim|caro": "/photos/kim-caro-sharp.png",
  "kyla|tayoan": "/photos/kyla-tayoan-plain.png",
  "manuel|sesaldo": "/photos/manuel-sesaldo-sharp.png",
  "rodolfo|rueca": "/photos/rodolfo-rueca-plain.png",
  "samantha|baloloy": "/photos/samantha-baloloy-plain.png",
  "vincent|roxas": "/photos/vincent-roxas-sharp.png"
};
  var EVERY = 4500;

  var wrap  = document.getElementById('vaSpotlight');
  var strip = document.getElementById('vaStrip');
  if(!wrap && !strip) return;
  var stage, pic, nm, badge;
  if(wrap){
    stage = wrap.querySelector('.va-stage');
    pic   = wrap.querySelector('.va-pic');
    nm    = wrap.querySelector('.va-nm');
    badge = wrap.querySelector('.va-badge');
  }

  function key(n){ var w=(n||'').trim().split(/\s+/); return ((w[0]||'')+'|'+(w[w.length-1]||'')).toLowerCase(); }
  function shortName(n){
    var p=(n||'').trim().split(/\s+/);
    if(p.length<2) return p[0]||'';
    return p.slice(0,-1).join(' ')+' '+p[p.length-1].charAt(0).toUpperCase()+'.';
  }
  function firstLast(n){
    var p=(n||'').trim().split(/\s+/);
    if(p.length<2) return p[0]||'';
    return p[0]+' '+p[p.length-1].charAt(0).toUpperCase()+'.';
  }
  function initials(n){ return (n||'').split(/\s+/).map(function(w){return w[0];}).slice(0,2).join('').toUpperCase(); }
  function driveId(u){ var r=/\/d\/([-\w]{20,})/.exec(u||'')||/[?&]id=([-\w]{20,})/.exec(u||''); return r?r[1]:''; }
  function col(h,n){ for(var i=0;i<h.length;i++){ if((h[i]||'').trim().toLowerCase()===n.toLowerCase()) return i; } return -1; }
  function parseCSV(t){
    var rows=[],row=[],f='',q=false,i;
    for(i=0;i<t.length;i++){
      var c=t[i];
      if(q){ if(c==='"'){ if(t[i+1]==='"'){ f+='"'; i++; } else q=false; } else f+=c; }
      else if(c==='"'){ q=true; }
      else if(c===','){ row.push(f); f=''; }
      else if(c==='\n'||c==='\r'){ if(c==='\r'&&t[i+1]==='\n') i++; row.push(f); f='';
        if(row.length>1||row[0]!=='') rows.push(row); row=[]; }
      else f+=c;
    }
    if(f!==''||row.length){ row.push(f); rows.push(row); }
    return rows;
  }

  function start(people){
    if(!wrap || !people.length) return;
    people.forEach(function(p){ if(p.photo){ var i=new Image(); i.src=p.photo; } });
    var i = 0, timer = null;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function paint(){
      var p = people[i];
      stage.classList.add('fading');
      setTimeout(function(){
        pic.innerHTML = p.photo ? '<img src="'+p.photo+'" alt="">' : '';
        pic.classList.toggle('va-ini', !p.photo);
        if(!p.photo) pic.textContent = initials(p.name);
        nm.textContent = shortName(p.name);
        badge.textContent = p.availability || '';
        badge.className = 'va-badge' + (p.availability === 'Part-Time' ? ' pt' : '') + (p.availability ? '' : ' empty');
        stage.classList.remove('fading');
      }, reduce ? 0 : 180);
    }
    function go(n){ i = (i + n + people.length) % people.length; paint(); }
    function play(){ if(!reduce && !timer) timer = setInterval(function(){ go(1); }, EVERY); }
    function stop(){ if(timer){ clearInterval(timer); timer = null; } }

    wrap.addEventListener('mouseenter', stop);
    wrap.addEventListener('mouseleave', play);
    wrap.addEventListener('focusin', stop);
    wrap.addEventListener('focusout', play);
    document.addEventListener('visibilitychange', function(){ document.hidden ? stop() : play(); });

    paint(); wrap.hidden = false; play();
  }

  /* A row of assistants, duplicated once so the scroll loop is seamless.
     Nothing here is clickable -- it shows the range of the bench, it is not
     a picker. The row holds still until it is scrolled into view, so a
     visitor always meets it as a full line rather than mid-slide. */
  function startStrip(people){
    if(!strip || people.length < 3) return;
    var track = strip.querySelector('.va-strip-track');
    function chip(p){
      var d = document.createElement('div');
      d.className = 'va-chip';
      d.setAttribute('aria-hidden','true');
      var face = p.photo
        ? '<img src="'+p.photo+'" alt="" loading="lazy">'
        : '<span class="va-ini">'+initials(p.name)+'</span>';
      d.innerHTML = face
        + '<span class="nm">'+firstLast(p.name)+'</span>'
        + '<span class="av'+(p.availability==='Part-Time'?' pt':'')+'">'+(p.availability||'')+'</span>';
      return d;
    }
    people.forEach(function(p){ track.appendChild(chip(p)); });
    people.forEach(function(p){ track.appendChild(chip(p)); });
    strip.hidden = false;

    if('IntersectionObserver' in window){
      var io = new IntersectionObserver(function(es){
        es.forEach(function(e){ if(e.isIntersecting){ strip.classList.add('in-view'); io.unobserve(e.target); } });
      }, {threshold:0.25});
      io.observe(strip);
    } else {
      strip.classList.add('in-view');
    }
  }

  fetch(SHEET, {cache:'no-store'}).then(function(r){
    if(!r.ok) throw new Error('HTTP '+r.status);
    return r.text();
  }).then(function(t){
    var rows = parseCSV(t);
    if(rows.length < 2) throw new Error('empty');
    var h = rows[0];
    var cN=col(h,'Name'), cA=col(h,'Availability');
    var cP=col(h,'Photo'); if(cP===-1) cP=col(h,'Photo Link');
    var out=[];
    for(var r=1;r<rows.length;r++){
      var name = cN!==-1 ? (rows[r][cN]||'').trim() : '';
      var avail = cA!==-1 ? (rows[r][cA]||'').trim() : '';
      if(!name || !avail) continue;
      var photo = LOCAL[key(name)] || '';
      if(!photo && cP!==-1){ var id=driveId((rows[r][cP]||'').trim());
        if(id) photo='https://lh3.googleusercontent.com/d/'+id+'=w320'; }
      out.push({name:name, availability:avail, photo:photo,});
    }
    start(out);
    startStrip(out);
  }).catch(function(){ /* leave hidden */ });
})();
