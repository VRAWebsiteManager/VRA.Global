import io

fname = "digital-marketing-virtual-assistant.html"

edits = [
    (
        "<p>Every VRA digital marketing VA completes certified training in paid ads and marketing analytics, SEO and content marketing, social media marketing and brand awareness, and social selling — plus hands-on graphic design in Canva — before they ever touch client work. Because mastering one platform means picking up another quickly, we commit to having your VA fluent in whatever marketing tools and channels you use within 5 days of hire.</p>",
        "<p>Every VRA digital marketing VA completes our full Marketing Track — Content &amp; SEO, Paid Ads &amp; Analytics, and Social &amp; Selling — plus hands-on graphic design in Canva — before they ever touch client work. Training runs through real, verifiable certifications from providers like HubSpot, Google, and Semrush, not just internal coursework, so the credentials your VA earns are ones you can check yourself. Because mastering one platform means picking up another quickly, we commit to having your VA fluent in whatever marketing tools and channels you use within 5 days of hire.</p>",
    ),
    (
        """    <div class="service-grid">
      <div class="service-card wide">
        <h3>Industry-Specific Support</h3>
        <ul>
          <li>Social media content creation and scheduling</li>
          <li>Video content production &mdash; scripting, filming &amp; short-form editing (reels, ads, walkthroughs)</li>
          <li>Graphic design in Canva for social posts, flyers, and ads</li>
          <li>Paid ad campaign support (PPC, social ads) and reporting</li>
          <li>Email marketing campaign creation and scheduling</li>
          <li>SEO and content marketing support</li>
          <li>Marketing analytics and performance reporting</li>
          <li>Social selling and LinkedIn prospecting support</li>
          <li>Custom workflows tailored to your marketing stack</li>
        </ul>
      </div>
    </div>""",
        """    <div class="service-grid">
      <div class="service-card">
        <h3>Content &amp; SEO</h3>
        <ul>
          <li>SEO and content marketing support</li>
          <li>Graphic design in Canva for social posts, flyers, and ads</li>
          <li>Email marketing campaign creation and scheduling</li>
        </ul>
      </div>
      <div class="service-card">
        <h3>Paid Ads &amp; Analytics</h3>
        <ul>
          <li>Paid ad campaign support (PPC, social ads) and reporting</li>
          <li>Marketing analytics and performance reporting</li>
        </ul>
      </div>
      <div class="service-card wide">
        <h3>Social &amp; Selling</h3>
        <ul>
          <li>Social media content creation and scheduling</li>
          <li>Video content production &mdash; scripting, filming &amp; short-form editing (reels, ads, walkthroughs)</li>
          <li>Social selling and LinkedIn prospecting support</li>
        </ul>
      </div>
    </div>
    <p class="trust-closing">Every VA's workflow is customized to your existing marketing stack and tools.</p>""",
    ),
]

with io.open(fname, "r", encoding="utf-8") as f:
    content = f.read()

for old, new in edits:
    count = content.count(old)
    if count != 1:
        print(f"MISMATCH ({count} occurrences) for block starting: {old[:60]!r}")
        continue
    content = content.replace(old, new, 1)
    print("OK:", old[:60].replace("\n", " "))

with io.open(fname, "w", encoding="utf-8") as f:
    f.write(content)

print("DONE")
