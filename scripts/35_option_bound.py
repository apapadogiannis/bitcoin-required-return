"""Appendix C.5: an option-implied cap on the probability of a collapse to zero.
A put pays its full strike K if the price goes to zero, so (put price / K) bounds the market-implied probability of that event before expiry.
Quotes: Deribit public API (get_book_summary_by_instrument, get_index_price), retrieved 12 November 2026. Output: option_bound.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
from datetime import date
index = 73477.85                                    # Deribit BTC index, USD
quotes = [  # instrument, strike, expiry, bid, ask, mark (BTC), futures price for the expiry, open interest
    ("BTC-25JUN27-30000-P", 30000, date(2027, 6, 25), 0.0030, 0.0035, 0.00327766, 76081.74, 604.1),
    ("BTC-24SEP27-35000-P", 35000, date(2027, 9, 24), 0.0085, 0.0095, 0.00895990, 77170.58, 555.1),
]
out = open(os.path.join(OUT,"option_bound.txt"), "w")
for name, K, exp, bid, ask, mark, fut, oi in quotes:
    T = (exp - date(2026, 11, 12)).days / 365
    usd = ask * index; share = usd / K; cap = share * fut / index      # carried to expiry at the futures basis
    s = (f"{name}: strike {K/index:.0%} of the index; ask {ask} BTC = ${usd:,.0f} = {share:.2%} of strike; "
         f"T = {T:.3f} years; cap on P(collapse to zero before expiry) {cap:.2%}, {cap/T:.2%} a year; open interest {oi}")
    print(s); out.write(s + "\n")
out.close()
