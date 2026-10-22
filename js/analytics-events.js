/* VRA GA4 conversion events.

   Sends four events through the gtag setup already on every page
   (G-ZLM9HBC8PK, configured inline in <head>):

     form_submit_needs_assessment   the Needs Assessment form, after Formspree returns ok
     form_submit_contact            the Contact form, after Formspree returns ok
     consult_booked                 a Calendly booking completed in an embedded widget
     calendly_click                 a click on a link that opens Calendly

   The two form events are fired by the page's own submit handler inside the
   success branch, so a failed POST sends nothing. The two Calendly events are
   wired up here.

   Nothing in this file touches the DOM. If gtag is missing or blocked the calls
   are swallowed, so an ad blocker cannot break a form submission. */
(function () {
  'use strict';

  var KEY = 'vra_first_touch';   /* written by attribution.js; read-only here */

  function query(name) {
    try { return new URLSearchParams(window.location.search).get(name) || ''; }
    catch (e) { return ''; }
  }

  function pagePath() {
    return (window.location.pathname || '/').replace(/\.html$/, '') || '/';
  }

  /* The campaign tag, for tying a submission back to the post that produced it.
     Reads the live query string first, then falls back to the first-touch value
     attribution.js put in sessionStorage -- a visitor who lands on a tagged link
     and then clicks through to the form has no query string left by the time
     they submit, which is the whole reason the stored copy exists. */
  function eventSource() {
    var tagged = query('src') || query('ref');
    if (tagged) return tagged.slice(0, 80);
    try {
      var ft = JSON.parse(sessionStorage.getItem(KEY) || 'null');
      if (ft && ft.source) return String(ft.source).slice(0, 80);
    } catch (e) {}
    return 'unknown';
  }

  function track(name, params) {
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', name, params || {});
      }
    } catch (e) {}
  }

  window.vraTrack = track;
  window.vraEventSource = eventSource;

  /* calendly_click -- fires on the click, not on a booking. These links open in a
     new tab, so this is the only signal this page ever gets. */
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href*="calendly.com"]') : null;
    if (!a) return;
    track('calendly_click', { page_path: pagePath(), src: eventSource() });
  }, true);

  /* consult_booked -- Calendly posts this message from an embedded widget when a
     booking completes. Today every Calendly link on the site opens a new tab
     instead of embedding, so nothing posts to this window and this never fires.
     It is here so that the day a page embeds the widget, the event works without
     another deploy. */
  window.addEventListener('message', function (e) {
    var host = '';
    try { host = new URL(e.origin).hostname.replace(/^www\./, ''); } catch (err) { return; }
    if (host !== 'calendly.com' && !/\.calendly\.com$/.test(host)) return;
    var d = e.data;
    if (!d || typeof d !== 'object' || d.event !== 'calendly.event_scheduled') return;
    track('consult_booked', { page_path: pagePath(), src: eventSource() });
  });
})();
