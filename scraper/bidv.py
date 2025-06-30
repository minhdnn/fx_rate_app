import requests
import ssl
from bs4 import BeautifulSoup
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter

class UnsafeLegacyAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        # Cho phép legacy renegotiation
        ctx.options &= ~ssl.OP_NO_RENEGOTIATION
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")  # Hạ security level nếu cần
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

def get_bidv_rates():
    session = requests.Session()
    session.mount("https://", UnsafeLegacyAdapter())

    res = session.get("https://bidv.com.vn/vn/ty-gia-ngoai-te", timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")
    
    # TODO: parse bảng dữ liệu tỉ giá ở đây
    return []

# Test
if __name__ == "__main__":
    print(get_bidv_rates())
