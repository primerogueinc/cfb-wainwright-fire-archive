import boto3, os, sys
from botocore.config import Config
"""Download Sentinel-3 SLSTR FRP files (FRP_in/an/bn.nc + manifest) from CDSE S3.
Usage: CDSE_S3_CREDS=~/.cdse_s3 OUT=dir python3 sentinel3_frp_download.py /eodata/Sentinel-3/... [...]
The creds file is an AWS-style ini ([default] aws_access_key_id / aws_secret_access_key). Never commit it."""
import configparser; c=configparser.ConfigParser(); c.read(os.path.expanduser(os.environ["CDSE_S3_CREDS"])); sec=c[c.sections()[0]]
ak=sec["aws_access_key_id"]; sk=sec["aws_secret_access_key"]
s3=boto3.client("s3",endpoint_url="https://eodata.dataspace.copernicus.eu",aws_access_key_id=ak,aws_secret_access_key=sk,region_name="default",config=Config(request_checksum_calculation="when_required",response_checksum_validation="when_required"))
out=os.environ.get("OUT","s3frp")+"/"; os.makedirs(out,exist_ok=True)
for path in sys.argv[1:]:
    pre=path.lstrip("/").split("/",1)[1]+"/"
    r=s3.list_objects_v2(Bucket="eodata",Prefix=pre)
    names=[o["Key"] for o in r.get("Contents",[])]
    if not names: print("EMPTY",pre); continue
    d=out+pre.rstrip("/").split("/")[-1]; os.makedirs(d,exist_ok=True)
    for k in names:
        b=k.split("/")[-1]
        if (b.startswith("FRP_") and b.endswith(".nc")) or b=="xfdumanifest.xml":
            s3.download_file("eodata",k,d+"/"+b)
    print("ok",d.split("/")[-1][:60],sorted(os.listdir(d)))
