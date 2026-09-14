import io

edits = {
    "real-estate-virtual-assistant.html": (
        "Only the top 1% of applicants make it through our screening and mandatory 4-week training program — covering real estate database management, contract writing, and e-signature workflows in dotloop and DocuSign — before they ever touch client work. Because mastering one database means picking up any other quickly, we commit to having them fluent in whatever CRM you use within 5 days of hire.",
        "Every real estate virtual assistant we place has already made it through our screening and a mandatory 4-week training program — covering real estate database management, contract writing, and e-signature workflows in dotloop and DocuSign — before ever touching client work. VAs supporting transaction coordination can also complete our Texas Contract Law certification (and Florida Contract Law, for agents closing deals there too) — in-depth training on earnest money, option periods, disclosure timelines, and the closing-document checklist, so your VA already speaks the language of your contracts. Because mastering one database means picking up any other quickly, we commit to having them fluent in whatever CRM you use within 5 days of hire.",
    ),
    "title-escrow-virtual-assistant.html": (
        "Only the top 1% of applicants make it through our screening and mandatory 4-week training program — covering Qualia, e-signature workflows in dotloop and DocuSign, and closing-file organization — before they ever touch client work. Because mastering one industry workflow means picking up another quickly, we commit to having every VA fluent in whatever title production software or CRM you use within 5 days of hire.",
        "Every title and escrow virtual assistant we place has cleared our screening and a mandatory 4-week training program — covering Qualia, e-signature workflows in dotloop and DocuSign, and closing-file organization — before ever touching client work. VAs supporting title and escrow teams also receive instruction in Texas Contract Law — covering exactly what a transaction coordinator should verify before a file reaches your team — so the handoff into your office is clean from day one. Because mastering one industry workflow means picking up another quickly, we commit to having every VA fluent in whatever title production software or CRM you use within 5 days of hire.",
    ),
    "mortgage-virtual-assistant.html": (
        "Only the top 1% of applicants make it through our screening and mandatory 4-week training program — covering document preparation, e-signature workflows in dotloop and DocuSign, calendar and CRM management, and marketing support — before they ever touch client work. Because loan file data involves sensitive borrower information like Social Security numbers, VRA VAs handle the administrative and marketing side of your office rather than working inside your LOS — so you get real leverage without the compliance risk.",
        "Every mortgage virtual assistant we place has cleared our screening and a mandatory 4-week training program — covering document preparation, e-signature workflows in dotloop and DocuSign, calendar and CRM management, and marketing support — before ever touching client work. VAs matched to mortgage and lending clients can also complete our Mortgage & Lending Specialist certification — a structured, four-module program covering the loan lifecycle, compliance boundaries for unlicensed staff, CRM-based borrower nurture campaigns, and referral marketing — ending in a verifiable certification badge. Because loan file data involves sensitive borrower information like Social Security numbers, VRA VAs handle the administrative and marketing side of your office rather than working inside your LOS — so you get real leverage without the compliance risk.",
    ),
    "restaurant-virtual-assistant.html": (
        "Only the top 1% of applicants make it through our screening and mandatory 4-week training program — covering scheduling systems, vendor coordination, and online ordering/reservation platforms — before they ever touch client work. Because mastering one industry workflow means picking up another quickly, we commit to having every VA fluent in whatever reservation or POS system you use within 5 days of hire.",
        "Every restaurant virtual assistant we place has made it through our screening and a mandatory 4-week training program — covering scheduling systems and vendor coordination — before ever touching client work. Restaurant clients also lean heavily on social media and promotion, so VAs matched to restaurants can add our Social & Selling marketing certification — covering social content creation, short-form video, and brand voice — giving you a true generalist who can run your online presence alongside the day-to-day. Because mastering one industry workflow means picking up another quickly, we commit to having every VA fluent in whatever reservation or POS system you use within 5 days of hire.",
    ),
    "small-business-virtual-assistant.html": (
        "Only the top 1% of applicants make it through our screening and mandatory 4-week training program — covering client communication, scheduling systems, and general business admin — before they ever touch client work. Because mastering one workflow means picking up another quickly, we commit to having every VA fluent in whatever CRM, scheduling, or project tools you use within 5 days of hire.",
        "Every small business virtual assistant we place has made it through our screening and a mandatory 4-week training program — covering client communication, scheduling systems, and general business admin — before ever touching client work. From there, VAs can add specialized certifications in admin & executive support, bookkeeping, marketing, sales support, or AI-assisted workflows — so the VA you're matched with brings exactly the mix of skills your business needs, not just general admin. Because mastering one workflow means picking up another quickly, we commit to having every VA fluent in whatever CRM, scheduling, or project tools you use within 5 days of hire.",
    ),
    "keller-williams-leadership-virtual-assistant.html": (
        "Only the top 1% of applicants make it through our screening and mandatory 4-week training program — covering KW Command, Commission Disbursement Authorizations (CDAs), accounts receivable follow-up, and market center marketing support — before they ever touch office work. Every VA is backed by a $1 million Errors &amp; Omissions insurance policy, and because mastering one market center's workflow means picking up another quickly, we commit to having them fluent in your office's systems within 5 days of hire.",
        "Every Keller Williams market center virtual assistant we place has already made it through our screening and a mandatory 4-week training program — covering KW Command, Commission Disbursement Authorizations (CDAs), accounts receivable follow-up, and market center marketing support — before ever touching office work. Market center admins can also add our Business, Finance &amp; Bookkeeping certification — covering bookkeeping fundamentals, QuickBooks ProAdvisor training, and payroll — for even deeper support on the financial side of running your office. Every VA is backed by a $1 million Errors &amp; Omissions insurance policy, and because mastering one market center's workflow means picking up another quickly, we commit to having them fluent in your office's systems within 5 days of hire.",
    ),
    "keller-williams-agent-virtual-assistant.html": (
        "Only the top 1% of applicants make it through our screening and mandatory 4-week training program — covering KW Command, contract writing, and e-signature workflows in dotloop and DocuSign — before they ever touch client work. Every VA trains hands-on in KW Command, and because mastering one database means picking up any other quickly, we commit to having them fluent in whatever CRM you use within 5 days of hire.",
        "Every Keller Williams agent virtual assistant we place has already made it through our screening and a mandatory 4-week training program — covering KW Command, contract writing, and e-signature workflows in dotloop and DocuSign — before ever touching client work. VAs supporting transaction coordination can also complete our Texas Contract Law certification (and Florida Contract Law, for agents closing deals there too) — in-depth training on earnest money, option periods, disclosure timelines, and the closing-document checklist, so your VA already speaks the language of your contracts. Every VA trains hands-on in KW Command, and because mastering one database means picking up any other quickly, we commit to having them fluent in whatever CRM you use within 5 days of hire.",
    ),
}

base = "."
for fname, (old, new) in edits.items():
    path = f"{base}/{fname}"
    with io.open(path, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    if count != 1:
        print(f"MISMATCH ({count} occurrences): {fname}")
        continue
    content = content.replace(old, new, 1)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {fname}")

print("DONE")
