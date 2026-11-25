# holder_surveys.csv: what crypto owners hold, from repeated household surveys

Figures read from published reports, a few numbers per source, on 25 November 2026. They are used in
Appendix B of the paper (holdings per owner against Bitcoin's price) by `scripts/49_holder_surveys.py`
and in the figure drawn by `scripts/26_holder_weight.py`.

## Columns

| Column | Meaning |
|---|---|
| `country`, `survey`, `wave` | The survey and its wave, as the source names it |
| `fieldwork` | When respondents were interviewed |
| `price_from`, `price_to` | The month or months over which Bitcoin's price is averaged for this wave (the fieldwork months) |
| `ownership_pct` | Share of adults who own cryptoassets (UK) or Bitcoin (Canada), percent |
| `owners_million` | The source's estimate of the number of owners, millions (UK only) |
| `median_holding`, `mean_holding` | Value held per owner, in `currency`: all cryptoassets (UK), Bitcoin (Canada) |
| `currency` | GBP or CAD, not adjusted for inflation |

## United Kingdom: Financial Conduct Authority, cryptoasset consumer research

- Median and mean holdings of all four waves: FCA, response to freedom of information request
  FOI2025/00604, "Information on the average value of UK crypto holdings", released 8 September 2025,
  https://www.fca.org.uk/freedom-information/information-average-value-uk-crypto-holdings-september-2025 .
  The response labels the waves 2020, 2021, 2022 and 2024. The means of 2021, 2022 and 2024 and the medians
  of 2022 and 2024 are computed by the FCA from the midpoints of value bands. The share of owners who did
  not state a value was 32%, 42%, 13% and 13%.
- Wave 2 (fieldwork December 2019; 3.9% of adults, about 1.9 million) and wave 3 (fieldwork 5 to 24 January
  2021; 4.4%, about 2.3 million; median £260 rising to £300): FCA, "Research Note: Cryptoasset consumer
  research 2021", 17 June 2021,
  https://www.fca.org.uk/publications/research/research-note-cryptoasset-consumer-research-2021 .
- Wave 4 (fieldwork 9 to 18 August 2022; 9% of adults, 4.97 million; mean £1,595): FCA, "Research Note:
  Cryptoassets consumer research 2023 (Wave 4)", 8 June 2023,
  https://www.fca.org.uk/publication/research-notes/research-note-cryptoasset-consumer-research-2023-wave4.pdf .
- Wave 5 (fieldwork 12 to 21 August 2024; 12% of adults, about 7 million): FCA, "Cryptoassets consumer
  research 2024 (Wave 5)", https://fca.org.uk/publication/research-notes/cryptoasset-consumer-research-2024-wave-5.pdf .
- Two differences between the reports. The wave 5 report gives the 2021 number of owners as 2.2 million and
  the 2022 ownership rate as 10% (5 million); the file keeps the figures of each wave's own report (2.3 million;
  9%, 4.97 million).
- Wave 6 (August to September 2025, 8% of adults) is not in the file: its report gives no mean or median holding.

## Canada: Bank of Canada, Bitcoin Omnibus Survey

- 2018 and 2019 (ownership 5.2% and 5.1%; median holding "from around $500 to $250"): Balutel, D., M.-H. Felt,
  G. Nicholls and M. C. Voia, "Bitcoin Awareness, Ownership and Use: 2016-20", Staff Discussion Paper 2022-10,
  https://www.bankofcanada.ca/wp-content/uploads/2022/04/sdp2022-10.pdf . The paper dates the 2019 survey to
  December 2019 and does not state the month of the 2018 survey; December is assumed here, because the 2023
  paper says the survey is fielded in December "consistent with past versions".
- 2021 and 2022 (ownership 13.1% and 10.1%; median Can$503 and Can$500): Balutel, D., C. S. Henry and D. Rusu,
  "Cryptoasset Ownership and Use in Canada: An Update for 2022", Staff Discussion Paper 2023-14,
  https://www.bankofcanada.ca/wp-content/uploads/2023/07/sdp2023-14.pdf .
- 2023 (ownership 9.9%; median about Can$500; fieldwork 4 to 12 December 2023): Balutel, D., M.-H. Felt and
  D. Rusu, "Canadian Bitcoin Ownership in 2023: Key Takeaways", Staff Discussion Paper 2025-4,
  https://bankofcanada.ca/wp-content/uploads/2025/03/sdp2025-4.pdf .

These are official statistics quoted as facts with their sources; no licence terms of the reports are affected.
