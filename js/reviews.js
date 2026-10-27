/* VRA client reviews, scrolling.

   One list, used by every lead-capture page, so a review edited here changes
   everywhere instead of drifting between hand-kept copies.

   Every line is a client's own words, lifted whole from the video transcript
   in watch/. scripts/check_quotes.py reads the `quote:` fields below and
   checks each one against its transcript, so an edit that rewords a client
   fails the build rather than going live. Leave the words alone.

   One review at a time. A row of moving text boxes gives a visitor nothing
   to settle on and competes with whatever the page is asking them to do.

   Markup a page needs:
     <div class="review-spot" id="reviewSpotlight" hidden aria-label="What clients say">
       <div class="review-stage"><span class="stars"></span><q></q><span class="by"></span></div>
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

  var STARS = '&#9733;&#9733;&#9733;&#9733;&#9733;';
  var spot = document.getElementById('reviewSpotlight');
  if(!spot) return;

  /* One at a time. Long enough on each to actually read it, and it stops
     whenever the visitor might be reading or is not looking: hover, keyboard
     focus, hidden tab. Reduced motion gets a single review and no cycling. */
  if(spot){
    var stage = spot.querySelector('.review-stage');
    var sq    = spot.querySelector('q');
    var sby   = spot.querySelector('.by');
    var sst   = spot.querySelector('.stars');
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    /* Always opens on the first review in the list, so the strongest line
       is the one every visitor sees; reorder the list to change it. */
    var i = 0, timer = null;

    function paint(){
      var r = REVIEWS[i];
      stage.classList.add('fading');
      setTimeout(function(){
        sst.innerHTML = STARS;
        sq.innerHTML  = r.quote;
        sby.innerHTML = r.by;
        stage.classList.remove('fading');
      }, reduce ? 0 : 220);
    }
    function play(){ if(!reduce && !timer) timer = setInterval(function(){ i=(i+1)%REVIEWS.length; paint(); }, 6500); }
    function stop(){ if(timer){ clearInterval(timer); timer = null; } }
    spot.addEventListener('mouseenter', stop);
    spot.addEventListener('mouseleave', play);
    spot.addEventListener('focusin', stop);
    spot.addEventListener('focusout', play);
    document.addEventListener('visibilitychange', function(){ document.hidden ? stop() : play(); });
    paint(); spot.hidden = false; play();
  }

})();
