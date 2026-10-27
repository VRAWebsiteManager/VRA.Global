/* VRA assistant carousel.
   Renders a scrolling strip of currently-available assistants.

   Data comes from the same published sheet the homepage gallery reads, so the
   strip reflects who is actually on the bench rather than a fixed lineup that
   goes stale. Names render as "First L." and nothing about where an assistant
   is based is read or shown.

   Photos: we prefer a local file already on the site (keyed by first+last
   name), fall back to the sheet's Drive photo for anyone new, and fall back
   again to initials. If the sheet cannot be reached the whole block stays
   hidden rather than rendering empty or stale. */
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

  var wrap = document.getElementById('vaCarousel');
  var track = document.getElementById('vaTrack');
  if(!wrap || !track) return;

  function key(n){
    var w = (n||'').trim().split(/\s+/);
    return ((w[0]||'') + '|' + (w[w.length-1]||'')).toLowerCase();
  }
  function shortName(n){
    var p = (n||'').trim().split(/\s+/);
    if(p.length < 2) return p[0] || '';
    return p.slice(0,-1).join(' ') + ' ' + p[p.length-1].charAt(0).toUpperCase() + '.';
  }
  function initials(n){
    return (n||'').split(/\s+/).map(function(w){return w[0];}).slice(0,2).join('').toUpperCase();
  }
  function driveId(u){
    var m1 = /\/d\/([-\w]{20,})/.exec(u||'') || /[?&]id=([-\w]{20,})/.exec(u||'');
    return m1 ? m1[1] : '';
  }
  function col(h, name){
    for(var i=0;i<h.length;i++){ if((h[i]||'').trim().toLowerCase() === name.toLowerCase()) return i; }
    return -1;
  }
  /* Minimal CSV reader: handles quoted fields and embedded commas/newlines. */
  function parseCSV(t){
    var rows=[], row=[], f='', q=false, i;
    for(i=0;i<t.length;i++){
      var c=t[i];
      if(q){
        if(c === '"'){ if(t[i+1] === '"'){ f+='"'; i++; } else q=false; }
        else f+=c;
      } else if(c === '"'){ q=true; }
      else if(c === ','){ row.push(f); f=''; }
      else if(c === '\n' || c === '\r'){
        if(c === '\r' && t[i+1] === '\n') i++;
        row.push(f); f='';
        if(row.length>1 || row[0] !== '') rows.push(row);
        row=[];
      } else f+=c;
    }
    if(f !== '' || row.length){ row.push(f); rows.push(row); }
    return rows;
  }

  function card(p){
    var img = p.photo
      ? '<div class="va-pic"><img src="'+p.photo+'" alt="" loading="lazy" onerror="this.parentNode.textContent=\''+initials(p.name)+'\';"></div>'
      : '<div class="va-pic va-ini">'+initials(p.name)+'</div>';
    var badge = p.availability
      ? '<span class="va-badge'+(p.availability === 'Part-Time' ? ' pt' : '')+'">'+p.availability+'</span>' : '';
    var line = p.line ? '<p class="va-line">'+p.line+'</p>' : '';
    return '<article class="va-card">'+img+
           '<div class="va-nm">'+shortName(p.name)+'</div>'+badge+line+'</article>';
  }

  function render(people){
    if(!people.length) return;
    track.innerHTML = people.map(card).join('');
    wrap.hidden = false;
    var prev = wrap.querySelector('.va-prev'), next = wrap.querySelector('.va-next');
    function step(dir){
      var c = track.querySelector('.va-card');
      track.scrollBy({left: dir * ((c ? c.offsetWidth : 150) + 16) * 2, behavior:'smooth'});
    }
    prev.addEventListener('click', function(){ step(-1); });
    next.addEventListener('click', function(){ step(1); });
    function arrows(){
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
    }
    track.addEventListener('scroll', arrows); window.addEventListener('resize', arrows); arrows();
  }

  fetch(SHEET, {cache:'no-store'}).then(function(r){
    if(!r.ok) throw new Error('HTTP ' + r.status);
    return r.text();
  }).then(function(t){
    var rows = parseCSV(t);
    if(rows.length < 2) throw new Error('empty');
    var h = rows[0];
    var cN = col(h,'Name'), cA = col(h,'Availability'), cP = col(h,'Photo'),
        cL = col(h,'Carousel line');
    if(cP === -1) cP = col(h,'Photo Link');
    var out = [];
    for(var r=1;r<rows.length;r++){
      var name = cN !== -1 ? (rows[r][cN]||'').trim() : '';
      if(!name) continue;
      var avail = cA !== -1 ? (rows[r][cA]||'').trim() : '';
      if(!avail) continue;                    /* not currently available */
      var photo = LOCAL[key(name)] || '';
      if(!photo && cP !== -1){
        var id = driveId((rows[r][cP]||'').trim());
        if(id) photo = 'https://lh3.googleusercontent.com/d/' + id + '=w240';
      }
      out.push({ name:name, availability:avail, photo:photo,
                 line: cL !== -1 ? (rows[r][cL]||'').trim() : '' });
    }
    render(out);
  }).catch(function(){ /* leave the block hidden */ });
})();
