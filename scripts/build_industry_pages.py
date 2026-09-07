#!/usr/bin/env python3
"""Generates the four industry-specific landing pages for vra.global.

Run from the repo root: python3 scripts/build_industry_pages.py
Regenerates each page from scratch based on the INDUSTRIES data below —
edit the data, don't hand-edit the generated HTML files' shared structure.
"""
import os

STYLE = """
  :root{
    --light-blue:#9ecfe7;
    --blue:#275ea3;
    --dark-blue:#010110;
    --darker-blue:#010110;
    --white:#e9edef;
    --black:#010110;
    --gray:#4b5354;
    --border:#cbe1ec;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Segoe UI',Helvetica,Arial,sans-serif;color:var(--black);background:var(--white);line-height:1.6;}
  a{text-decoration:none;color:inherit;}
  img{max-width:100%;display:block;}
  .wrap{max-width:1160px;margin:0 auto;padding:0 24px;}
  h1,h2,h3,h4{color:var(--darker-blue);font-weight:800;line-height:1.2;}
  section{padding:72px 0;}
  .btn{display:inline-block;padding:14px 30px;border-radius:8px;font-weight:700;font-size:15px;transition:all .2s ease;cursor:pointer;border:2px solid transparent;}
  .btn-primary{background:var(--dark-blue);color:var(--white);}
  .btn-primary:hover{background:var(--darker-blue);}
  .btn-outline{background:transparent;color:var(--dark-blue);border-color:var(--dark-blue);}
  .btn-outline:hover{background:var(--light-blue);}

  /* NAV */
  header{position:sticky;top:0;background:var(--white);border-bottom:1px solid var(--border);z-index:100;}
  nav.wrap{display:flex;align-items:center;justify-content:flex-start;padding:14px 24px;gap:16px 32px;max-width:none;width:100%;margin:0;flex-wrap:wrap;}
  .brand{display:flex;align-items:center;gap:10px;font-weight:800;color:var(--darker-blue);font-size:18px;letter-spacing:.3px;flex-shrink:0;}
  .brand img{height:42px;width:42px;object-fit:contain;}
  .navlinks{display:flex;gap:12px 20px;align-items:center;flex-wrap:wrap;}
  .navlinks a{font-size:13.5px;font-weight:600;color:var(--gray);white-space:nowrap;}
  .navlinks a:hover{color:var(--dark-blue);}
  .navlinks a.btn-primary{color:var(--white);font-weight:700;padding:10px 16px;font-size:13.5px;}
  .navlinks a.btn-primary:hover{color:var(--white);background:var(--darker-blue);}
  .navlinks a.active{color:var(--dark-blue);}
  @media(max-width:1150px){.navlinks{display:none;}}

  /* PAGE HERO */
  .page-hero{background:linear-gradient(135deg,var(--light-blue) 0%,var(--white) 100%);padding:64px 0 56px;text-align:center;}
  .page-hero .kicker{color:var(--blue);font-weight:800;font-size:13px;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;}
  .page-hero h1{font-size:38px;margin-bottom:14px;}
  .page-hero p{color:var(--gray);font-size:16px;max-width:640px;margin:0 auto 26px;}
  .page-hero .hero-ctas{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;}

  /* SECTION HEADS */
  .section-head{text-align:center;max-width:720px;margin:0 auto 48px;}
  .kicker{color:var(--blue);font-weight:800;font-size:13px;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;}
  .section-head h2{font-size:32px;margin-bottom:12px;}
  .section-head p{color:var(--gray);font-size:16px;}

  .alt-bg{background:linear-gradient(135deg,var(--light-blue) 0%,var(--white) 100%);}

  /* VALUE CARDS */
  .card-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;}
  .card{background:var(--white);border:1px solid var(--border);border-radius:14px;padding:28px 22px;text-align:left;}
  .card .icon{width:46px;height:46px;border-radius:10px;background:var(--light-blue);color:var(--blue);display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:16px;}
  .card h3{font-size:17px;margin-bottom:8px;}
  .card p{font-size:14px;color:var(--gray);}
  @media(max-width:900px){.card-grid{grid-template-columns:repeat(2,1fr);}}
  @media(max-width:560px){.card-grid{grid-template-columns:1fr;}}

  /* SERVICES */
  .service-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
  .service-card{background:var(--white);border:1px solid var(--border);border-radius:16px;padding:30px;}
  .service-card h3{font-size:19px;margin-bottom:14px;display:flex;align-items:center;gap:10px;}
  .service-card h3:before{content:"";width:8px;height:8px;background:var(--blue);border-radius:50%;}
  .service-card ul{list-style:none;display:flex;flex-direction:column;gap:9px;}
  .service-card ul li{font-size:14.5px;color:var(--gray);padding-left:22px;position:relative;}
  .service-card ul li:before{content:"—";position:absolute;left:0;color:var(--blue);}
  .service-card.wide{grid-column:1 / -1;}
  .service-card.wide ul{display:grid;grid-template-columns:1fr 1fr;gap:9px 24px;}
  @media(max-width:900px){.service-grid{grid-template-columns:1fr;}.service-card.wide ul{grid-template-columns:1fr;}}

  /* VIDEO TESTIMONIAL */
  .video-feature{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;}
  .video-card{display:block;border-radius:16px;overflow:hidden;box-shadow:0 8px 28px rgba(1,1,16,.14);}
  .video-thumb{position:relative;aspect-ratio:16/9;background:#000;}
  .video-thumb img{width:100%;height:100%;object-fit:cover;opacity:.88;}
  .video-play{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
  .video-play-btn{width:56px;height:56px;border-radius:50%;background:rgba(1,1,16,.75);display:flex;align-items:center;justify-content:center;}
  .testimonial-quote-lg{font-size:20px;font-weight:600;color:var(--darker-blue);line-height:1.5;margin-bottom:18px;}
  .testimonial-stars{color:#f5b400;font-size:16px;letter-spacing:2px;margin-bottom:10px;}
  .testimonial-name-lg{font-size:15px;font-weight:700;color:var(--darker-blue);}
  .testimonial-role-lg{font-size:14px;color:var(--gray);}
  @media(max-width:900px){.video-feature{grid-template-columns:1fr;}}

  /* PRICING */
  .pricing-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:24px;margin-bottom:28px;}
  .pricing-card{background:var(--white);border:2px solid var(--blue);border-radius:16px;padding:32px;}
  .pricing-card .price-tag{font-size:32px;font-weight:800;color:var(--darker-blue);margin-bottom:2px;}
  .pricing-card .price-tag span{font-size:15px;font-weight:600;color:var(--gray);}
  .pricing-card .price-sub{font-size:13.5px;color:var(--blue);font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:18px;}
  .pricing-card ul{list-style:none;display:flex;flex-direction:column;gap:9px;margin-bottom:18px;}
  .pricing-card ul li{font-size:14.5px;color:var(--gray);padding-left:22px;position:relative;}
  .pricing-card ul li:before{content:"—";position:absolute;left:0;color:var(--blue);}
  .pricing-card .price-best{font-size:13.5px;color:var(--gray);border-top:1px solid var(--border);padding-top:14px;}
  .pricing-note{background:var(--light-blue);border-radius:14px;padding:22px 26px;font-size:14.5px;color:var(--darker-blue);}
  .pricing-note strong{display:block;margin-bottom:4px;}
  @media(max-width:900px){.pricing-grid{grid-template-columns:1fr;}}

  /* OTHER INDUSTRIES */
  .industry-row{display:flex;gap:16px;flex-wrap:wrap;justify-content:center;}
  .industry-pill{background:var(--white);border:1px solid var(--border);border-radius:10px;padding:14px 22px;font-weight:700;font-size:14.5px;color:var(--dark-blue);}
  .industry-pill:hover{border-color:var(--blue);color:var(--blue);}

  /* CTA BANNER */
  .cta-banner{background:var(--dark-blue);border-radius:20px;padding:56px 40px;text-align:center;color:#fff;}
  .cta-banner h2{color:#fff;font-size:30px;margin-bottom:12px;}
  .cta-banner p{color:#cfe1f0;margin-bottom:26px;font-size:16px;}
  .cta-banner .btn-primary{background:#fff;color:var(--dark-blue);}
  .cta-banner .btn-primary:hover{background:var(--light-blue);}

  /* FOOTER */
  footer{background:var(--darker-blue);color:#fff;padding:56px 0 28px;}
  .footer-grid{display:grid;grid-template-columns:1.1fr 0.9fr 0.9fr 0.9fr 1fr;gap:24px;margin-bottom:36px;}
  .footer-subhead{margin-top:24px;}
  .footer-grid h4{color:#fff;font-size:15px;margin-bottom:16px;}
  .footer-grid p, .footer-grid a{font-size:14px;color:#fff;display:block;margin-bottom:10px;}
  .footer-grid a:hover{color:var(--light-blue);}
  .footer-bottom{border-top:1px solid rgba(255,255,255,.12);padding-top:22px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-size:13px;color:#fff;}
  .social-row{display:flex;gap:14px;flex-wrap:wrap;}
  @media(max-width:1100px){.footer-grid{grid-template-columns:1fr 1fr 1fr;}}
  @media(max-width:700px){.footer-grid{grid-template-columns:1fr 1fr;}}
  @media(max-width:480px){.footer-grid{grid-template-columns:1fr;}}
"""

NAV = """<header>
  <nav class="wrap">
    <a class="brand" href="index.html">
      <img src="brand/vra-logo.png" alt="VRA logo">
      VIRTUAL REALTY ASSISTANTS
    </a>
    <div class="navlinks">
      <a href="index.html#why">Why VRA</a>
      <a href="index.html#services">Services</a>
      <a href="pricing.html">Pricing</a>
      <a href="index.html#process">Hiring Process</a>
      <a href="index.html#assistants">Meet the Team</a>
      <a href="reviews.html">Reviews</a>
      <a href="faq.html">FAQ</a>
      <a href="insights.html">Insights</a>
      <a href="needs-assessment.html">Needs Assessment</a>
      <a href="contact.html">Contact</a>
      <a href="join-sales-team.html">Join Our Sales Team</a>
      <a href="https://www.vrealtyassistants.com/apply-now" target="_blank" rel="noopener">Apply as a VA</a>
      <a href="https://calendly.com/michael2582/virtual-realty-assistants-consultation-interview" target="_blank" rel="noopener" class="btn btn-primary">Schedule a Consult</a>
    </div>
    </nav>
</header>"""

FOOTER_TMPL = """<footer>
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h4>Virtual Realty Assistants</h4>
        <p>Exceptional assistants for exceptional businesses. Based out of Keller Williams Memorial, Houston, TX.</p>
        <h4 class="footer-subhead">Follow Us</h4>
        <div class="social-row">
          <a href="https://www.instagram.com/virtualrealtyassistants" target="_blank" rel="noopener">Instagram</a>
          <a href="https://www.tiktok.com/@virtualrealtyassistants" target="_blank" rel="noopener">TikTok</a>
          <a href="https://www.youtube.com/channel/UCjbtac-Lrr86WJzb6PcUq2w" target="_blank" rel="noopener">YouTube</a>
          <a href="https://www.linkedin.com/company/virtualrealtyassistants/" target="_blank" rel="noopener">LinkedIn</a>
        </div>
      </div>
      <div>
        <h4>Company</h4>
        <a href="index.html#why">Why VRA</a>
        <a href="index.html#services">Services</a>
        <a href="pricing.html">Pricing</a>
        <a href="index.html#process">Hiring Process</a>
        <a href="index.html#assistants">Meet the Team</a>
      </div>
      <div>
        <h4>Resources</h4>
        <a href="reviews.html">Reviews</a>
        <a href="faq.html">FAQ</a>
        <a href="insights.html">Insights</a>
        <a href="needs-assessment.html">Needs Assessment</a>
        <a href="contact.html">Contact</a>
      </div>
      <div>
        <h4>Industries</h4>
{industry_links}
      </div>
      <div>
        <h4>Get in Touch</h4>
        <a href="mailto:contact@vrealtyassistants.com" target="_blank" rel="noopener">contact@vrealtyassistants.com</a>
        <a href="tel:1-281-612-9678" target="_blank" rel="noopener">(281) 612-9678</a>
        <a href="https://www.vrealtyassistants.com/privacy-policy" target="_blank" rel="noopener">Privacy Policy</a>
        <h4 class="footer-subhead">Careers</h4>
        <a href="https://www.vrealtyassistants.com/apply-now" target="_blank" rel="noopener">Apply as a VA</a>
        <a href="join-sales-team.html">Join Our Sales Team</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2025 Virtual Realty Assistants &mdash; All Rights Reserved</span>
    </div>
  </div>
</footer>"""

PRICING_SECTION = """<!-- PRICING -->
<section id="pricing">
  <div class="wrap">
    <div class="section-head" style="max-width:900px;">
      <div class="kicker">Pricing at a Glance</div>
      <h2>Transparent, Flat-Rate Pricing</h2>
      <p>No matter your industry or the skills your VA specializes in, pricing doesn't change &mdash; no tiers, no upcharges, just one flat rate for dedicated hours, not a per-task menu.</p>
    </div>
    <div class="pricing-grid">
      <div class="pricing-card">
        <div class="price-tag">$1,500<span>/month</span></div>
        <div class="price-sub">Full-Time VA</div>
        <ul>
          <li>40 hours/week</li>
          <li>1-year agreement</li>
          <li>Invoiced on the 20th of each month</li>
        </ul>
        <div class="price-best">Best for: ongoing admin, CRM management, full inbox/calendar ownership, or any business that needs a consistent full-day presence.</div>
      </div>
      <div class="pricing-card">
        <div class="price-tag">$800<span>/month</span></div>
        <div class="price-sub">Part-Time VA</div>
        <ul>
          <li>20 hours/week</li>
          <li>6-month agreement</li>
          <li>Invoiced on the 20th of each month</li>
        </ul>
        <div class="price-best">Best for: easing into delegation, seasonal support, or lighter task loads.</div>
      </div>
    </div>
    <div class="pricing-note">
      <strong>Part-time and full-time both include:</strong>
      Your VA's full dedicated time, hands-on matching &amp; onboarding to get you paired with the right person from day one, and ongoing VRA support with check-ins at 14/30/60/90 days &mdash; no hidden fees, ever. If your VA is not the right fit, you can swap in a different VA at any point, at no extra cost.
    </div>
  </div>
</section>"""

INDUSTRIES = [
    {
        "slug": "real-estate-virtual-assistant",
        "nav_label": "Real Estate",
        "page_title": "Real Estate Virtual Assistant Services",
        "meta_description": "Hire a virtual assistant trained specifically for real estate agents and teams — transaction coordination, MLS and CRM management, listing docs, and buyer/seller updates. Flat-rate pricing, no long trial periods.",
        "kicker": "Virtual Assistants for Real Estate",
        "h1": "The Virtual Assistant Built for Real Estate Agents &amp; Teams",
        "hero_p": "Between new leads, active contracts, listing paperwork, and a CRM that never stops pinging, most agents spend as much time on admin as they do selling. A VRA real estate virtual assistant is trained specifically to take that off your plate — from transaction coordination to CRM upkeep — so you can spend your time with clients, not spreadsheets.",
        "why_card1": "Only the top 1% of applicants make it through our screening and mandatory 28-day training program — covering real estate database management, contract writing, and e-signature workflows in dotloop and DocuSign — before they ever touch client work. Every VA trains hands-on in KW Command, and because mastering one database means picking up any other quickly, we commit to having them fluent in whatever CRM you use within 5 days of hire.",
        "service_intro": "Every VRA real estate VA is trained on the day-to-day of running a book of business — not just general admin.",
        "service_bullets": [
            "Pre-listing document prep and coordination",
            "Buyer and seller update calls/emails",
            "Full transaction coordination from contract to close",
            "CRM and database management (KW Command and others)",
            "Open house preparation, promotion &amp; scheduling",
            "MLS listing updates and photo/document uploads",
        ],
        "video": {
            "name": "Kaylee Fisher",
            "role": "REALTOR&reg; | Keller Williams Elite",
            "quote": "For the first time in months, I have been able to cook dinner for my family. I have been able to go to some of my son's baseball practices.",
            "youtube_id": "jxetrEtOE8U",
            "duration": "PT2M3S",
        },
        "second_video": {
            "name": "Emily Zakhem",
            "role": "REALTOR&reg; | Keller Williams Memorial | Top 20% | Luxury Agent",
            "quote": "I cannot think of running my business without a virtual assistant.",
            "youtube_id": "kKX-915tQVA",
            "duration": None,
        },
        "service_type": "Real Estate Virtual Assistant Services",
        "service_description": "Virtual assistants trained specifically for real estate agents and teams — transaction coordination, MLS and CRM management, listing document prep, and buyer/seller communication.",
    },
    {
        "slug": "title-escrow-virtual-assistant",
        "nav_label": "Title &amp; Escrow",
        "page_title": "Virtual Assistant for Title &amp; Escrow Companies",
        "meta_description": "Hire a virtual assistant trained for title and escrow work in Qualia — closing coordination, document prep, and client updates. Flat-rate pricing, hands-on matching, no long trial periods.",
        "kicker": "Virtual Assistants for Title &amp; Escrow",
        "h1": "The Virtual Assistant Built for Title &amp; Escrow Professionals",
        "hero_p": "Closings don't wait, and neither does the paperwork behind them. A VRA virtual assistant trained for title and escrow work keeps closing files organized, documents moving, and clients updated — so your team can focus on getting deals to the table on time.",
        "why_card1": "Only the top 1% of applicants make it through our screening and mandatory 28-day training program — covering Qualia, e-signature workflows in dotloop and DocuSign, and closing-file organization — before they ever touch client work. Because mastering one industry workflow means picking up another quickly, we commit to having every VA fluent in whatever title production software or CRM you use within 5 days of hire.",
        "service_intro": "Every VRA title &amp; escrow VA is trained on the day-to-day of a closing file — not just general admin.",
        "service_bullets": [
            "Closing coordination and scheduling",
            "Document preparation and organization in Qualia",
            "Hyperlinking title commitments for easy reference",
            "File auditing and quality-control checks",
            "Client and agent update calls/emails",
            "CRM and file-tracking database management",
            "Invoicing and closing statement support",
            "Custom workflows tailored to your title production software",
        ],
        "video": {
            "name": "Elle Haynes",
            "role": "Texas Title &amp; Escrow Consultant | New Century Title &amp; Escrow",
            "quote": "Instead of this entry-level assistant that I thought I was getting, I got a game changer.",
            "youtube_id": "9j_BsGEmU4U",
            "duration": None,
        },
        "second_video": {
            "name": "Debbie Yates",
            "role": "President | Key Title Group",
            "quote": "I wasn't sure how it was going to work out in the beginning, but she's taken direction really well. She's a self-starter, finding things we didn't even expect her to find.",
            "youtube_id": "sL5ETpuB8Tg",
            "duration": None,
        },
        "service_type": "Virtual Assistant Services for Title &amp; Escrow",
        "service_description": "Virtual assistants trained for title and escrow work — closing coordination, document preparation, and client updates.",
    },
    {
        "slug": "mortgage-virtual-assistant",
        "nav_label": "Mortgage &amp; Lending",
        "page_title": "Virtual Assistant for Mortgage &amp; Lending",
        "meta_description": "Hire a virtual assistant trained for mortgage and lending work — loan file organization in Encompass, borrower communication, and appointment scheduling. Flat-rate pricing, no long trial periods.",
        "kicker": "Virtual Assistants for Mortgage &amp; Lending",
        "h1": "The Virtual Assistant Built for Mortgage &amp; Lending Professionals",
        "hero_p": "Between loan files, borrower calls, and appointment scheduling, busy season can bury a lending team in admin. A VRA virtual assistant trained for mortgage and lending work keeps files organized and borrowers in the loop — so nothing falls through the cracks when volume picks up.",
        "why_card1": "Only the top 1% of applicants make it through our screening and mandatory 28-day training program — covering document preparation, e-signature workflows in dotloop and DocuSign, and file organization — before they ever touch client work. Every mortgage VA also completes our certified Encompass training track, covering compliance and the full loan lifecycle, so they're fluent in the industry's leading LOS from day one.",
        "service_intro": "Every VRA mortgage &amp; lending VA is trained on the day-to-day of a loan file — not just general admin.",
        "service_bullets": [
            "Loan file organization and document tracking in Encompass",
            "Borrower communication and follow-up",
            "Appointment scheduling and calendar management",
            "CRM and pipeline database management",
            "Invoicing and reporting support",
            "Certified training in Encompass compliance and loan lifecycle management",
            "Custom workflows tailored to your loan origination system",
        ],
        "video": {
            "name": "James Del Bosque",
            "role": "GFS Home Loans",
            "quote": "When we get busy, a lot of things seem to fall between the cracks. Laurenz has been very helpful in keeping on top of those things.",
            "youtube_id": "QOPZY8aWNNY",
            "duration": None,
        },
        "second_video": {
            "name": "Erica Lopez",
            "role": "High Point Mortgage",
            "quote": "Kate is phenomenal — quick, eager, and she does everything we ask her to do efficiently. I'd rate her a 10 out of 10.",
            "youtube_id": "_eQJNl00gK4",
            "duration": None,
        },
        "third_video": {
            "name": "Ronalyn Barut",
            "role": "GFS Home Loans",
            "quote": "She's a great asset to my marketing team, and that helps the entire team and company. I'd definitely suggest other institutions look into hiring a VA.",
            "youtube_id": "_woVVc-XaOg",
            "duration": None,
        },
        "service_type": "Virtual Assistant Services for Mortgage &amp; Lending",
        "service_description": "Virtual assistants trained for mortgage and lending work — loan file organization, borrower communication, and appointment scheduling.",
    },
    {
        "slug": "restaurant-virtual-assistant",
        "nav_label": "Restaurants",
        "page_title": "Virtual Assistant for Restaurants",
        "meta_description": "Hire a virtual assistant trained for restaurant operations — reservations, vendor coordination, online ordering, and menu updates. Flat-rate pricing, no long trial periods.",
        "kicker": "Virtual Assistants for Restaurants",
        "h1": "The Virtual Assistant Built for Restaurant Owners",
        "hero_p": "Running a restaurant means the phone never stops and the to-do list never ends — reservations, vendor calls, online listings, menu changes. A VRA virtual assistant trained for restaurant operations handles the behind-the-scenes admin so you can stay focused on the floor and the kitchen.",
        "why_card1": "Only the top 1% of applicants make it through our screening and mandatory 28-day training program — covering scheduling systems, vendor coordination, and online ordering/reservation platforms — before they ever touch client work. Because mastering one industry workflow means picking up another quickly, we commit to having every VA fluent in whatever reservation or POS system you use within 5 days of hire.",
        "service_intro": "Every VRA restaurant VA is trained on the day-to-day of running a restaurant's front-of-house admin — not just general tasks.",
        "service_bullets": [
            "Reservation management and confirmations",
            "Vendor coordination and ordering",
            "Online ordering platform updates",
            "Menu updates across delivery apps and your website",
            "Customer review monitoring and responses",
            "Invoicing and vendor list management",
        ],
        "video": {
            "name": "Rayan Saleh",
            "role": "Owner | The Butcher's Grille",
            "quote": "I don't know how I made it this long without even having a VA.",
            "youtube_id": "rJZMNtqjTz8",
            "duration": "PT52S",
        },
        "second_video": None,
        "service_type": "Virtual Assistant Services for Restaurants",
        "service_description": "Virtual assistants trained for restaurant operations — reservations, vendor coordination, online ordering, and menu updates.",
    },
    {
        "slug": "small-business-virtual-assistant",
        "nav_label": "Small Business",
        "page_title": "Virtual Assistant for Small Businesses",
        "meta_description": "Hire a virtual assistant trained for small business owners and consultants — client communication, scheduling, reporting, and day-to-day admin. Flat-rate pricing, no long trial periods.",
        "kicker": "Virtual Assistants for Small Business",
        "h1": "The Virtual Assistant Built for Small Business Owners",
        "hero_p": "Running a small business means wearing every hat — client calls, scheduling, invoicing, follow-up — often with no one else to hand it to. A VRA virtual assistant is trained to take the day-to-day admin off your plate so you can spend your time on the work that actually grows your business.",
        "why_card1": "Only the top 1% of applicants make it through our screening and mandatory 28-day training program — covering client communication, scheduling systems, and general business admin — before they ever touch client work. Because mastering one workflow means picking up another quickly, we commit to having every VA fluent in whatever CRM, scheduling, or project tools you use within 5 days of hire.",
        "service_intro": "Every VRA small business VA is trained to run point on the admin that keeps a growing business moving — not just generic tasks.",
        "service_bullets": [
            "Client communication and follow-up",
            "Scheduling and calendar management",
            "Invoicing and reporting support",
            "CRM and database management",
            "Vendor and client onboarding",
            "Custom workflows tailored to your business",
        ],
        "video": {
            "name": "Austin Galvez",
            "role": "CPA",
            "quote": "He's been fantastic — things that used to fall through the cracks no longer do, and he keeps me honest on everything I have going on.",
            "youtube_id": "ri45R6VEWCI",
            "duration": None,
        },
        "second_video": {
            "name": "Quinton Randel",
            "role": "Co-Founder &amp; EVP, Operations and Technology | EidleExit",
            "quote": "I have no reservations about them communicating with clients with minimal to no oversight.",
            "youtube_id": "jcVkz2-Ms4Y",
            "duration": None,
        },
        "service_type": "Virtual Assistant Services for Small Business",
        "service_description": "Virtual assistants trained for small business owners and consultants — client communication, scheduling, reporting, and day-to-day admin support.",
    },
    {
        "slug": "keller-williams-virtual-assistant",
        "nav_label": "KW Leadership",
        "page_title": "Virtual Assistant for Keller Williams Market Center Leadership",
        "meta_description": "Hire a virtual assistant trained for Keller Williams market center back-office operations — CDA processing, accounts receivable, agent billing, and KW Command. Flat-rate pricing, no long trial periods.",
        "kicker": "Virtual Assistants for KW Market Center Leadership",
        "h1": "The Virtual Assistant Built for Keller Williams Market Center Leadership",
        "hero_p": "Running a market center means keeping hundreds of agents' commissions, billing, and receivables moving — plus the marketing that keeps the office visible — often with a lean staff. A VRA virtual assistant trained for market center operations takes accounting and marketing tasks off your plate so your MCA and staff can focus on agents, not spreadsheets.",
        "why_card1": "Only the top 1% of applicants make it through our screening and mandatory 28-day training program — covering KW Command, Commission Disbursement Authorizations (CDAs), accounts receivable follow-up, and market center marketing support — before they ever touch office work. Every VA is backed by a $1 million Errors &amp; Omissions insurance policy, and because mastering one market center's workflow means picking up another quickly, we commit to having them fluent in your office's systems within 5 days of hire.",
        "service_intro": "VRA virtual assistants already support Keller Williams Memorial and Keller Williams Heritage in San Antonio — handling accounting, marketing, and special projects, trained on the day-to-day of running MC back-office operations, not just general admin.",
        "service_bullets": [
            "Commission Disbursement Authorization (CDA) processing",
            "Accounts receivable outreach and collections follow-up",
            "Agent billing and invoicing support",
            "KW Command database management",
            "Professional, agent-facing communication on your MC's behalf",
            "Market center marketing support — social graphics, flyers, and agent communications",
            "Social media scheduling and content coordination",
            "Custom workflows tailored to your market center's systems",
        ],
        "video": {
            "name": "Victoria Williams",
            "role": "Market Center Administrator | Keller Williams Memorial",
            "quote": "He handles all of our CDAs — this month we've had over 400 — and he reaches out to 60 to 75-plus people a month for accounts receivable. It's been great to have that leverage.",
            "youtube_id": "SzLDWizkKMc",
            "duration": None,
        },
        "second_video": {
            "name": "Hannah DuBose",
            "role": "Marketing Team | Keller Williams Heritage",
            "quote": "She's been way more self-sufficient than I could have ever asked for. After learning our brand and processes, she took the tasks I gave her and really ran with it.",
            "youtube_id": "EmsjM5hEGeg",
            "duration": None,
        },
        "service_type": "Virtual Assistant Services for Keller Williams Market Center Leadership",
        "service_description": "Virtual assistants trained for Keller Williams market center back-office operations — CDA processing, accounts receivable, agent billing, and KW Command database management.",
    },
]

# Not an "industry" — a cross-cutting task/specialty deep-dive page, linked from the
# Virtual Assistant Tasks section on the homepage rather than listed among Industries.
TASK_PAGES = [
    {
        "slug": "digital-marketing-virtual-assistant",
        "nav_label": "Digital Marketing",
        "page_title": "Virtual Assistant for Digital Marketing",
        "meta_description": "Hire a virtual assistant trained in digital marketing — social media management, content creation, paid ads, and email marketing. Flat-rate pricing, hands-on matching, no long trial periods.",
        "kicker": "Virtual Assistants for Digital Marketing",
        "h1": "The Virtual Assistant Built for Digital Marketing",
        "hero_p": "Consistent content, active social channels, and campaigns that actually get reported on — marketing is the first thing to slip when a team gets busy. A VRA virtual assistant trained in digital marketing keeps your channels active and your campaigns moving, so your brand stays visible without eating up your week.",
        "why_card1": "Every VRA digital marketing VA completes certified training in paid ads and marketing analytics, SEO and content marketing, social media marketing and brand awareness, and social selling — plus hands-on graphic design in Canva — before they ever touch client work. Because mastering one platform means picking up another quickly, we commit to having your VA fluent in whatever marketing tools and channels you use within 5 days of hire.",
        "service_intro": "Every VRA digital marketing VA is trained to run the day-to-day of a marketing calendar — not just general admin.",
        "service_bullets": [
            "Social media content creation and scheduling",
            "Graphic design in Canva for social posts, flyers, and ads",
            "Paid ad campaign support (PPC, social ads) and reporting",
            "Email marketing campaign creation and scheduling",
            "SEO and content marketing support",
            "Marketing analytics and performance reporting",
            "Social selling and LinkedIn prospecting support",
            "Custom workflows tailored to your marketing stack",
        ],
        "video": {
            "name": "Hannah DuBose",
            "role": "Marketing Team | Keller Williams Heritage",
            "quote": "She's been way more self-sufficient than I could have ever asked for. After learning our brand and processes, she took the tasks I gave her and really ran with it.",
            "youtube_id": "EmsjM5hEGeg",
            "duration": None,
        },
        "service_type": "Virtual Assistant Services for Digital Marketing",
        "service_description": "Virtual assistants trained in digital marketing — social media management, content creation, paid ads, and email marketing.",
    },
]


def initials(name):
    return "".join(w[0] for w in name.split()[:2]).upper()


def video_block(v, canonical_name_for_second=False):
    dur = f',\n      "duration": "{v["duration"]}"' if v["duration"] else ""
    return f"""  {{
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": "{v['name']} — Virtual Realty Assistants Testimonial",
    "description": "{v['name']}, {v['role'].replace('&reg;', '').replace('&amp;', 'and')}, on working with a Virtual Realty Assistants (VRA) virtual assistant: “{v['quote']}”",
    "thumbnailUrl": ["https://i.ytimg.com/vi/{v['youtube_id']}/maxresdefault.jpg"],
    "contentUrl": "https://www.youtube.com/watch?v={v['youtube_id']}",
    "embedUrl": "https://www.youtube.com/embed/{v['youtube_id']}",
    "publisher": {{
      "@type": "Organization",
      "name": "Virtual Realty Assistants",
      "logo": {{"@type": "ImageObject", "url": "https://vra.global/brand/vra-logo.png"}}
    }}{dur}
  }}"""


def build_page(data, all_industries):
    slug = data["slug"]
    url = f"https://vra.global/{slug}"
    plain_title = data['page_title'].replace('&amp;', '&')
    title_tag = f"{plain_title} | Virtual Realty Assistants"

    extra_videos = [v for v in (data.get("second_video"), data.get("third_video")) if v]

    video_objects = [video_block(data["video"])]
    for v in extra_videos:
        video_objects.append(video_block(v))
    video_schema = ",\n".join(video_objects)

    service_bullets_html = "\n".join(f"          <li>{b}</li>" for b in data["service_bullets"])

    other_industries = [i for i in all_industries if i["slug"] != slug]
    industry_pills = "\n".join(
        f'      <a class="industry-pill" href="{i["slug"]}.html">{i["nav_label"]}</a>'
        for i in other_industries
    )
    footer_industry_links = "\n".join(
        f'        <a href="{i["slug"]}.html">{i["nav_label"]}</a>' for i in all_industries
    )

    def video_feature(v, video_id_for_link):
        return f"""    <div class="video-card-wrap">
        <a class="video-card" href="https://www.youtube.com/watch?v={v['youtube_id']}" target="_blank" rel="noopener">
          <div class="video-thumb">
            <img src="https://i.ytimg.com/vi/{v['youtube_id']}/maxresdefault.jpg" alt="{v['name']} testimonial">
            <div class="video-play"><div class="video-play-btn"><svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg></div></div>
          </div>
        </a>
      </div>"""

    def extra_video_block(v):
        return f"""
    <div class="video-feature" style="margin-top:32px;">
{video_feature(v, v['youtube_id'])}
      <div>
        <div class="testimonial-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <p class="testimonial-quote-lg">&ldquo;{v['quote']}&rdquo;</p>
        <div class="testimonial-name-lg">{v['name']}</div>
        <div class="testimonial-role-lg">{v['role']}</div>
      </div>
    </div>"""

    second_video_html = "".join(extra_video_block(v) for v in extra_videos)

    v1 = data["video"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#275ea3">
<title>{title_tag}</title>
<meta name="description" content="{data['meta_description']}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Virtual Realty Assistants">
<meta property="og:title" content="{title_tag}">
<meta property="og:description" content="{data['meta_description']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://vra.global/photos/hero-globe.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_tag}">
<meta name="twitter:description" content="{data['meta_description']}">
<meta name="twitter:image" content="https://vra.global/photos/hero-globe.png">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://vra.global/"}},
    {{"@type": "ListItem", "position": 2, "name": "{plain_title}", "item": "{url}"}}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "{data['service_type']}",
  "serviceType": "{data['service_type']}",
  "provider": {{
    "@type": "ProfessionalService",
    "name": "Virtual Realty Assistants",
    "url": "https://vra.global/"
  }},
  "areaServed": "US",
  "description": "{data['service_description']}",
  "hasOfferCatalog": {{
    "@type": "OfferCatalog",
    "name": "Virtual Assistant Plans",
    "itemListElement": [
      {{
        "@type": "Offer",
        "name": "Full-Time Virtual Assistant",
        "description": "40 hours/week, 1-year agreement, invoiced on the 20th of each month.",
        "priceSpecification": {{"@type": "UnitPriceSpecification", "price": "1500", "priceCurrency": "USD", "unitText": "MONTH"}}
      }},
      {{
        "@type": "Offer",
        "name": "Part-Time Virtual Assistant",
        "description": "20 hours/week, 6-month agreement, invoiced on the 20th of each month.",
        "priceSpecification": {{"@type": "UnitPriceSpecification", "price": "800", "priceCurrency": "USD", "unitText": "MONTH"}}
      }}
    ]
  }}
}}
</script>
<script type="application/ld+json">
[
{video_schema}
]
</script>
<style>
{STYLE}
</style>
</head>
<body>

{NAV}

<!-- PAGE HERO -->
<section class="page-hero">
  <div class="wrap">
    <div class="kicker">{data['kicker']}</div>
    <h1>{data['h1']}</h1>
    <p>{data['hero_p']}</p>
    <div class="hero-ctas">
      <a href="https://calendly.com/michael2582/virtual-realty-assistants-consultation-interview" target="_blank" rel="noopener" class="btn btn-primary">Schedule a Consult</a>
      <a href="needs-assessment.html" class="btn btn-outline">Take Our Needs Assessment</a>
    </div>
  </div>
</section>

<!-- WHY VRA -->
<section id="why">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Why VRA</div>
      <h2>The Best Virtual Assistant for Your Business</h2>
      <p>VRA was founded to give business owners the best virtual assistance available &mdash; with a hassle-free process from search to onboarding.</p>
    </div>
    <div class="card-grid">
      <div class="card">
        <div class="icon">&#10003;</div>
        <h3>We Find the Best of the Best</h3>
        <p>{data['why_card1']}</p>
      </div>
      <div class="card">
        <div class="icon">&#10003;</div>
        <h3>Dedicated Matching</h3>
        <p>Matching starts with your free Needs Assessment &mdash; a two-minute breakdown of where you actually need help. From there, every VA is screened with a DISC Assessment and a Keller Personality Assessment for fit and fast-learning ability.</p>
      </div>
      <div class="card">
        <div class="icon">&#10003;</div>
        <h3>Business Support</h3>
        <p>Support continues after your VA starts, with check-ins at 14, 30, 60, and 90 days. If the fit still isn't right, swap in a different VA at any point, at no extra cost &mdash; no trial window, no fine print.</p>
      </div>
      <div class="card">
        <div class="icon">&#10003;</div>
        <h3>Built Differently</h3>
        <p>Most VA agencies lock you into tiered pricing, time-boxed trial guarantees, or a generic assistant with no industry training. VRA doesn't &mdash; backed by a $1 million Errors &amp; Omissions insurance policy for added peace of mind.</p>
      </div>
    </div>
  </div>
</section>

<!-- SERVICES -->
<section id="services" class="alt-bg">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">What Your VA Can Do</div>
      <h2>{data['service_type']}</h2>
      <p>{data['service_intro']}</p>
    </div>
    <div class="service-grid">
      <div class="service-card wide">
        <h3>Industry-Specific Support</h3>
        <ul>
{service_bullets_html}
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- VIDEO TESTIMONIAL -->
<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Hear From a Client</div>
      <h2>Real Results, In Their Own Words</h2>
    </div>
    <div class="video-feature">
{video_feature(v1, v1['youtube_id'])}
      <div>
        <div class="testimonial-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <p class="testimonial-quote-lg">&ldquo;{v1['quote']}&rdquo;</p>
        <div class="testimonial-name-lg">{v1['name']}</div>
        <div class="testimonial-role-lg">{v1['role']}</div>
      </div>
    </div>{second_video_html}
  </div>
</section>

{PRICING_SECTION}

<!-- OTHER INDUSTRIES -->
<section class="alt-bg">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Every Industry</div>
      <h2>We Also Support</h2>
      <p>VRA trains virtual assistants across industries &mdash; explore what a VA looks like for your line of work.</p>
    </div>
    <div class="industry-row">
{industry_pills}
    </div>
  </div>
</section>

<!-- CTA BANNER -->
<section>
  <div class="wrap">
    <div class="cta-banner">
      <h2>Ready to Get Your Time Back?</h2>
      <p>Schedule a free consultation and we'll walk you through the process, answer your questions, and get you matched with the right Virtual Assistant.</p>
      <a href="https://calendly.com/michael2582/virtual-realty-assistants-consultation-interview" target="_blank" rel="noopener" class="btn btn-primary">Schedule a Consult</a>
    </div>
  </div>
</section>

{FOOTER_TMPL.format(industry_links=footer_industry_links)}

</body>
</html>
"""
    return html


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for data in INDUSTRIES:
        html = build_page(data, INDUSTRIES)
        out_path = os.path.join(repo_root, f"{data['slug']}.html")
        with open(out_path, "w") as f:
            f.write(html)
        print(f"wrote {out_path}")
    # Task/specialty deep-dive pages: not industries, so pills/footer are built
    # against the real INDUSTRIES list (the page itself isn't added to it).
    for data in TASK_PAGES:
        html = build_page(data, INDUSTRIES)
        out_path = os.path.join(repo_root, f"{data['slug']}.html")
        with open(out_path, "w") as f:
            f.write(html)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
