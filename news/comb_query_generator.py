#!/usr/local/bin/python3

#### ENTITIES #####

coins = [
            {
                "tickers": ("btc", "bitcoin", "bitcoin foundation"),
                "figures": ("satoshi nakamoto"),
            },
            {
                "tickers": ("etc", "ethereum"),
                "figures": ("vitalik buterin", "virgil griffith"),
                "organizations": ("ethereum foundation",),
            },
            {
                "tickers": ("eos", "eos.io"),
                "figures": ("daniel larimer", "brendan blumer"),
                "organizations": ("block.one", "eos foundation"),
            },
            {
                "tickers": ("xrp",),
                "figures": ("david schwartz",),
                "organizations": ("ripple", "ripple labs"),
            },
            {
                "tickers": ("ltc", "litecoin"),
                "figures": ("charlie lee", "john kim"),
                "organizations": ("litecoin core development team",),
            },
            {
                "tickers": ("bch", "bitcoin cash", "bitcoin abc"),
            },
            {
                "tickers": ("bnb", "binance"),
                "figures": ("changpeng zhao",),
                "organizations": ("binance charity foundation",),
            },
            {
                "tickers": ("xlm", "stellar", "stellar lumens"),
                "figures": ("jed mccaleb",),
                "organizations": ("stellar development foundation",),
            },
            {
                "tickers": ("bsv", "bitcoin  sv", "bitcoin satoshi vision"),
                "figures": ("craig wright", "dr craig s wright", "calvin ayre"),
                "organizations": ("nchain",),
            },
        ]

verticals = [
                "",
                "attack", "theft",
                "regulation", "regulatory",
                "development", "roadmap",
                "institutional adoption",
                "announce", "announcement",
            ]

selection = [
        "tickers",
        "figures",
        "organizations",
        ]


#################


def get_queries():
    queries = {}
    for c in coins:
        cn = c["tickers"][0]
        queries.setdefault(cn, [])

        for v in verticals:
            for cat, values in c.items():
                if cat not in selection:
                    continue

                for q in values:
                    fq = " ".join([q, v]) if v else q
                    queries[cn].append(fq)
    return queries


########## MAIN ###########

def main():
    tqs = get_queries()
    total = 0
    for t, qs in tqs.items():
        for q in qs:
            print(q)
            total += 1
    print()
    print("Total: %s" % total)

if __name__ == "__main__":
    main()
