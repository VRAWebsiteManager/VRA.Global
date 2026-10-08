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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', stamp);
  } else {
    stamp();
  }
})();
