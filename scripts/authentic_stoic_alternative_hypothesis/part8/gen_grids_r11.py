import sys, os, math, numpy as np
REPO="/home/claude/cfb-wainwright-fire-archive"
src=open(REPO+"/scripts/authentic_stoic_alternative_hypothesis/part8/spread_range11.py").read().split("# ---------------- runs")[0]
src=src.replace('OUT = os.path.join(REPO, "data/authentic-stoic-stress-test/part8_range11")','OUT = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/p4_r11"')
src=src.replace("r = R * (1 - E) / (1 - E * math.cos(phi))","r = R * (1 - EE) / (1 - EE * math.cos(phi))")
src=src.replace("def run(sched, tf, ros_kmh, fuel, t_end=mdt(\"18:00\")):","def run(sched, tf, ros_kmh, fuel, t_end=mdt(\"18:00\"), EE=None):\n    EE = E if EE is None else EE")
sys.argv=["x",REPO]; exec(src)
OUT="/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/p4_r11"
np.save(OUT+"/meta.npy",np.array([minx,maxy,RES,H,W]))
SCHED=["S0_fixed306","S1_stoic","S2_station_veer","S3_fast_veer","S4_fixed315"]
for lbname,lb in (("steady",LB),("gusty",3.0)):
    EE=math.sqrt(1-1/lb**2)
    for s in SCHED:
        for ros in (4.4,8.0,12.0):
            A=run(schedule(s,mdt("15:16")),mdt("15:16"),ros,fuel_scar,t_end=mdt("18:30"),EE=EE)
            np.save(f"{OUT}/arr_{s}_{ros}_{lbname}.npy",A.astype("float32")); print(lbname,s,ros,flush=True)
np.save(OUT+"/fuel_scar.npy",fuel_scar)
