/* VRA first-touch attribution.
   Records where a visitor entered the site, keeps it for the whole session, and
   stamps it onto any form's hidden "src" field. The leads pull script maps "src"
   to the "Came from" column in the VRA Leads sheet.

   First touch, not last touch: someone who arrives from LinkedIn, reads three
   pages and then fills in the contact form should be credited to LinkedIn, not
   to /contact.

   The same first touch is also sent to GA4, as a user property on every event
   and as a one-per-session first_touch event. Without it GA4 only ever sees the
   referrer of the page that arrived, so a visitor who lands from ChatGPT, reads
   four pages and books on the fifth shows up as a consult click from nowhere. */
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
  var isNewTouch = false;
  if (!first || !first.source) {
    var now = current();
    if (now.source) {
      first = now;
      isNewTouch = true;
      try { sessionStorage.setItem(KEY, JSON.stringify(now)); } catch (e) {}
    }
  }

  /* Collapse the labels into a handful of channels, so AI traffic can be read as
     one channel without listing every assistant by name, while first_touch_source
     still says which one it was. */
  function channelOf(source) {
    if (!source) return 'unknown';
    /* utm_source arrives as "linkedin/eta-launch", a referrer as plain "linkedin",
       so match on the part before the slash or both spellings split apart. */
    var base = String(source).split('/')[0];
    if (base === 'ai') return 'ai';
    if (base === 'google' || base === 'bing' || base === 'duckduckgo') return 'search';
    if (base === 'linkedin' || base === 'facebook' || base === 'x') return 'social';
    if (base === 'direct') return 'direct';
    return 'referral';
  }

  /* gtag is defined synchronously in the page head and queues into dataLayer, so
     this runs correctly even before the async GA4 script has finished loading. */
  function sendToGA4(ft, isNew) {
    if (!ft || !ft.source || typeof gtag !== 'function') return;
    try {
      /* Rides along on every later event in the session, so a conversion can be
         read back to where the visitor originally came from. */
      gtag('set', 'user_properties', {
        first_touch_source: String(ft.source).slice(0, 36),
        first_touch_channel: channelOf(ft.source)
      });
      if (!isNew) return;
      gtag('event', 'first_touch', {
        source: String(ft.source).slice(0, 100),
        channel: channelOf(ft.source),
        landing_page: String(ft.landing || '/').slice(0, 100),
        medium: String(ft.medium || '').slice(0, 100)
      });
    } catch (e) {}
  }

  sendToGA4(first, isNewTouch);

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
