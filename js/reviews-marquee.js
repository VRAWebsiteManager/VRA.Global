/* VRA client reviews, scrolling.

   One list, used by every lead-capture page, so a review edited here changes
   everywhere instead of drifting between hand-kept copies.

   Every line is a client's own words, lifted whole from the video transcript
   in watch/. scripts/check_quotes.py reads the `quote:` fields below and
   checks each one against its transcript, so an edit that rewords a client
   fails the build rather than going live. Leave the words alone.

   Markup a page needs:
     <div class="review-marquee" id="reviewMarquee" aria-label="What clients say">
       <div class="review-track"></div>
     </div> */
(function(){
  var REVIEWS = [
    { quote: "I cannot think of running my business without a virtual assistant.",
      by: "Emily Zakhem, Keller Williams Memorial &middot; 60-day check-in" },
    { quote: "I am surprised that we didn't take this step earlier.",
      by: "Montse Foster, Keller Williams Memorial &middot; 90-day check-in" },
    { quote: "As I was saying, I don't know how I made it this long without even having a VA.",
      by: "Rayan Saleh &middot; Owner, The Butcher&rsquo;s Grille" },
    { quote: "He&rsquo;s given me my life back, so I&rsquo;m not working 16 hours a day.",
      by: "Lisa Rigdon, REALTOR&reg; &middot; Keller Williams Memorial Rookie of the Year" },
    { quote: "I would say, honestly, she's already paid for her first year of work.",
      by: "Clay Stagg &middot; River Road Reservations" },
    { quote: "She&rsquo;s a self-starter, finding things we didn&rsquo;t even expect her to find.",
      by: "Debbie Yates, President &amp; Escrow Officer &middot; Key Title of Texas" },
    { quote: "But instead of this entry-level associate that I thought I was getting, I got a game changer.",
      by: "Elle Haynes &middot; President of Escrow Operations, Elevate Compliance Partners" },
    { quote: "He handles all of our CDAs &mdash; this month we&rsquo;ve had over 400.",
      by: "Victoria Williams, Market Center Administrator &middot; Keller Williams Memorial" },
    { quote: "She has been way more self-sufficient than I could have ever asked for.",
      by: "Hannah DuBose &middot; Keller Williams Heritage" },
    { quote: "Josh is one of the most capable CRE assistants I&rsquo;ve worked with.",
      by: "Sepideh Akhavi &middot; Keller Williams Commercial" },
    { quote: "My VA is amazing &mdash; prompt, pleasant, and productive.",
      by: "Kim Dixon-Dudley, Broker Associate &middot; Compass" },
    { quote: "She has saved so much time in my day-to-day.",
      by: "Brandon Lara &middot; 90-day check-in" },
    { quote: "Excellent. Exceeding expectations, for sure.",
      by: "Quinton Randel &middot; EIDLexit" }
  ];

  var m = document.getElementById('reviewMarquee');
  if(!m) return;
  var track = m.querySelector('.review-track');
  if(!track) return;

  function card(r, dupe){
    var d = document.createElement('div');
    d.className = 'review-card';
    if(dupe) d.setAttribute('aria-hidden','true');
    d.innerHTML = '<span class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>'
                + '<q>' + r.quote + '</q>'
                + '<span class="by">' + r.by + '</span>';
    return d;
  }
  /* The set runs twice so the loop meets itself with no gap. */
  REVIEWS.forEach(function(r){ track.appendChild(card(r, false)); });
  REVIEWS.forEach(function(r){ track.appendChild(card(r, true)); });

  /* Hold still until it is on screen, so a visitor always meets a full row. */
  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ m.classList.add('in-view'); io.unobserve(e.target); } });
    }, {threshold:0.2});
    io.observe(m);
  } else {
    m.classList.add('in-view');
  }
})();
