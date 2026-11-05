SLIDE 1: Data Sources Overview
Title: Internet Adoption Database — Data Sources

Source	Network type	Years	Firms	Confidence
IETF Internet Monthly Reports	Regional IP (JvNCnet)	1992	9	High
UUCP Mapping Project	UUCP mail	1987–92	9,437	Med/Low
NSFNET PRDB routing additions	NSFNET IP routing	1992–93	3,262	Medium
Scale: 16,433 observations · 10,000 unique firms · 30 countries

Entity types (classified, filterable):
firm 13,582 · school 2,195 · infrastructure 297 · government 216 · military 143

Top countries: USA 13,962 · Germany 384 · France 377 · Canada 258 · UK 219 · Italy 186 · Australia 175 · Japan 111

Speaker notes: Three network types spanning email (UUCP) to IP (NSFNET). entity_type field lets us include/exclude groups on demand — firms are the main set; infrastructure (ANS-CIX, backbones) can be dropped. Dates = earliest appearance; NSFNET later-1993/94 messages were mostly repeats/migrations.

SLIDE 2: Deduplication — Method & Conflict Handling
Title: How We Link & Deduplicate Firms

Matching (two-stage):

Normalize names (lowercase, strip punctuation & legal suffixes: Inc./Corp./Ltd.)
LinkTransformer (semantic, threshold 0.1, blocked by country) catches remaining variants — spelling, &/and, abbreviations
Linking: each firm gets a firm_group_id; all its rows link to it.

Conflict handling — we do NOT discard data:

Keep all granular rows (branches, networks, variants) — nothing overwritten
Disagreements (e.g., two addresses) are preserved, not resolved away
Roll-ups compute the relevant value on demand (e.g., earliest date per network, earliest-ever across networks)
→ No information lost; aggregation is a view, not a destructive merge
Validation: thresholds chosen by inspecting clusters. 0.2 over-merged same-template universities ("Universidad de Murcia/Oviedo"); 0.1 is clean.

Speaker notes: The professor asked "what if two rows disagree?" Answer: we never force a single row — we retain everything linked by firm_group_id, so conflicts are visible and recoverable. We only pick specific values (like earliest date) when computing a summary.

SLIDE 3: Deduplication — Examples (random)
Title: Deduplication Examples

Each firm appears under slightly different names / networks — linked into one firm_group_id, all rows retained:

Firm (linked)	Row as recorded	Network	Date
American Computer & Electronics	"American Computer & Electronics"	UUCP	1991-11
"American Computer and Electronics Corporation"	NSFNET	1992-07
The Portland Group	"The Portland Group, Incorporated"	UUCP	1991-11
"The Portland Group"	NSFNET	1992-04
Unix International	"Unix International, Inc."	UUCP	1991-11
"Unix International"	NSFNET	1992-12
Houghton Mifflin	"Houghton Mifflin Company"	UUCP	1992-03
"Houghton Mifflin Company"	NSFNET	1992-09
Centers for Disease Control	"Centers for Disease Control"	UUCP	1991-11
"The United States Centers For Disease Control"	NSFNET	1992-03
What we retain: both rows + both dates + both networks, under one firm. The "&/and", suffix (Inc./Corp.), and prefix ("The United States...") differences are matched automatically.

Speaker notes: These are randomly sampled. Note the variant types LinkTransformer handles. We keep each network's first date, so we can show the UUCP→NSFNET progression per firm.

SLIDE 4: Key Finding (bonus — strong to include)
Title: Email Before IP — Adoption Progression

Of 308 firms observed on both UUCP (email) and NSFNET (IP routing):

95.5% appeared on UUCP first
Median 1.1 years earlier (mean 2.3)
Robust: holds under both exact-name and LinkTransformer matching
e.g., Adobe: UUCP 1987 → NSFNET 1992

Caveat: sources span different years (UUCP 1987–92, NSFNET 1992–94), biasing toward "UUCP first" → read 1.1 yr as a lower bound.

(Include the uucp_to_nsfnet_gap.png chart here)

SLIDE 5: Next Steps
Title: Next Steps

Sources found, not yet included:

BITNET (BITEARN NODES) — academic network; may have actual connection dates (:CONNECT field); strong European coverage
HOSTS.TXT history — pre-1987 hosts (extends timeline earlier)
Internet Numbers RFCs — network allocations (allocation ≠ connection; earliest adopters)
More IETF monthly reports (other regional networks)
Planned improvements:

Refine entity_type edge cases (e.g., CDC → government)
Cross-source parent-company roll-ups (link divisions to HQ)
Tighten the windowing caveat (find UUCP data for the 1989–90 gap)
Open questions for discussion:

Priority: more sources (breadth) vs. deeper entity resolution (depth)?
Treatment of infrastructure rows (exclude entirely, or keep flagged)?