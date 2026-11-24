# Flushing & Mylor Pilot Gig Club — Website and Email Style Guide

**Purpose:** Use this guide with Microsoft Copilot, GitHub Copilot, or another AI coding assistant to create consistent, professional and accessible content for Flushing & Mylor Pilot Gig Club (FMPGC).

**How to use it:** Give Copilot this guide at the start of a project, then describe the page or email you want. Ask it to follow the guide, preserve any details you provide, and return complete, usable code. This guide is for both websites and HTML emails; the technical rules differ and must not be mixed up.

## 1. Overall look and feel

Aim for **welcoming, professional, maritime-inspired and easy to read** — a friendly community sports club, not a corporate business or flashy marketing site.

- Keep pages simple, with a clear heading, short introduction and obvious next action.
- Use the same colours, spacing and typography throughout.
- Prefer generous whitespace, tidy alignment, subtle borders and restrained use of decoration.
- Avoid unnecessary animation, visual clutter, enormous banners, excessive icons, stock-photo backgrounds and multiple competing buttons.
- Write in plain British English. Sound helpful and inclusive, not pushy.

## 2. Club colour palette

| Role | Colour | Hex | Use |
|---|---|---|---|
| Primary burgundy | Deep raspberry/burgundy | `#810E49` | Header, headings, links, main buttons |
| Dark burgundy | Dark wine | `#650B39` | Hover states and strong accents |
| Accent gold | Warm gold | `#FFC857` | Highlights and small accents on dark backgrounds |
| Page background | Soft off-white | `#FAF7F8` | Main page background |
| Cards/content | White | `#FFFFFF` | Content sections and tables |
| Main text | Charcoal | `#25202A` | Body text |
| Secondary text | Muted charcoal | `#57505A` | Explanatory text |
| Borders | Pale rose-grey | `#E8DFE4` | Table rules, cards and dividers |

**Contrast rule:** Use white or gold text on burgundy; use burgundy or charcoal text on white/off-white. Never put gold text on a white background. Colour must not be the only way to communicate meaning. Body text should meet at least WCAG AA contrast of 4.5:1; large text at least 3:1.

For ordinary webpages, begin with these reusable CSS variables:

```css
:root {
  --color-primary: #810E49;
  --color-primary-dark: #650B39;
  --color-accent: #FFC857;
  --color-background: #FAF7F8;
  --color-surface: #FFFFFF;
  --color-text: #25202A;
  --color-muted: #57505A;
  --color-border: #E8DFE4;
  --radius: 12px;
  --content-width: 1100px;
}
```

## 3. Typography and hierarchy

- Use a clean, common sans-serif font: `Arial, Helvetica, sans-serif` for reliable results. For a website, a well-supported modern sans-serif is acceptable if already installed.
- Main page heading (`h1`): approximately 34–42 px desktop; 28–34 px mobile.
- Section headings (`h2`): approximately 24–30 px.
- Minor headings (`h3`): approximately 19–22 px.
- Body text: 16–18 px, line height about 1.5–1.7.
- Supporting notes: 14–15 px, never so small that they become difficult to read.
- Use sentence case for most headings. Bold only what needs emphasis.
- Keep long paragraphs to 2–4 sentences when practical; use lists for genuinely scannable information.
- For reading comfort, keep prose lines about 60–75 characters wide where possible.

## 4. Layout and spacing

- Use a centred page container with `max-width: 1100px` and comfortable side padding (16–24 px on smaller screens).
- A header, main content area and footer should feel visually related.
- Use a consistent spacing scale: **8, 16, 24, 32 and 48 px**.
- Separate major sections with about 32–48 px of space.
- Put important information in white cards or clearly separated sections; avoid boxing every paragraph.
- Card corners should be gently rounded (about 12 px), with a fine border or very subtle shadow.
- Use simple, responsive grids where helpful; stack columns vertically on mobile.
- Important information must remain visible and readable without horizontal scrolling.

## 5. Navigation, buttons and links

- Keep navigation short and descriptive: e.g. Home, About, Rowing, Membership, Events, Contact.
- One **primary action** per section. Make the action label specific: “Renew membership”, “Update your details”, “Contact the membership team”.
- Primary button: burgundy background, white text, about 10–14 px rounded corners, generous horizontal padding.
- Secondary action: burgundy outline or a simple underlined link.
- Interactive targets should be at least about **44 × 44 px** where feasible.
- Links should be obvious even without colour alone (for example, underline text links).
- Show a visible keyboard focus state. Support keyboard navigation throughout.
- Do not use vague buttons such as “Click here” when a useful label is possible.

## 6. Images and club identity

- Use genuine club, rowing, boats, coastal or event photography if supplied and approved for use.
- Never invent a club logo, photograph, event, sponsor or endorsement.
- Keep images proportionate and responsive (`max-width: 100%; height: auto`).
- Provide meaningful `alt` text for informative images; use empty alt text for purely decorative ones.
- Do not put important information only inside an image.
- If no approved logo or images are provided, use clear typography and the club colour palette instead.

## 7. Accessibility, responsiveness and code quality

For **webpages**:

- Write semantic HTML5: `header`, `nav`, `main`, `section`, `footer`, correct heading order and proper lists/tables.
- Use one meaningful `h1` per page and logical `h2`/`h3` structure.
- Include `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Make pages work well at 320 px mobile width, tablets and desktops; test the layout at common breakpoints such as 768 px.
- Use native links and buttons, labelled form inputs, useful validation messages and clear error states.
- Respect reduced-motion preferences; avoid unnecessary animations and autoplay.
- Use straightforward HTML and CSS. Add JavaScript only for real functionality.
- Prefer maintainable code and shared CSS styles over repeated inline styles.
- Do not add libraries, analytics, cookies or third-party services unless requested.
- Do not invent URLs, payment information, membership prices, dates or contact details. Use clearly marked placeholders when missing.

For **HTML emails**, use the separate rules in Section 9; webpage techniques such as JavaScript, forms, modern layout grids and external CSS are not reliably supported in email clients.

## 8. Recommended page structure

Use this order unless the content calls for something different:

1. **Club header** — club name or approved logo, and simple navigation if appropriate.
2. **Clear page title** — what the page is for, in plain English.
3. **Short introduction** — one or two sentences explaining what readers can do here.
4. **Main content** — grouped into a few labelled sections, cards or a straightforward table.
5. **Primary call to action** — one clear next step.
6. **Helpful footer** — club name, relevant contact details, and only verified links.

### Content-writing rules

- Keep all supplied facts exact, particularly fees, bank details, contact addresses and dates.
- Never silently change legal wording or a Gift Aid statement. Flag anything that may need review.
- Use a friendly tone: “We’d be delighted to welcome you back” rather than “Is this intentional?”
- Put the key message early. Readers should understand the purpose in the first few seconds.
- Use accessible tables for genuine tabular data, such as membership prices.
- On membership and payment pages, clearly distinguish **fees** from **optional donations**.

## 9. Special rules for HTML emails

For membership reminders, newsletters and event emails, tell Copilot to build a **responsive HTML email**, not a conventional webpage.

- Use a centred email container around **600 px** wide.
- Use **table-based layout** and **inline CSS** for maximum compatibility with Outlook, Gmail and Apple Mail.
- Use common fonts: Arial, Helvetica, sans-serif. Avoid relying on custom webfonts.
- Use burgundy for the header, white content area, and gold as a restrained highlight.
- Keep body text around **16 px**, with generous line spacing.
- Make the main action a robust, clearly labelled link or table-based button.
- Include a plain-text URL fallback where helpful.
- Do not use JavaScript, embedded forms, CSS Grid, flexbox-dependent layouts, video backgrounds or advanced animations.
- Do not depend on external stylesheets, images or scripts for essential content.
- Use table headers and readable row spacing for fee tables; ensure the mobile version is legible.
- Preserve merge placeholders such as `{{Name}}` **exactly as supplied**, including spaces and case.
- Do not guess live form links. A Google Forms URL ending `/edit` is normally for editing, not for the recipient to complete; ask for or insert a placeholder for the actual published respondent link.
- Include a short sign-off, the relevant contact email, and any required footer text.
- Ask for a plain-text alternative to accompany the HTML email.
- Test sample emails in Outlook, Gmail and on a phone before a bulk send.

## 10. Final checks before accepting generated code

Ask Copilot to check the following:

- Does the page look recognisably like FMPGC?
- Is the purpose obvious, with a clearly labelled next step?
- Does it work on mobile and with the keyboard?
- Is the text legible and sufficiently high contrast?
- Are headings, tables, form labels and image descriptions correct?
- Are all links real, working, and directed to the **reader**, not an editor dashboard?
- Are all membership figures, dates, bank details and placeholders preserved exactly?
- Are there unnecessary libraries, scripts, complicated code or decorative elements to remove?
- For emails, will the layout survive Outlook and Gmail, and is there a plain-text version?

---

## 11. Copy-and-paste master prompt for Copilot

Copy the text below whenever you want Copilot to make a new page or improve an existing one:

> You are designing or improving an official Flushing & Mylor Pilot Gig Club (FMPGC) [WEBPAGE / HTML EMAIL]. Follow the attached **FMPGC Website and Email Style Guide**.
>
> Make it professional, welcoming, clean, accessible, easy to read and consistent with our burgundy (`#810E49`) and gold (`#FFC857`) branding. Use Arial/Helvetica or a similarly clear sans-serif font, good contrast, generous spacing and sensible content hierarchy. Make it mobile-friendly.
>
> **Task:** [DESCRIBE WHAT YOU WANT THE PAGE OR EMAIL TO DO].
>
> **Content to include:** [PASTE THE TEXT OR EXISTING HTML].
>
> Preserve factual details, prices, payment instructions, links and merge fields such as `{{Name}}` exactly. Do not invent missing details. If a link or instruction appears incorrect, flag it rather than quietly changing it.
>
> For a **webpage**, use semantic HTML5, maintainable CSS, accessible controls and minimal JavaScript. For an **HTML email**, use table-based layout and inline CSS compatible with Outlook and Gmail; do not use JavaScript or conventional webpage-only layout methods.
>
> Return the **complete, ready-to-save HTML** (and CSS/JavaScript files only if genuinely required). Briefly explain any important changes and identify any items I must check before sending or publishing.

### Example request: improve a membership renewal email

> Apply the FMPGC style guide to the membership renewal email below. Keep all prices and `{{Name}}` placeholders unchanged. Make the opening friendlier, present the membership fees in a clear table, separate the voluntary donation from standard fees, and make the payment details easy to scan. Use email-safe tables and inline CSS. Return complete HTML and a plain-text version. Flag any suspicious form URLs rather than guessing a replacement.

### Example request: build a club events webpage

> Apply the FMPGC style guide to create a mobile-friendly events page. Show each event with its date, location, short description and a clear link where supplied. Do not invent event details or booking links. Use simple semantic HTML and maintainable CSS; return the complete code.
