window.CAPEX_DATA = {
 "verdict": {
  "stage": 1,
  "stage_raw": 1,
  "stage_name": "Friction",
  "clusters": [
   {
    "id": "A",
    "name": "Demand",
    "score": 0
   },
   {
    "id": "B",
    "name": "Physical supply",
    "score": 1
   },
   {
    "id": "C",
    "name": "Financing",
    "score": 1
   },
   {
    "id": "D",
    "name": "The paying end",
    "score": 1
   }
  ],
  "red": 0,
  "amber": 3,
  "confirmed": {
   "A2": 1,
   "A1": 0,
   "A3": 0,
   "D3": 1,
   "C2": 0,
   "D2": 1,
   "B4": 1,
   "A4": 0,
   "B2": 0,
   "B3": 1,
   "C1": 1,
   "C3": 1,
   "C4": 0,
   "D1": 1,
   "D4": 0
  },
  "confirmation_ready": false,
  "history_days": 1
 },
 "alerts": [],
 "generated": "2026-08-21 08:54 UTC",
 "generated_date": "2026-08-21",
 "auto": {
  "A2": {
   "state": 1,
   "value": 71.3,
   "unit": "%",
   "detail": "median of 5 hyperscalers, trailing twelve months"
  },
  "A1": {
   "state": 0,
   "value": 79.6,
   "unit": "% YoY",
   "detail": "median realised capex growth, trailing twelve months"
  },
  "A3": {
   "state": 0,
   "value": 19.8,
   "unit": "% QoQ",
   "detail": "prior quarter 19.5% \u2014 total revenue, the data-centre split needs the release itself"
  },
  "D3": {
   "state": 1,
   "value": 61.8,
   "unit": "pp",
   "detail": "median capex growth minus total revenue growth, trailing twelve months. Prior two quarters: 48.0pp, 52.5pp. A proxy \u2014 total revenue dilutes AI revenue, so the true AI-level gap is smaller."
  },
  "C2": {
   "state": 0,
   "value": 273,
   "unit": "bp",
   "detail": "US high-yield spread, -25bp over six months"
  },
  "B1": {
   "state": null,
   "value": 4.0084,
   "unit": "$/hr H200",
   "detail": "1 day(s) of history \u2014 a trend needs about a month"
  },
  "D2": {
   "state": 1,
   "value": 2.7,
   "unit": "% YoY",
   "detail": "CPI, personal computers and peripherals \u2014 this series normally declines"
  },
  "B4": {
   "state": 1,
   "value": 27.1,
   "unit": "% YoY",
   "detail": "PPI semiconductors, six-month change 18.8% \u2014 a proxy; spot DRAM leads it"
  }
 },
 "companies": [
  {
   "ticker": "MSFT",
   "name": "Microsoft",
   "asof": "2026-06-30",
   "stale": false,
   "tags": {
    "capex": "PaymentsToAcquirePropertyPlantAndEquipment",
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax"
   },
   "capex_ttm": 115948000000,
   "ocf_ttm": 182935000000,
   "rev_ttm": 331839000000,
   "capex_ocf": 63.38207560062317,
   "capex_ocf_prev": 57.14378074655727,
   "capex_growth": 79.62231413920776,
   "rev_growth": 17.78868679984666,
   "coverage_gap": 61.8336273393611,
   "coverage_gap_hist": [
    61.8336273393611,
    40.61435123308284,
    32.905485595236655
   ],
   "rev_q": [
    {
     "end": "2024-06-30",
     "val": 64727000000
    },
    {
     "end": "2024-09-30",
     "val": 65585000000
    },
    {
     "end": "2024-12-31",
     "val": 69632000000
    },
    {
     "end": "2025-03-31",
     "val": 70066000000
    },
    {
     "end": "2025-06-30",
     "val": 76441000000
    },
    {
     "end": "2025-09-30",
     "val": 77673000000
    },
    {
     "end": "2025-12-31",
     "val": 81273000000
    },
    {
     "end": "2026-03-31",
     "val": 82886000000
    },
    {
     "end": "2026-06-30",
     "val": 90007000000
    }
   ],
   "capex_q": [
    {
     "end": "2024-06-30",
     "val": 13873000000
    },
    {
     "end": "2024-09-30",
     "val": 14923000000
    },
    {
     "end": "2024-12-31",
     "val": 15804000000
    },
    {
     "end": "2025-03-31",
     "val": 16745000000
    },
    {
     "end": "2025-06-30",
     "val": 17079000000
    },
    {
     "end": "2025-09-30",
     "val": 19394000000
    },
    {
     "end": "2025-12-31",
     "val": 29876000000
    },
    {
     "end": "2026-03-31",
     "val": 30876000000
    },
    {
     "end": "2026-06-30",
     "val": 35802000000
    }
   ]
  },
  {
   "ticker": "AMZN",
   "name": "Amazon",
   "asof": "2026-06-30",
   "stale": false,
   "tags": {
    "capex": "PaymentsToAcquireProductiveAssets",
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax"
   },
   "capex_ttm": 173028000000,
   "ocf_ttm": 161403000000,
   "rev_ttm": 775680000000,
   "capex_ocf": 107.20246835560678,
   "capex_ocf_prev": 101.66429903521824,
   "capex_growth": 60.72304376904213,
   "rev_growth": 15.766568463281185,
   "coverage_gap": 44.95647530576095,
   "coverage_gap_hist": [
    44.95647530576095,
    47.9883802953741,
    46.44223109966654
   ],
   "rev_q": [
    {
     "end": "2024-06-30",
     "val": 147977000000
    },
    {
     "end": "2024-09-30",
     "val": 158877000000
    },
    {
     "end": "2024-12-31",
     "val": 187792000000
    },
    {
     "end": "2025-03-31",
     "val": 155667000000
    },
    {
     "end": "2025-06-30",
     "val": 167702000000
    },
    {
     "end": "2025-09-30",
     "val": 180169000000
    },
    {
     "end": "2025-12-31",
     "val": 213386000000
    },
    {
     "end": "2026-03-31",
     "val": 181519000000
    },
    {
     "end": "2026-06-30",
     "val": 200606000000
    }
   ],
   "capex_q": [
    {
     "end": "2024-06-30",
     "val": 17620000000
    },
    {
     "end": "2024-09-30",
     "val": 22620000000
    },
    {
     "end": "2024-12-31",
     "val": 27834000000
    },
    {
     "end": "2025-03-31",
     "val": 25019000000
    },
    {
     "end": "2025-06-30",
     "val": 32183000000
    },
    {
     "end": "2025-09-30",
     "val": 35095000000
    },
    {
     "end": "2025-12-31",
     "val": 39522000000
    },
    {
     "end": "2026-03-31",
     "val": 44203000000
    },
    {
     "end": "2026-06-30",
     "val": 54208000000
    }
   ]
  },
  {
   "ticker": "GOOGL",
   "name": "Alphabet",
   "asof": "2026-06-30",
   "stale": false,
   "tags": {
    "capex": "PaymentsToAcquirePropertyPlantAndEquipment",
    "revenue": "Revenues"
   },
   "capex_ttm": 132402000000,
   "ocf_ttm": 185675000000,
   "rev_ttm": 445867000000,
   "capex_ocf": 71.30846909923252,
   "capex_ocf_prev": 63.04680733913383,
   "capex_growth": 97.6739325171693,
   "rev_growth": 20.050673265140727,
   "coverage_gap": 77.62325925202857,
   "coverage_gap_hist": [
    77.62325925202857,
    72.98904979608763,
    52.49755007771792
   ],
   "rev_q": [
    {
     "end": "2024-06-30",
     "val": 84742000000
    },
    {
     "end": "2024-09-30",
     "val": 88268000000
    },
    {
     "end": "2024-12-31",
     "val": 96469000000
    },
    {
     "end": "2025-03-31",
     "val": 90234000000
    },
    {
     "end": "2025-06-30",
     "val": 96428000000
    },
    {
     "end": "2025-09-30",
     "val": 102346000000
    },
    {
     "end": "2025-12-31",
     "val": 113829000000
    },
    {
     "end": "2026-03-31",
     "val": 109896000000
    },
    {
     "end": "2026-06-30",
     "val": 119796000000
    }
   ],
   "capex_q": [
    {
     "end": "2024-06-30",
     "val": 13186000000
    },
    {
     "end": "2024-09-30",
     "val": 13061000000
    },
    {
     "end": "2024-12-31",
     "val": 14276000000
    },
    {
     "end": "2025-03-31",
     "val": 17197000000
    },
    {
     "end": "2025-06-30",
     "val": 22446000000
    },
    {
     "end": "2025-09-30",
     "val": 23953000000
    },
    {
     "end": "2025-12-31",
     "val": 27851000000
    },
    {
     "end": "2026-03-31",
     "val": 35674000000
    },
    {
     "end": "2026-06-30",
     "val": 44924000000
    }
   ]
  },
  {
   "ticker": "META",
   "name": "Meta",
   "asof": "2026-06-30",
   "stale": false,
   "tags": {
    "capex": "PaymentsToAcquirePropertyPlantAndEquipment",
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax"
   },
   "capex_ttm": 89325000000,
   "ocf_ttm": 130301000000,
   "rev_ttm": 228247000000,
   "capex_ocf": 68.55281233451777,
   "capex_ocf_prev": 61.08629032258065,
   "capex_growth": 71.24535102181665,
   "rev_growth": 27.65206594930762,
   "coverage_gap": 43.593285072509026,
   "coverage_gap_hist": [
    43.593285072509026,
    46.76843298100225,
    64.89262919564821
   ],
   "rev_q": [
    {
     "end": "2024-06-30",
     "val": 39071000000
    },
    {
     "end": "2024-09-30",
     "val": 40589000000
    },
    {
     "end": "2024-12-31",
     "val": 48385000000
    },
    {
     "end": "2025-03-31",
     "val": 42314000000
    },
    {
     "end": "2025-06-30",
     "val": 47516000000
    },
    {
     "end": "2025-09-30",
     "val": 51242000000
    },
    {
     "end": "2025-12-31",
     "val": 59893000000
    },
    {
     "end": "2026-03-31",
     "val": 56311000000
    },
    {
     "end": "2026-06-30",
     "val": 60801000000
    }
   ],
   "capex_q": [
    {
     "end": "2024-06-30",
     "val": 8173000000
    },
    {
     "end": "2024-09-30",
     "val": 8258000000
    },
    {
     "end": "2024-12-31",
     "val": 14425000000
    },
    {
     "end": "2025-03-31",
     "val": 12941000000
    },
    {
     "end": "2025-06-30",
     "val": 16538000000
    },
    {
     "end": "2025-09-30",
     "val": 18829000000
    },
    {
     "end": "2025-12-31",
     "val": 21383000000
    },
    {
     "end": "2026-03-31",
     "val": 18997000000
    },
    {
     "end": "2026-06-30",
     "val": 30116000000
    }
   ]
  },
  {
   "ticker": "ORCL",
   "name": "Oracle",
   "asof": "2026-05-31",
   "stale": false,
   "tags": {
    "capex": "PaymentsToAcquirePropertyPlantAndEquipment",
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax"
   },
   "capex_ttm": 55663000000,
   "ocf_ttm": 31977000000,
   "rev_ttm": 67358000000,
   "capex_ocf": 174.07198924226788,
   "capex_ocf_prev": 205.19690397210172,
   "capex_growth": 162.37567758661325,
   "rev_growth": 17.350476489137442,
   "coverage_gap": 145.02520109747582,
   "coverage_gap_hist": [
    145.02520109747582,
    208.24156178495284,
    219.0968631807721
   ],
   "rev_q": [
    {
     "end": "2024-05-31",
     "val": 14287000000
    },
    {
     "end": "2024-08-31",
     "val": 13307000000
    },
    {
     "end": "2024-11-30",
     "val": 14059000000
    },
    {
     "end": "2025-02-28",
     "val": 14130000000
    },
    {
     "end": "2025-05-31",
     "val": 15903000000
    },
    {
     "end": "2025-08-31",
     "val": 14926000000
    },
    {
     "end": "2025-11-30",
     "val": 16058000000
    },
    {
     "end": "2026-02-28",
     "val": 17190000000
    },
    {
     "end": "2026-05-31",
     "val": 19184000000
    }
   ],
   "capex_q": [
    {
     "end": "2024-05-31",
     "val": 2798000000
    },
    {
     "end": "2024-08-31",
     "val": 2303000000
    },
    {
     "end": "2024-11-30",
     "val": 3970000000
    },
    {
     "end": "2025-02-28",
     "val": 5862000000
    },
    {
     "end": "2025-05-31",
     "val": 9080000000
    },
    {
     "end": "2025-08-31",
     "val": 8502000000
    },
    {
     "end": "2025-11-30",
     "val": 12033000000
    },
    {
     "end": "2026-02-28",
     "val": 18635000000
    },
    {
     "end": "2026-05-31",
     "val": 16493000000
    }
   ]
  },
  {
   "ticker": "NVDA",
   "name": "Nvidia",
   "asof": "2026-04-26",
   "stale": false,
   "tags": {
    "capex": "PaymentsToAcquireProductiveAssets",
    "revenue": "Revenues"
   },
   "capex_ttm": 6572000000,
   "ocf_ttm": 125648000000,
   "rev_ttm": 253491000000,
   "capex_ocf": 5.230485164905132,
   "capex_ocf_prev": 5.882123873128371,
   "capex_growth": 60.5276013678554,
   "rev_growth": 70.68376931623068,
   "coverage_gap": -10.156167948375284,
   "coverage_gap_hist": [
    -10.156167948375284,
    21.238454321153654,
    76.59608759825367
   ],
   "rev_q": [
    {
     "end": "2024-04-28",
     "val": 26044000000
    },
    {
     "end": "2024-07-28",
     "val": 30040000000
    },
    {
     "end": "2024-10-27",
     "val": 35082000000
    },
    {
     "end": "2025-01-26",
     "val": 39331000000
    },
    {
     "end": "2025-04-27",
     "val": 44062000000
    },
    {
     "end": "2025-07-27",
     "val": 46743000000
    },
    {
     "end": "2025-10-26",
     "val": 57006000000
    },
    {
     "end": "2026-01-25",
     "val": 68127000000
    },
    {
     "end": "2026-04-26",
     "val": 81615000000
    }
   ],
   "capex_q": [
    {
     "end": "2024-04-28",
     "val": 369000000
    },
    {
     "end": "2024-07-28",
     "val": 977000000
    },
    {
     "end": "2024-10-27",
     "val": 813000000
    },
    {
     "end": "2025-01-26",
     "val": 1077000000
    },
    {
     "end": "2025-04-27",
     "val": 1227000000
    },
    {
     "end": "2025-07-27",
     "val": 1895000000
    },
    {
     "end": "2025-10-26",
     "val": 1636000000
    },
    {
     "end": "2026-01-25",
     "val": 1284000000
    },
    {
     "end": "2026-04-26",
     "val": 1757000000
    }
   ]
  }
 ],
 "fred": {
  "hy_oas": {
   "series": "BAMLH0A0HYM2",
   "latest": {
    "d": "2026-08-19",
    "v": 2.73
   },
   "yoy": -5.20833333333333,
   "chg_6m": -8.389261744966444,
   "abs_6m": -0.25,
   "spark": [
    2.72,
    2.74,
    2.72,
    2.71,
    2.75,
    2.74,
    2.76,
    2.75,
    2.78,
    2.8,
    2.78,
    2.71,
    2.66,
    2.71,
    2.63,
    2.66,
    2.66,
    2.65,
    2.71,
    2.76,
    2.78,
    2.83,
    2.8,
    2.75,
    2.74,
    2.75,
    2.74,
    2.72,
    2.67,
    2.7,
    2.7,
    2.69,
    2.69,
    2.72,
    2.71,
    2.71,
    2.73,
    2.69,
    2.69,
    2.68,
    2.77,
    2.79,
    2.81,
    2.84,
    2.87,
    2.84,
    2.85,
    2.78,
    2.73,
    2.75,
    2.71,
    2.7,
    2.7,
    2.72,
    2.71,
    2.71,
    2.67,
    2.7,
    2.75,
    2.73
   ],
   "spark_dates": [
    "2026-05-29",
    "2026-05-31",
    "2026-06-01",
    "2026-06-02",
    "2026-06-03",
    "2026-06-04",
    "2026-06-05",
    "2026-06-08",
    "2026-06-09",
    "2026-06-10",
    "2026-06-11",
    "2026-06-12",
    "2026-06-15",
    "2026-06-16",
    "2026-06-17",
    "2026-06-18",
    "2026-06-19",
    "2026-06-22",
    "2026-06-23",
    "2026-06-24",
    "2026-06-25",
    "2026-06-26",
    "2026-06-29",
    "2026-06-30",
    "2026-07-01",
    "2026-07-02",
    "2026-07-03",
    "2026-07-06",
    "2026-07-07",
    "2026-07-08",
    "2026-07-09",
    "2026-07-10",
    "2026-07-13",
    "2026-07-14",
    "2026-07-15",
    "2026-07-16",
    "2026-07-17",
    "2026-07-20",
    "2026-07-21",
    "2026-07-22",
    "2026-07-23",
    "2026-07-24",
    "2026-07-27",
    "2026-07-28",
    "2026-07-29",
    "2026-07-30",
    "2026-07-31",
    "2026-08-03",
    "2026-08-04",
    "2026-08-05",
    "2026-08-06",
    "2026-08-07",
    "2026-08-10",
    "2026-08-11",
    "2026-08-12",
    "2026-08-13",
    "2026-08-14",
    "2026-08-17",
    "2026-08-18",
    "2026-08-19"
   ],
   "n": 787
  },
  "semi_ppi": {
   "series": "PCU3344133441",
   "latest": {
    "d": "2026-07-01",
    "v": 73.154
   },
   "yoy": 27.05641239405307,
   "chg_6m": 18.789276261305876,
   "abs_6m": 11.570999999999998,
   "spark": [
    54.775,
    54.885,
    54.957,
    55.26,
    55.43,
    56.346,
    56.376,
    56.736,
    56.498,
    56.634,
    56.927,
    56.815,
    56.643,
    56.832,
    57.323,
    57.601,
    57.617,
    57.242,
    57.238,
    57.302,
    57.152,
    56.59,
    56.743,
    56.929,
    57.135,
    57.372,
    57.384,
    57.602,
    57.547,
    57.884,
    58.055,
    58.105,
    58.256,
    58.205,
    58.062,
    57.463,
    57.494,
    57.543,
    58.003,
    58.936,
    58.828,
    58.272,
    58.07,
    58.425,
    58.322,
    58.328,
    57.606,
    57.576,
    59.637,
    59.765,
    60.125,
    60.868,
    61.063,
    61.583,
    67.019,
    68.282,
    73.177,
    72.861,
    73.56,
    73.154
   ],
   "spark_dates": [
    "2021-08-01",
    "2021-09-01",
    "2021-10-01",
    "2021-11-01",
    "2021-12-01",
    "2022-01-01",
    "2022-02-01",
    "2022-03-01",
    "2022-04-01",
    "2022-05-01",
    "2022-06-01",
    "2022-07-01",
    "2022-08-01",
    "2022-09-01",
    "2022-10-01",
    "2022-11-01",
    "2022-12-01",
    "2023-01-01",
    "2023-02-01",
    "2023-03-01",
    "2023-04-01",
    "2023-05-01",
    "2023-06-01",
    "2023-07-01",
    "2023-08-01",
    "2023-09-01",
    "2023-10-01",
    "2023-11-01",
    "2023-12-01",
    "2024-01-01",
    "2024-02-01",
    "2024-03-01",
    "2024-04-01",
    "2024-05-01",
    "2024-06-01",
    "2024-07-01",
    "2024-08-01",
    "2024-09-01",
    "2024-10-01",
    "2024-11-01",
    "2024-12-01",
    "2025-01-01",
    "2025-02-01",
    "2025-03-01",
    "2025-04-01",
    "2025-05-01",
    "2025-06-01",
    "2025-07-01",
    "2025-08-01",
    "2025-09-01",
    "2025-10-01",
    "2025-11-01",
    "2025-12-01",
    "2026-01-01",
    "2026-02-01",
    "2026-03-01",
    "2026-04-01",
    "2026-05-01",
    "2026-06-01",
    "2026-07-01"
   ],
   "n": 500
  },
  "pc_cpi": {
   "series": "CUSR0000SEEE01",
   "latest": {
    "d": "2026-07-01",
    "v": 36.641
   },
   "yoy": 2.6789967773574217,
   "chg_6m": 5.371984010582908,
   "abs_6m": 1.867999999999995,
   "spark": [
    40.135,
    40.184,
    40.649,
    40.31,
    39.78,
    39.401,
    39.651,
    39.958,
    40.302,
    39.446,
    38.909,
    39.421,
    38.719,
    38.469,
    39.175,
    39.076,
    38.02,
    37.115,
    37.21,
    37.712,
    37.957,
    37.449,
    37.289,
    37.357,
    36.82,
    36.529,
    37.146,
    36.845,
    36.258,
    35.773,
    36.441,
    36.695,
    36.528,
    36.865,
    36.476,
    35.778,
    35.929,
    35.792,
    35.406,
    34.849,
    34.259,
    33.942,
    34.237,
    34.477,
    34.547,
    34.805,
    35.202,
    35.685,
    35.273,
    35.064,
    35.141,
    34.184,
    33.73,
    34.773,
    34.782,
    35.293,
    35.601,
    35.662,
    35.406,
    36.641
   ],
   "spark_dates": [
    "2021-07-01",
    "2021-08-01",
    "2021-09-01",
    "2021-10-01",
    "2021-11-01",
    "2021-12-01",
    "2022-01-01",
    "2022-02-01",
    "2022-03-01",
    "2022-04-01",
    "2022-05-01",
    "2022-06-01",
    "2022-07-01",
    "2022-08-01",
    "2022-09-01",
    "2022-10-01",
    "2022-11-01",
    "2022-12-01",
    "2023-01-01",
    "2023-02-01",
    "2023-03-01",
    "2023-04-01",
    "2023-05-01",
    "2023-06-01",
    "2023-07-01",
    "2023-08-01",
    "2023-09-01",
    "2023-10-01",
    "2023-11-01",
    "2023-12-01",
    "2024-01-01",
    "2024-02-01",
    "2024-03-01",
    "2024-04-01",
    "2024-05-01",
    "2024-06-01",
    "2024-07-01",
    "2024-08-01",
    "2024-09-01",
    "2024-10-01",
    "2024-11-01",
    "2024-12-01",
    "2025-01-01",
    "2025-02-01",
    "2025-03-01",
    "2025-04-01",
    "2025-05-01",
    "2025-06-01",
    "2025-07-01",
    "2025-08-01",
    "2025-09-01",
    "2025-11-01",
    "2025-12-01",
    "2026-01-01",
    "2026-02-01",
    "2026-03-01",
    "2026-04-01",
    "2026-05-01",
    "2026-06-01",
    "2026-07-01"
   ],
   "n": 258
  },
  "semi_ip": {
   "series": "IPG3344S",
   "latest": {
    "d": "2026-07-01",
    "v": 191.8973
   },
   "yoy": 11.85727067916797,
   "chg_6m": 8.59423101300207,
   "abs_6m": 15.186900000000009,
   "spark": [
    117.8182,
    118.1095,
    119.9345,
    122.4168,
    124.7074,
    125.773,
    128.9521,
    129.5542,
    127.9384,
    128.77,
    131.2495,
    131.7061,
    132.8333,
    134.0567,
    132.9257,
    133.4489,
    130.8489,
    130.0403,
    133.54,
    133.5331,
    135.8398,
    136.0676,
    135.4366,
    136.6894,
    135.6233,
    134.4233,
    136.4045,
    137.8263,
    138.9374,
    139.4212,
    138.2248,
    138.3547,
    143.8737,
    144.2792,
    143.4192,
    143.4068,
    148.7946,
    146.4195,
    148.7125,
    148.1992,
    150.2275,
    158.0732,
    159.6876,
    159.2281,
    162.2271,
    164.3526,
    163.1741,
    171.5555,
    169.197,
    165.667,
    169.1163,
    169.7424,
    170.5402,
    176.7104,
    176.1804,
    173.4832,
    176.4046,
    183.8045,
    187.4427,
    191.8973
   ],
   "spark_dates": [
    "2021-08-01",
    "2021-09-01",
    "2021-10-01",
    "2021-11-01",
    "2021-12-01",
    "2022-01-01",
    "2022-02-01",
    "2022-03-01",
    "2022-04-01",
    "2022-05-01",
    "2022-06-01",
    "2022-07-01",
    "2022-08-01",
    "2022-09-01",
    "2022-10-01",
    "2022-11-01",
    "2022-12-01",
    "2023-01-01",
    "2023-02-01",
    "2023-03-01",
    "2023-04-01",
    "2023-05-01",
    "2023-06-01",
    "2023-07-01",
    "2023-08-01",
    "2023-09-01",
    "2023-10-01",
    "2023-11-01",
    "2023-12-01",
    "2024-01-01",
    "2024-02-01",
    "2024-03-01",
    "2024-04-01",
    "2024-05-01",
    "2024-06-01",
    "2024-07-01",
    "2024-08-01",
    "2024-09-01",
    "2024-10-01",
    "2024-11-01",
    "2024-12-01",
    "2025-01-01",
    "2025-02-01",
    "2025-03-01",
    "2025-04-01",
    "2025-05-01",
    "2025-06-01",
    "2025-07-01",
    "2025-08-01",
    "2025-09-01",
    "2025-10-01",
    "2025-11-01",
    "2025-12-01",
    "2026-01-01",
    "2026-02-01",
    "2026-03-01",
    "2026-04-01",
    "2026-05-01",
    "2026-06-01",
    "2026-07-01"
   ],
   "n": 655
  }
 },
 "gpus": [
  {
   "gpu": "H200",
   "offers": 6,
   "median": 4.0084,
   "p25": 2.9664,
   "min": 2.6418
  },
  {
   "gpu": "B200",
   "offers": 6,
   "median": 5.5962,
   "p25": 4.6271,
   "min": 4.6267
  },
  {
   "gpu": "H100 SXM",
   "offers": 11,
   "median": 2.0022,
   "p25": 1.3901,
   "min": 0.9901
  }
 ],
 "gpu_history": [
  {
   "date": "2026-08-21",
   "gpu": {
    "H200": {
     "median": 4.0084,
     "offers": 6
    },
    "B200": {
     "median": 5.5962,
     "offers": 6
    },
    "H100 SXM": {
     "median": 2.0022,
     "offers": 11
    }
   }
  }
 ],
 "context": {
  "semi_ip": {
   "series": "IPG3344S",
   "latest": {
    "d": "2026-07-01",
    "v": 191.8973
   },
   "yoy": 11.85727067916797,
   "chg_6m": 8.59423101300207,
   "abs_6m": 15.186900000000009,
   "spark": [
    117.8182,
    118.1095,
    119.9345,
    122.4168,
    124.7074,
    125.773,
    128.9521,
    129.5542,
    127.9384,
    128.77,
    131.2495,
    131.7061,
    132.8333,
    134.0567,
    132.9257,
    133.4489,
    130.8489,
    130.0403,
    133.54,
    133.5331,
    135.8398,
    136.0676,
    135.4366,
    136.6894,
    135.6233,
    134.4233,
    136.4045,
    137.8263,
    138.9374,
    139.4212,
    138.2248,
    138.3547,
    143.8737,
    144.2792,
    143.4192,
    143.4068,
    148.7946,
    146.4195,
    148.7125,
    148.1992,
    150.2275,
    158.0732,
    159.6876,
    159.2281,
    162.2271,
    164.3526,
    163.1741,
    171.5555,
    169.197,
    165.667,
    169.1163,
    169.7424,
    170.5402,
    176.7104,
    176.1804,
    173.4832,
    176.4046,
    183.8045,
    187.4427,
    191.8973
   ],
   "spark_dates": [
    "2021-08-01",
    "2021-09-01",
    "2021-10-01",
    "2021-11-01",
    "2021-12-01",
    "2022-01-01",
    "2022-02-01",
    "2022-03-01",
    "2022-04-01",
    "2022-05-01",
    "2022-06-01",
    "2022-07-01",
    "2022-08-01",
    "2022-09-01",
    "2022-10-01",
    "2022-11-01",
    "2022-12-01",
    "2023-01-01",
    "2023-02-01",
    "2023-03-01",
    "2023-04-01",
    "2023-05-01",
    "2023-06-01",
    "2023-07-01",
    "2023-08-01",
    "2023-09-01",
    "2023-10-01",
    "2023-11-01",
    "2023-12-01",
    "2024-01-01",
    "2024-02-01",
    "2024-03-01",
    "2024-04-01",
    "2024-05-01",
    "2024-06-01",
    "2024-07-01",
    "2024-08-01",
    "2024-09-01",
    "2024-10-01",
    "2024-11-01",
    "2024-12-01",
    "2025-01-01",
    "2025-02-01",
    "2025-03-01",
    "2025-04-01",
    "2025-05-01",
    "2025-06-01",
    "2025-07-01",
    "2025-08-01",
    "2025-09-01",
    "2025-10-01",
    "2025-11-01",
    "2025-12-01",
    "2026-01-01",
    "2026-02-01",
    "2026-03-01",
    "2026-04-01",
    "2026-05-01",
    "2026-06-01",
    "2026-07-01"
   ],
   "n": 655
  },
  "gpu_all": [
   {
    "gpu": "H200",
    "offers": 6,
    "median": 4.0084,
    "p25": 2.9664,
    "min": 2.6418
   },
   {
    "gpu": "B200",
    "offers": 6,
    "median": 5.5962,
    "p25": 4.6271,
    "min": 4.6267
   },
   {
    "gpu": "H100 SXM",
    "offers": 11,
    "median": 2.0022,
    "p25": 1.3901,
    "min": 0.9901
   }
  ]
 },
 "manual": {
  "_comment": "Sensors with no machine-readable feed. Updated by research, not by fetch.py. Each carries its own 'asof' date; the dashboard marks anything older than 45 days as stale so a forgotten sensor cannot quietly pass for a current reading. state: 0 calm, 1 watch, 2 turning.",
  "A4": {
   "state": 0,
   "value": "supply-constrained",
   "detail": "No hyperscaler has yet introduced optimisation language on an earnings call while still guiding capex up. The tell to look for is the shift from 'demand exceeds our supply' to 'measured', 'digesting', 'prioritising utilisation', 'capital discipline'.",
   "asof": "2026-08-21",
   "source": "Quarterly earnings call transcripts"
  },
  "B2": {
   "state": 0,
   "value": "1.8% / 3.6% / 5.8%",
   "detail": "Data-centre vacancy at record lows in North America, Europe and Asia-Pacific, with H1 2026 absorption a record 25 GW. Hyperscalers account for about 59% of 2026 tenant demand.",
   "asof": "2026-08-21",
   "source": "JLL midyear 2026 North America report; CBRE Global Data Center Trends 2026"
  },
  "B3": {
   "state": 1,
   "value": "~6,000 MW, first decline since 2020",
   "detail": "Around twenty US data-centre projects were cancelled in Q1 2026, and capacity under construction across the eight primary US markets fell at end-2025 for the first time since 2020, from roughly 6,350 MW to just under 6,000 MW. Read against record absorption in B2, this is the board's first genuine tension \u2014 and power and permitting, not demand, kill many of these projects.",
   "asof": "2026-08-21",
   "source": "JLL / CBRE pipeline data; project cancellation reporting"
  },
  "C1": {
   "state": 1,
   "value": ">$3tn committed off balance sheet",
   "detail": "Analysis of nine large technology companies puts more than $3tn in off-balance-sheet commitments \u2014 leases, energy contracts, hardware obligations \u2014 much of it tied to AI infrastructure. The visible capex line understates the economic commitment already made.",
   "asof": "2026-08-21",
   "source": "Wall Street Journal analysis of off-balance-sheet commitments"
  },
  "C3": {
   "state": 1,
   "value": "5-6 year useful lives, group no longer aligned",
   "detail": "Server useful lives were extended from three or four years to five or six, worth roughly $18bn a year in avoided depreciation. Critics estimate $176bn of understated depreciation across 2026-2028 if true economic life is nearer three years. Amazon has shortened life on a subset of servers while Meta extended further \u2014 the group is no longer moving in one direction, which is what makes this a watch rather than a calm.",
   "asof": "2026-08-21",
   "source": "10-K and 10-Q useful-life disclosures; depreciation debate coverage"
  },
  "C4": {
   "state": 0,
   "value": "growing, structures still clean",
   "detail": "AI startup funding volume still growing in dollar terms. Watch for structure appearing \u2014 ratchets, preference stacks, compute credits substituting for cash \u2014 before volume falls.",
   "asof": "2026-08-21",
   "source": "Quarterly venture funding trackers"
  },
  "D1": {
   "state": 1,
   "value": "units down, revenue up",
   "detail": "IDC describes the disconnect directly: PC shipments falling while revenue rises as manufacturers pass memory costs through. The disguise Rule 03 exists for is already in place. Not yet at the two-consecutive-quarters, minus-5% threshold.",
   "asof": "2026-08-21",
   "source": "IDC / Canalys quarterly shipment trackers"
  },
  "D4": {
   "state": 0,
   "value": "expanding",
   "detail": "No reported contraction or non-renewal wave at the large enterprise AI vendors. The hardest sensor on the board to observe from outside \u2014 qualitative evidence scores watch at most, never turning on its own.",
   "asof": "2026-08-21",
   "source": "Vendor results, net revenue retention disclosures"
  }
 },
 "errors": []
};
window.CAPEX_HISTORY = [
 {
  "date": "2026-08-21",
  "states": {
   "A2": 1,
   "A1": 0,
   "A3": 0,
   "D3": 1,
   "C2": 0,
   "D2": 1,
   "B4": 1,
   "A4": 0,
   "B2": 0,
   "B3": 1,
   "C1": 1,
   "C3": 1,
   "C4": 0,
   "D1": 1,
   "D4": 0
  }
 }
];
