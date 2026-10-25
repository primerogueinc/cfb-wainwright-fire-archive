"""Working model v4: analysis of competing hypotheses (ACH, after Heuer 1999) for two open questions.
Usage: python3 ach.py REPO
Each item of evidence is rated against each hypothesis: CC strongly consistent (+2), C consistent (+1), N neutral or not applicable (0),
I inconsistent (-1), II strongly inconsistent (-2). Following Heuer, hypotheses are ranked by the weight of evidence AGAINST them
(sum of the negative ratings, times the item's credibility: high 1.0, medium 0.7, low 0.4), not by the evidence for them; an item rated
the same for every hypothesis has no diagnostic value and is flagged. Ratings are judgements; each cites the file or statement it rests on.
Writes model_v4/ach/ach_<question>.csv (matrix), ach_summary.json (scores, diagnosticity) and ach.md (tables for the notes)."""
import sys, os, json
import pandas as pd
REPO = sys.argv[1]; OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/model_v4/ach"); os.makedirs(OUT, exist_ok=True)
VAL = {"CC": 2, "C": 1, "N": 0, "I": -1, "II": -2}; CRED = {"high": 1.0, "medium": 0.7, "low": 0.4}

Q1 = dict(
    name="slow_fire",
    question="Why did the fire spread at about a sixth of the standard rate between 12:17 and 2:49 p.m.?",
    hyp={"H0": "Not really slow: a measurement artefact",
         "H1": "Direct suppression held it",
         "H1b": "Indirect containment: guards or roads at the boundary of permanent danger area 2",
         "H2": "Patchy ground at 10 m scale or larger (bare ground, old burns, gaps)",
         "H2b": "Fine-scale fuel reduction below 10 m (grazing, trampling, cratering, short grass)",
         "H3": "Grass not fully cured (still partly green)",
         "H4": "Damper fine fuel and lighter wind at grass height than the station implies"},
    ev=[
        ("Head advance re-measured 0.33-0.52 km/h allowing for VIIRS pixel size", "h0_speed_check.json", "high",
         dict(H0="I", H1="C", H1b="C", H2="C", H2b="C", H3="C", H4="C")),
        ("Fire energy (VIIRS FRP 75 MW) implies 0.2-0.4 km2/h burned vs 2.7 km2/h at the standard rate", "h0_speed_check.json", "medium",
         dict(H0="II", H1="C", H1b="C", H2="C", H2b="C", H3="C", H4="C")),
        ("No water or bare ground ahead of the head for 2.9 km (head not stalled at Peterson Pond)", "pond_stall.json", "high",
         dict(H0="I", H1="N", H1b="N", H2="I", H2b="N", H3="N", H4="N")),
        ("DND, Oct. 22: PDA 2 'restricted the firefighters ability to conduct direct suppressive operations'; monitored all day", "dnd_briefing_2026-10-22_transcript.txt", "medium",
         dict(H0="N", H1="II", H1b="N", H2="N", H2b="N", H3="N", H4="N")),
        ("DND, Oct. 22: the fire 'initially remained within permanent danger area 2'", "dnd_briefing_2026-10-22_transcript.txt", "medium",
         dict(H0="N", H1="N", H1b="C", H2="N", H2b="C", H3="N", H4="N")),
        ("No unmapped straight edge with a guard signature (bare strip) before or after the fire at 10-20 m", "fireguards_summary.json", "medium",
         dict(H0="N", H1="I", H1b="I", H2="N", H2b="N", H3="N", H4="N")),
        ("Morning path: 0% bare, 0% old burn, 0% patchy 100 m blocks (surroundings 5 / 8 / 20%)", "fuel_paths.json", "high",
         dict(H0="N", H1="N", H1b="N", H2="II", H2b="N", H3="N", H4="N")),
        ("Morning path not greener than afternoon path (NDVI 0.42 vs 0.44)", "fuel_paths.json", "high",
         dict(H0="N", H1="N", H1b="N", H2="N", H2b="N", H3="I", H4="N")),
        ("Curing alone would have to be about 57% to close the gap; mid-October prairie grass is normally 90-100%", "curing_check.json", "medium",
         dict(H0="N", H1="N", H1b="N", H2="N", H2b="N", H3="II", H4="N")),
        ("CWFIS station Oct. 17: FFMC 91.8, FWI 30.8 (Extreme); afternoon humidity 16-23%", "curing_check.json; data/nrcan_cwfis", "high",
         dict(H0="N", H1="N", H1b="N", H2="N", H2b="N", H3="N", H4="I")),
        ("Closing the gap by moisture/wind alone needs e.g. FFMC -6 with wind at 60%, or FFMC -10 at full wind", "moisture_wind.csv", "medium",
         dict(H0="N", H1="N", H1b="N", H2="N", H2b="N", H3="N", H4="I")),
        ("After the front the same kind of grass burned at or near the standard rate (4.4-12 km/h; GOES power x16)", "ensemble_summary.json; h0_speed_check.json", "medium",
         dict(H0="C", H1="C", H1b="C", H2="N", H2b="C", H3="I", H4="C")),
        ("Lower burn severity where it burned before the shift (median dNBR 0.40-0.42 vs 0.47)", "model_v3/severity_oct24", "medium",
         dict(H0="N", H1="N", H1b="N", H2="C", H2b="C", H3="C", H4="C")),
    ])

Q2 = dict(
    name="timeline_location",
    question="Where was the pairs range, and when was it overtaken?",
    hyp={"L1": "Range 2 / road head area, overtaken about 3:20-3:35 ('just before 4:00' approximate)",
         "L2": "Further south-east, 2-3 km from the fire at the shift, overtaken about 3:40-3:55 ('about a kilometre' approximate)",
         "L3": "On the fire's flank (strip south-east of the road head or by the western lake): both statements literal",
         "L4": "The front reached the fire much later than the station (about 3:45), so Range 2 burned just before 4:00"},
    ev=[
        ("Rutland, Oct. 18: fire about a kilometre away when the wind shifted", "part 7; Oct. 18 briefing", "medium",
         dict(L1="C", L2="I", L3="C", L4="C")),
        ("Rutland, Oct. 22: overtook the pairs range 'just before 4:00'", "dnd_briefing_2026-10-22_transcript.txt", "medium",
         dict(L1="I", L2="C", L3="C", L4="C")),
        ("DND release, Oct. 17: 'approximately 4:00 p.m.'", "part7_briefing_check/ABOUT.md", "low",
         dict(L1="I", L2="C", L3="C", L4="C")),
        ("CZWN front 3:16 p.m., 82 km/h gust; station about 15 km west (front at the fire 3:16-3:25)", "data/weather_exports; authentic-stoic-alternative-hypothesis/ABOUT.md", "high",
         dict(L1="C", L2="C", L3="C", L4="II")),
        ("GOES-18 fire power 76 MW (3:10) -> 1,215 MW (3:30); 336 MW at 3:40 in the southern pixel only", "data/goes/fire_timeline.csv", "medium",
         dict(L1="C", L2="C", L3="N", L4="II")),
        ("Model (240 fires): Range 2 median 3:21-3:30, road head 3:26-3:34; 0-9% of fires reach either 3:45-4:00", "ensemble_summary.json; overtaken_time*.json", "medium",
         dict(L1="C", L2="N", L3="I", L4="I")),
        ("Model: ground 600-1,400 m from the edge that also burns 3:45-4:00 is 0-3% of the likely ground", "location_update*.json", "medium",
         dict(L1="N", L2="N", L3="I", L4="N")),
        ("Part 2: 'about a kilometre' read 20 ways lands mostly around Range 2 and the road head (low-moderate confidence)", "part2", "low",
         dict(L1="C", L2="I", L3="C", L4="C")),
        ("CBC (Oct. 22 briefing question): commander said they went from not seeing the fire to it being on top of them", "dnd_briefing_2026-10-22_transcript.txt", "low",
         dict(L1="C", L2="C", L3="N", L4="C")),
        ("Terrain: a rise of about 10 m hides the fire's edge from much of the ground near the road head (part 5)", "part5_visibility", "medium",
         dict(L1="C", L2="N", L3="N", L4="C")),
    ])

summary = {}; md = []
for Q in (Q1, Q2):
    H = list(Q["hyp"]); rows = []
    for e, src, cred, r in Q["ev"]:
        row = dict(evidence=e, source=src, credibility=cred, **{h: r[h] for h in H})
        row["diagnostic"] = len(set(r[h] for h in H)) > 1; rows.append(row)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(OUT, f"ach_{Q['name']}.csv"), index=False)
    score = {}
    for h in H:
        inc = sum(min(VAL[r], 0) * CRED[c] for r, c in zip(df[h], df.credibility))
        net = sum(VAL[r] * CRED[c] for r, c in zip(df[h], df.credibility))
        n_inc = int(sum(VAL[r] < 0 for r in df[h]))
        score[h] = dict(hypothesis=Q["hyp"][h], weighted_inconsistency=round(inc, 2), items_against=n_inc, net_score=round(net, 2))
    rank = sorted(H, key=lambda h: (score[h]["weighted_inconsistency"], score[h]["net_score"]), reverse=True)
    summary[Q["name"]] = dict(question=Q["question"], ranking_least_contradicted_first=rank, scores=score,
                              non_diagnostic_items=df[~df.diagnostic].evidence.tolist())
    md.append(f"#### {Q['question']}\n")
    md.append("| Evidence | Credibility | " + " | ".join(H) + " |"); md.append("|---|---|" + "---|" * len(H))
    for _, r in df.iterrows(): md.append(f"| {r.evidence} | {r.credibility} | " + " | ".join(r[h] for h in H) + " |")
    md.append("| **Weighted evidence against** | | " + " | ".join(f"**{score[h]['weighted_inconsistency']}**" for h in H) + " |\n")
    md.append("Hypotheses: " + "; ".join(f"**{h}** {Q['hyp'][h]}" for h in H) + ".\n")
    md.append("Least contradicted first: " + " > ".join(rank) + ".\n")
json.dump(summary, open(os.path.join(OUT, "ach_summary.json"), "w"), indent=1)
open(os.path.join(OUT, "ach.md"), "w").write("\n".join(md))
print(json.dumps({k: dict(rank=v["ranking_least_contradicted_first"], scores={h: (s["weighted_inconsistency"], s["net_score"]) for h, s in v["scores"].items()}) for k, v in summary.items()}, indent=1))
