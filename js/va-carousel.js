/* VRA assistant spotlight.
   One assistant at a time, cycling while the visitor is on the page.

   Data comes from the same published sheet the homepage gallery reads, so it
   shows who is actually on the bench rather than a fixed lineup. Names render
   as "First L."; nothing about where an assistant is based is read or shown.

   Motion: cycling pauses on hover and on keyboard focus, and does not start
   at all for visitors who have asked for reduced motion -- they get the
   arrows instead. Photos are preloaded so a change never flashes. */
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

  var wrap = document.getElementById('vaSpotlight');
  if(!wrap) return;
  var stage = wrap.querySelector('.va-stage');
  var pic   = wrap.querySelector('.va-pic');
  var nm    = wrap.querySelector('.va-nm');
  var badge = wrap.querySelector('.va-badge');
  var line  = wrap.querySelector('.va-line');

  function key(n){ var w=(n||'').trim().split(/\s+/); return ((w[0]||'')+'|'+(w[w.length-1]||'')).toLowerCase(); }
  function shortName(n){
    var p=(n||'').trim().split(/\s+/);
    if(p.length<2) return p[0]||'';
    return p.slice(0,-1).join(' ')+' '+p[p.length-1].charAt(0).toUpperCase()+'.';
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
    if(!people.length) return;
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
        line.textContent = p.line || '';
        stage.classList.remove('fading');
      }, reduce ? 0 : 180);
    }
    function go(n){ i = (i + n + people.length) % people.length; paint(); }
    function play(){ if(!reduce && !timer) timer = setInterval(function(){ go(1); }, EVERY); }
    function stop(){ if(timer){ clearInterval(timer); timer = null; } }

    wrap.querySelector('.va-prev').addEventListener('click', function(){ stop(); go(-1); });
    wrap.querySelector('.va-next').addEventListener('click', function(){ stop(); go(1); });
    wrap.addEventListener('mouseenter', stop);
    wrap.addEventListener('mouseleave', play);
    wrap.addEventListener('focusin', stop);
    wrap.addEventListener('focusout', play);
    document.addEventListener('visibilitychange', function(){ document.hidden ? stop() : play(); });

    paint(); wrap.hidden = false; play();
  }

  fetch(SHEET, {cache:'no-store'}).then(function(r){
    if(!r.ok) throw new Error('HTTP '+r.status);
    return r.text();
  }).then(function(t){
    var rows = parseCSV(t);
    if(rows.length < 2) throw new Error('empty');
    var h = rows[0];
    var cN=col(h,'Name'), cA=col(h,'Availability'), cL=col(h,'Carousel line');
    var cP=col(h,'Photo'); if(cP===-1) cP=col(h,'Photo Link');
    var out=[];
    for(var r=1;r<rows.length;r++){
      var name = cN!==-1 ? (rows[r][cN]||'').trim() : '';
      var avail = cA!==-1 ? (rows[r][cA]||'').trim() : '';
      if(!name || !avail) continue;
      var photo = LOCAL[key(name)] || '';
      if(!photo && cP!==-1){ var id=driveId((rows[r][cP]||'').trim());
        if(id) photo='https://lh3.googleusercontent.com/d/'+id+'=w320'; }
      out.push({name:name, availability:avail, photo:photo,
                line: cL!==-1 ? (rows[r][cL]||'').trim() : ''});
    }
    start(out);
  }).catch(function(){ /* leave hidden */ });
})();
