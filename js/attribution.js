/* VRA first-touch attribution.
   Records where a visitor entered the site, keeps it for the whole session, and
   stamps it onto any form's hidden "src" field. The leads pull script maps "src"
   to the "Came from" column in the VRA Leads sheet.

   First touch, not last touch: someone who arrives from LinkedIn, reads three
   pages and then fills in the contact form should be credited to LinkedIn, not
   to /contact. */
(function () {
  'use strict';

  var KEY = 'vra_first_touch';

  function query(name) {
    try { return new URLSearchParams(window.location.search).get(name) || ''; }
    catch (e) { return ''; }
  }

  function hostOf(url) {
    try { return new URL(url).hostname.replace(/^www\./, ''); }
    catch (e) { return ''; }
  }

  /* Collapse the hosts we actually care about into stable labels, so the sheet
     doesn't end up with six spellings of LinkedIn. */
  function label(host) {
    if (!host) return '';
    /* AI assistants. Grouped under an 'ai/' prefix so the sheet can filter the whole
       channel, while still showing which assistant sent them. These must come before
       the google test below, or gemini.google.com is swallowed as plain google. */
    if (/(^|\.)chatgpt\.com$/.test(host) || /(^|\.)openai\.com$/.test(host)) return 'ai/chatgpt';
    if (/(^|\.)perplexity\.ai$/.test(host)) return 'ai/perplexity';
    if (/(^|\.)claude\.ai$/.test(host)) return 'ai/claude';
    if (/(^|\.)copilot\.microsoft\.com$/.test(host)) return 'ai/copilot';
    if (/(^|\.)gemini\.google\.com$/.test(host)) return 'ai/gemini';
    if (host === 'lnkd.in' || /(^|\.)linkedin\.com$/.test(host)) return 'linkedin';
    if (/(^|\.)google\./.test(host)) return 'google';
    if (/(^|\.)bing\.com$/.test(host)) return 'bing';
    if (/(^|\.)duckduckgo\.com$/.test(host)) return 'duckduckgo';
    if (host === 'l.facebook.com' || /(^|\.)facebook\.com$/.test(host)) return 'facebook';
    if (/(^|\.)t\.co$/.test(host) || /(^|\.)x\.com$/.test(host)) return 'x';
    return host;
  }

  function path() {
    return (window.location.pathname || '/').replace(/\.html$/, '') || '/';
  }

  function current() {
    var tagged = query('src') || query('ref');   // legacy short tags still in use
    var utmSource = query('utm_source');
    var utmCampaign = query('utm_campaign');
    var utmMedium = query('utm_medium');
    var refHost = label(hostOf(document.referrer || ''));
    var source = '';

    if (tagged) {
      source = tagged.slice(0, 80);
    } else if (utmSource) {
      source = utmSource + (utmCampaign ? '/' + utmCampaign : '');
    } else if (refHost && refHost !== 'vra.global') {
      source = refHost;
    } else if (!document.referrer) {
      /* No referrer and no tag. Genuinely typed/bookmarked, or a referrer the
         browser stripped - LinkedIn's in-app browser does this routinely, which
         is why posted links need utm tags to be counted correctly. */
      source = 'direct';
    }
    /* An internal referrer leaves source empty, so browsing the site never
       overwrites how the visitor originally arrived. */

    return { source: source, medium: utmMedium, landing: path() };
  }

  function stored() {
    try { return JSON.parse(sessionStorage.getItem(KEY) || 'null'); }
    catch (e) { return null; }
  }

  var first = stored();
  if (!first || !first.source) {
    var now = current();
    if (now.source) {
      first = now;
      try { sessionStorage.setItem(KEY, JSON.stringify(now)); } catch (e) {}
    }
  }

  /* A single readable line for the sheet, e.g.
     "linkedin/eta-launch | entered /just-bought-a-business | sent from /contact" */
  window.vraSource = function () {
    var ft = first || current();
    var bits = [ft.source || 'unknown'];
    if (ft.medium) bits.push(ft.medium);
    bits.push('entered ' + (ft.landing || '/'));
    var here = path();
    if (here !== ft.landing) bits.push('sent from ' + here);
    return bits.join(' | ');
  };

  function stamp() {
    var fields = document.querySelectorAll('input[name="src"]');
    for (var i = 0; i < fields.length; i++) fields[i].value = window.vraSource();
  }

  /* The /consult links are hand-written with utm_source=vra-site, which tells
     Calendly nothing: every booking looks identical whether the visitor came
     from LinkedIn, a search or an AI assistant. First touch is known here but
     dies at the redirect, so rewrite the links before anyone clicks one and
     carry it across the handoff.

     utm_source becomes the real first touch and utm_term the page they entered
     on. utm_medium, utm_campaign and utm_content are left alone -- utm_content
     already records which page the button sat on, which is the last touch. If
     first touch is unknown the link is left exactly as authored. */
  function tagConsultLinks() {
    var ft = first || current();
    if (!ft || !ft.source) return;
    var links = document.querySelectorAll('a[href*="/consult"]');
    for (var i = 0; i < links.length; i++) {
      var a = links[i], href = a.getAttribute('href'), u;
      if (!href) continue;
      try { u = new URL(href, window.location.origin); } catch (e) { continue; }
      if (u.pathname !== '/consult') continue;
      u.searchParams.set('utm_source', ft.source);
      if (ft.landing) u.searchParams.set('utm_term', ft.landing);
      a.setAttribute('href', u.pathname + u.search + u.hash);
    }
  }

  function onReady() {
    stamp();
    tagConsultLinks();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
