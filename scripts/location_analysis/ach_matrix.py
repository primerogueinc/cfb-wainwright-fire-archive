import csv
W={'H':1.0,'M':0.7,'L':0.4}
H=['H1','H2','H3','H4a','H4b','H5','H6']
E=[
('E1','Landsat 8, 12:17 MDT: 59 hotspots in NW lobe (52.770-52.780N, -110.937 to -110.913)','H','H','N I N II N N N'),
('E2','VIIRS NOAA-20, 14:49 MDT: 8 hotspots 52.769-52.788N; one inside OSM Range 3; hull 0.59 km from Range 2','H','H','C II N II C N N'),
('E3','Sentinel-2 dNBR scar: Range 2 inside (60 m from edge); Range 3 0% burned; zone burned fractions','H','H','C I N C C I C'),
('E4','Scar morphology: axis 130 deg, SE run starts at S edge of pre-shift hull; NE flank passes Range 2; N-S road held east flank N of 52.7705','M','H','C I C I C N C'),
('E5','ECCC CZWN: SW (235) to 3:16 p.m.; 82 km/h gust from 269 at 3:16; 306 (NW) by 4 p.m.','H','H','C I C I C N C'),
('E6','Rutland: fire ~1 km away when wind shifted (computed upwind distances per zone)','M','H','C II II II C C I'),
('E7','Rutland: covered the distance in 30-60 s (=60-120 km/h; implausible)','L','M','N N N N N N N'),
('E8','Rutland: casualties at section-attack admin area; grenade range not affected','M','M','N N N N N N N'),
('E9','Globe and Mail (unverified): "Range 3"','L','M','N C I I I N I'),
('E10','Carignan: fire "far removed from the training area"','L','L','N N N N N N N'),
('E11','DND release: fire reported/ignited ~4 p.m.','L','L','N N N N N N N'),
('E12','GOES-18 FDC fire pixels 15:10 / 15:30 (1215 MW) / 15:40 (south pixel only); 2-4 km pixels','H','L','N N N N N N N'),
('E13','Spread-rate check: 4.8 km run in ~20-40 min (7-14 km/h) => far-SE sites had 15-30 min warning','M','M','C N I N C N I'),
('E14','Base boundary (OSM, corroborated per repo notes): 82% of H3 zone outside CFB Wainwright','M','M','N N I N N N N'),
('E15','dNBR severity: H1 mean 0.50, H6 0.52, H2 0.39 (head-fire intensity in SE run)','M','L','C I N N N I C'),
('E16','Access: collector road dead-ends at 52.7705,-110.8996 + building 52.7701,-110.8963 (1.1-1.3 km downwind of hull, on burn edge); Range 3 has a building','M','L','C C N N N C N'),
]
rows=[];score={h:0.0 for h in H};cnt={h:0 for h in H}
for eid,desc,c,r,rat in E:
    w=round(W[c]*W[r],2); rr=rat.split()
    for h,x in zip(H,rr):
        if x=='I': score[h]-=w; cnt[h]+=1
        if x=='II': score[h]-=2*w; cnt[h]+=1
    rows.append([eid,desc,c,r,w]+rr)
with open('/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/ach/ach_matrix.csv','w') as f:
    wr=csv.writer(f); wr.writerow(['id','evidence','credibility','relevance','weight']+H); wr.writerows(rows)
    wr.writerow(['SCORE','weighted inconsistency','','','']+[round(score[h],2) for h in H])
    wr.writerow(['COUNT','number of I/II','','','']+[cnt[h] for h in H])
print('| ID | Evidence | Cred | Rel | Wt | '+' | '.join(H)+' |'); print('|'+'---|'*(5+len(H)))
for r in rows: print('| '+' | '.join(map(str,r))+' |')
print('| **Weighted inconsistency** | | | | | '+' | '.join(f'**{score[h]:.2f}**' for h in H)+' |')
print('| Count of I/II | | | | | '+' | '.join(str(cnt[h]) for h in H)+' |')
# sensitivity: drop E6 (Rutland 1 km) and E9
for drop in (['E6'],['E6','E9'],['E2'],['E3']):
    s={h:0.0 for h in H}
    for eid,desc,c,r,rat in E:
        if eid in drop: continue
        w=W[c]*W[r]
        for h,x in zip(H,rat.split()):
            s[h]-= w if x=='I' else 2*w if x=='II' else 0
    print('without',drop,{h:round(v,2) for h,v in s.items()})
