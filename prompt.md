# AI Exposure of the Finnish Job Market

This document contains structured data on 1184 Finnish occupations from Statistics Finland PxWeb and Occupational Barometer, each scored for AI exposure on a 0-10 scale by an LLM (Gemini Flash). Use this data to analyze, question, and discuss how AI will reshape the Finnish labor market.

Live visualization: https://github.com/karpathy/jobs
GitHub: https://github.com/karpathy/jobs

## Scoring methodology

Each occupation was scored on a single AI Exposure axis from 0 to 10, measuring how much AI will reshape that occupation. The score considers both direct automation (AI doing the work) and indirect effects (AI making workers so productive that fewer are needed).

A key heuristic: if the job can be done entirely from a home office on a computer — writing, coding, analyzing, communicating — then AI exposure is inherently high (7+), because AI capabilities in digital domains are advancing rapidly. Conversely, jobs requiring physical presence, manual skill, or real-time human interaction have a natural barrier.

Calibration anchors:
- 0-1 Minimal: roofers, janitors, construction laborers
- 2-3 Low: electricians, plumbers, firefighters, dental hygienists
- 4-5 Moderate: registered nurses, police officers, veterinarians
- 6-7 High: teachers, managers, accountants, journalists
- 8-9 Very high: software developers, graphic designers, translators, paralegals
- 10 Maximum: data entry clerks, telemarketers

## Aggregate statistics

- Total occupations: 1184
- Total jobs: 13,991,415 (14M)
- Total annual wages: €0.5T
- Job-weighted average AI exposure: 5.3/10

### Breakdown by exposure tier

| Tier | Occupations | Jobs | % of jobs | Wages | % of wages | Avg pay |
|------|-------------|------|-----------|-------|------------|---------|
| Minimal (0-1) | 26 | 81K | 0.6% | $0.0T | 0.5% | €32,160 |
| Low (2-3) | 25 | 95K | 0.7% | $0.0T | 0.6% | €34,873 |
| Moderate (4-5) | 27 | 205K | 1.5% | $0.0T | 1.4% | €36,143 |
| High (6-7) | 29 | 219K | 1.6% | $0.0T | 1.7% | €41,277 |
| Very high (8-10) | 40 | 187K | 1.3% | $0.0T | 2.1% | €57,121 |

### Average exposure by pay band (job-weighted)

| Pay band | Avg exposure | Jobs |
|----------|-------------|------|
| <€35K | 3.0 | 253K |
| €35-50K | 5.8 | 376K |
| €50-75K | 7.7 | 106K |
| €75-100K | 9.2 | 25K |
| €100K+ | 9.0 | 14K |

### Average exposure by education level (job-weighted)

| Education | Avg exposure | Jobs |
|-----------|-------------|------|
| No degree / Upper secondary | 4.4 | 628K |
| Bachelor's | 8.7 | 149K |
| Master's | 8.0 | 2K |
| Doctoral / Professional | 10.0 | 8K |

### Declining occupations (negative outlook)

| Occupation | Exposure | Outlook | Jobs |
|-----------|----------|---------|------|
| 9411 Fast food preparers (Level 4) | 1/10 | -6% | 7K |
| 9629 Elementary workers not elsewhere classified (Level 4) | 1/10 | -6% | 2K |
| 9612 Refuse sorters (Level 4) | 1/10 | -6% | 1K |
| 9211 Crop farm labourers (Level 4) | 1/10 | -6% | 571 |
| 9622 Odd job persons (Level 4) | 1/10 | -6% | 264 |
| 9520 Street vendors (excluding food) (Level 4) | 1/10 | -6% | 20 |
| 9333 Freight handlers (Level 4) | 0/10 | -6% | 39K |
| 9333. Freight handlers (Level 5) | None/10 | -6% | 39K |
| 9411. Fast food preparers (Level 5) | None/10 | -6% | 7K |
| 9313 Building construction labourers (Level 4) | None/10 | -6% | 3K |
| 9313. Building construction labourers (Level 5) | None/10 | -6% | 3K |
| 9629. Elementary workers not elsewhere classified (Level 5) | None/10 | -6% | 2K |
| 9612. Refuse sorters (Level 5) | None/10 | -6% | 1K |
| 9211. Crop farm labourers (Level 5) | None/10 | -6% | 571 |
| 9622. Odd job persons (Level 5) | None/10 | -6% | 264 |
| 9520. Street vendors (excluding food) (Level 5) | None/10 | -6% | 20 |
| 9311 Mining and quarrying labourers (Level 4) | None/10 | -6% | 4 |
| 9311. Mining and quarrying labourers (Level 5) | None/10 | -6% | 4 |
| 0110 Commissioned armed forces officers (Level 4) | 4/10 | -5% | 5K |
| 0210 Non-commissioned armed forces officers (Level 4) | 4/10 | -5% | 3K |
| 0310 Armed forces occupations, other ranks (Level 4) | 3/10 | -5% | 176 |
| 9412 Kitchen helpers (Level 4) | 1/10 | -5% | 18K |
| 9621 Messengers, package deliverers and luggage porters (Level 4) | 1/10 | -5% | 3K |
| 9329 Manufacturing labourers not elsewhere classified (Level 4) | 1/10 | -5% | 2K |
| 9334 Shelf fillers (Level 4) | 1/10 | -5% | 803 |
| 9215 Forestry labourers (Level 4) | 1/10 | -5% | 314 |
| 9214 Garden and horticultural labourers (Level 4) | 1/10 | -5% | 265 |
| 9129 Other cleaning workers (Level 4) | 1/10 | -5% | 148 |
| 9212 Livestock farm labourers (Level 4) | 1/10 | -5% | 22 |
| 9213 Mixed crop and livestock farm labourers (Level 4) | 1/10 | -5% | 11 |
| 932.  (Not more specifically classified) Manufacturing labourers (Level 4) | 1/10 | -5% | 0 |
| 961.  (Not more specifically classified) Refuse workers (Level 4) | 1/10 | -5% | 0 |
| 9112 Cleaners and helpers in offices, hotels and other establishments (Level 4) | None/10 | -5% | 70K |
| 91121 Office cleaners, etc. (Level 5) | None/10 | -5% | 39K |
| 91123 Hospital and institutional helpers (Level 5) | None/10 | -5% | 22K |
| 9412. Kitchen helpers (Level 5) | None/10 | -5% | 18K |
| 931 Mining and construction labourers (Level 3) | None/10 | -5% | 8K |
| 0110. Commissioned armed forces officers (Level 5) | None/10 | -5% | 5K |
| 91124 Kindergarten assistants (Level 5) | None/10 | -5% | 5K |
| 9312 Civil engineering labourers (Level 4) | None/10 | -5% | 5K |
| 9312. Civil engineering labourers (Level 5) | None/10 | -5% | 5K |
| 0210. Non-commissioned armed forces officers (Level 5) | None/10 | -5% | 3K |
| 91129 Other cleaners not elsewhere classified (Level 5) | None/10 | -5% | 3K |
| 9621. Messengers, package deliverers and luggage porters (Level 5) | None/10 | -5% | 3K |
| 932 Manufacturing labourers (Level 3) | None/10 | -5% | 2K |
| 9329. Manufacturing labourers not elsewhere classified (Level 5) | None/10 | -5% | 2K |
| 961 Refuse workers (Level 3) | None/10 | -5% | 2K |
| 91122 Hotel cleaners (Level 5) | None/10 | -5% | 1K |
| 921 Agricultural, forestry and fishery labourers (Level 3) | None/10 | -5% | 1K |
| 95 Street and related sales and service workers (Level 2) | None/10 | -5% | 1K |
| 9510 Street and related service workers (Level 4) | None/10 | -5% | 1K |
| 9510. Street and related service workers (Level 5) | None/10 | -5% | 1K |
| 9111 Domestic cleaners and helpers (Level 4) | None/10 | -5% | 1K |
| 9111. Domestic cleaners and helpers (Level 5) | None/10 | -5% | 1K |
| 9334. Shelf fillers (Level 5) | None/10 | -5% | 803 |
| 912 Vehicle, window, laundry and other hand cleaning workers (Level 3) | None/10 | -5% | 585 |
| 9611 Garbage and recycling collectors (Level 4) | None/10 | -5% | 504 |
| 9611. Garbage and recycling collectors (Level 5) | None/10 | -5% | 504 |
| 9321 Hand packers (Level 4) | 0/10 | -5% | 439 |
| 9321. Hand packers (Level 5) | None/10 | -5% | 439 |
| 9122 Vehicle cleaners (Level 4) | 0/10 | -5% | 397 |
| 9122. Vehicle cleaners (Level 5) | None/10 | -5% | 397 |
| 9215. Forestry labourers (Level 5) | None/10 | -5% | 314 |
| 9214. Garden and horticultural labourers (Level 5) | None/10 | -5% | 265 |
| 0310. Armed forces occupations, other ranks (Level 5) | None/10 | -5% | 176 |
| 9129. Other cleaning workers (Level 5) | None/10 | -5% | 148 |
| 9613 Sweepers and related labourers (Level 4) | None/10 | -5% | 113 |
| 9613. Sweepers and related labourers (Level 5) | None/10 | -5% | 113 |
| 9623 Meter readers and vending-machine collectors (Level 4) | None/10 | -5% | 88 |
| 9623. Meter readers and vending-machine collectors (Level 5) | None/10 | -5% | 88 |
| 9123 Window cleaners (Level 4) | 0/10 | -5% | 40 |
| 9123. Window cleaners (Level 5) | None/10 | -5% | 40 |
| 9212. Livestock farm labourers (Level 5) | None/10 | -5% | 22 |
| 9332 Drivers of animal-drawn vehicles and machinery (Level 4) | None/10 | -5% | 12 |
| 9332. Drivers of animal-drawn vehicles and machinery (Level 5) | None/10 | -5% | 12 |
| 9213. Mixed crop and livestock farm labourers (Level 5) | None/10 | -5% | 11 |
| 9216 Fishery and aquaculture labourers (Level 4) | 0/10 | -5% | 4 |
| 9216. Fishery and aquaculture labourers (Level 5) | None/10 | -5% | 4 |
| 912.  (Not more specifically classified) Vehicle, window, laundry and other hand cleaning workers (Level 4) | None/10 | -5% | 0 |
| 912.. (Not more specifically classified) Vehicle, window, laundry and other hand cleaning workers (Level 5) | None/10 | -5% | 0 |
| 921.  (Not more specifically classified) Agricultural, forestry and fishery labourers (Level 4) | 0/10 | -5% | 0 |
| 921.. (Not more specifically classified) Agricultural, forestry and fishery labourers (Level 5) | None/10 | -5% | 0 |
| 931.  (Not more specifically classified) Mining and construction labourers (Level 4) | None/10 | -5% | 0 |
| 931.. (Not more specifically classified) Mining and construction labourers (Level 5) | None/10 | -5% | 0 |
| 932.. (Not more specifically classified) Manufacturing labourers (Level 5) | None/10 | -5% | 0 |
| 9331 Hand and pedal vehicle drivers (Level 4) | None/10 | -5% | 0 |
| 9331. Hand and pedal vehicle drivers (Level 4) | None/10 | -5% | 0 |
| 95..  (Not more specifically classified) Street and related sales and service workers (Level 4) | None/10 | -5% | 0 |
| 95... (Not more specifically classified) Street and related sales and service workers (Level 5) | None/10 | -5% | 0 |
| 961.. (Not more specifically classified) Refuse workers (Level 5) | None/10 | -5% | 0 |
| 9624 Water and firewood collectors (Level 4) | None/10 | -5% | 0 |
| 9624. Water and firewood collectors (Level 5) | None/10 | -5% | 0 |

### Fastest-growing occupations (10%+ projected growth)

| Occupation | Exposure | Outlook | Jobs |
|-----------|----------|---------|------|
| 1120 Managing directors and chief executives (Level 4) | None/10 | +10% | 3K |
| 1120. Managing directors and chief executives (Level 5) | None/10 | +10% | 3K |

## All 1184 occupations

Sorted by AI exposure (descending), then by number of jobs (descending).

### Exposure 10/10 (5 occupations, 28K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 2149 Engineering professionals not elsewhere classified (Level 4) | €60,888 | 14K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 2 | 2211 Generalist medical practitioners (Level 4) | €95,340 | 8K | +9% | Doctoral | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 3 | 2153 Telecommunications engineers (Level 4) | €62,952 | 3K | +7% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 4 | 2514 Applications programmers (Level 4) | €54,852 | 3K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 5 | 2356 Information technology trainers (Level 4) | €48,624 | 158 | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |

### Exposure 9/10 (28 occupations, 140K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 2342 Early childhood educators (Level 4) | €38,772 | 23K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 2 | 2422 Policy administration professionals (Level 4) | €55,956 | 21K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 3 | 2212 Specialist medical practitioners (Level 4) | €105,708 | 14K | +8% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 4 | 2359 Teaching professionals not elsewhere classified (Level 4) | €43,164 | 12K | +4% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 5 | 1321 Manufacturing managers (Level 4) | €95,820 | 7K | +8% | Bachelor's | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 6 | 4229 Client information workers not elsewhere classified (Level 4) | €36,552 | 6K | +1% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 7 | 4323 Transport clerks (Level 4) | €44,892 | 6K | +1% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 8 | 4321 Stock clerks (Level 4) | €41,580 | 6K | +1% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 9 | 2221 Nursing professionals (Level 4) | €50,376 | 6K | +8% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 10 | 4313 Payroll clerks (Level 4) | €37,548 | 5K | +2% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 11 | 4225 Enquiry clerks (Level 4) | €34,800 | 5K | +2% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 12 | 1211 Finance managers (Level 4) | €97,776 | 4K | +8% | Bachelor's | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 13 | 2269 Health professionals not elsewhere classified (Level 4) | €55,356 | 4K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 14 | 1345 Education managers (Level 4) | €77,832 | 4K | +5% | Bachelor's | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 15 | 4411 Library clerks (Level 4) | €32,868 | 3K | +2% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 16 | 2619 Legal professionals not elsewhere classified (Level 4) | ? | 3K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 17 | 2636 Religious professionals (Level 4) | €50,700 | 3K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 18 | 2354 Other music teachers (Level 4) | €41,988 | 3K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 19 | 4416 Personnel clerks (Level 4) | €39,000 | 2K | +1% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 20 | 2355 Other arts teachers (Level 4) | €35,124 | 2K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 21 | 2651 Visual artists (Level 4) | €39,612 | 979 | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 22 | 4322 Production clerks (Level 4) | €38,268 | 597 | +2% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 23 | 2114 Geologists and geophysicists (Level 4) | ? | 512 | +7% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 24 | 2353 Other language teachers (Level 4) | €44,400 | 325 | +5% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 25 | 4132 Data entry clerks (Level 4) | €33,720 | 154 | +1% | Upper sec | This clerical occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 26 | 1322 Mining managers (Level 4) | €105,000 | 145 | +7% | Bachelor's | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 27 | 226.  (Not more specifically classified) Other health professionals (Level 4) | ? | 0 | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 28 | 235.  (Not more specifically classified) Other teaching professionals (Level 4) | ? | 0 | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |

### Exposure 8/10 (7 occupations, 19K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 2423 Personnel and careers professionals (Level 4) | €54,348 | 10K | +6% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 2 | 2132 Farming, forestry and fisheries advisers (Level 4) | €47,412 | 3K | +8% | Bachelor's | This professional occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 3 | 1114 Senior officials of special-interest organizations (Level 4) | €66,552 | 2K | +6% | Bachelor's | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 4 | 1412 Restaurant managers (Level 4) | €54,660 | 2K | +3% | Upper sec | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 5 | 1112 Senior government officials (Level 4) | €96,012 | 2K | +5% | Master's | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 6 | 1411 Hotel managers (Level 4) | €65,280 | 379 | +3% | Upper sec | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |
| 7 | 1111 Legislators (Level 4) | €86,016 | 286 | +5% | Master's | This managerial occupation involves extensive digital knowledge work and analytical tasks that are highly susceptible to AI automation and augmentation. The work is primarily computer-based with limited physical requirements, making it highly exposed to AI capabilities. |

### Exposure 7/10 (5 occupations, 33K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 4120 Secretaries (general) (Level 4) | €37,440 | 27K | +2% | Upper sec | This clerical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 2 | 4419 Clerical support workers not elsewhere classified (Level 4) | €39,336 | 4K | +2% | Upper sec | This clerical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 3 | 4223 Telephone switchboard operators (Level 4) | €33,336 | 1K | +2% | Upper sec | This clerical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 4 | 3151 Ships' engineers (Level 4) | €75,180 | 367 | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 5 | 4213 Pawnbrokers and money-lenders (Level 4) | €37,224 | 133 | +1% | Upper sec | This clerical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |

### Exposure 6/10 (24 occupations, 186K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 3221 Nursing associate professionals (Level 4) | €42,444 | 75K | +5% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 2 | 3412 Social work associate professionals (Level 4) | €38,472 | 34K | +3% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 3 | 3313 Accounting associate professionals (Level 4) | €41,640 | 21K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 4 | 3344 Medical secretaries (Level 4) | €33,348 | 7K | +3% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 5 | 3353 Government social benefits officials (Level 4) | €38,460 | 7K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 6 | 3122 Manufacturing supervisors (Level 4) | €51,180 | 6K | +5% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 7 | 3413 Religious associate professionals (Level 4) | €37,368 | 5K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 8 | 3341 Office supervisors (Level 4) | €50,172 | 5K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 9 | 3321 Insurance representatives (Level 4) | €53,496 | 5K | +5% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 10 | 3258 Ambulance workers (Level 4) | €49,056 | 4K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 11 | 3259 Health associate professionals not elsewhere classified (Level 4) | €37,692 | 3K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 12 | 3222 Midwifery associate professionals (Level 4) | €47,292 | 2K | +6% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 13 | 3118 Draughtspersons (Level 4) | €42,888 | 2K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 14 | 3324 Trade brokers (Level 4) | €49,200 | 2K | +3% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 15 | 3342 Legal secretaries (Level 4) | €36,420 | 2K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 16 | 3139 Process control technicians not elsewhere classified (Level 4) | €55,776 | 1K | +3% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 17 | 3354 Government licensing officials (Level 4) | €37,476 | 1K | +3% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 18 | 3143 Forestry technicians (Level 4) | €45,768 | 1K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 19 | 3514 Web technicians (Level 4) | €51,396 | 1K | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 20 | 3135 Metal production process controllers (Level 4) | ? | 881 | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 21 | 3133 Chemical processing plant controllers (Level 4) | €48,780 | 740 | +3% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 22 | 3121 Mining supervisors (Level 4) | €57,912 | 273 | +6% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 23 | 3359 Regulatory government associate professionals not elsewhere classified (Level 4) | €52,224 | 268 | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |
| 24 | 3230 Traditional and complementary medicine associate professionals (Level 4) | ? | 94 | +4% | Upper sec | This technical occupation has significant AI exposure due to substantial digital and analytical components. While some aspects involve human judgment or physical presence, many core tasks can be automated or augmented by AI systems, particularly administrative and routine decision-making functions. |

### Exposure 5/10 (4 occupations, 18K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 3123 Construction supervisors (Level 4) | €55,620 | 10K | +5% | Upper sec | This technical occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 2 | 8344 Lifting truck operators (Level 4) | €48,960 | 4K | +4% | Upper sec | This machine operation occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 3 | 8219 Assemblers not elsewhere classified (Level 4) | €34,152 | 3K | +3% | Upper sec | This machine operation occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 4 | 8111 Miners and quarriers (Level 4) | €50,280 | 1K | +3% | Upper sec | This machine operation occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |

### Exposure 4/10 (23 occupations, 186K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 5223 Shop sales assistants (Level 4) | €33,660 | 103K | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 2 | 5312 Teachers' aides (Level 4) | €29,760 | 19K | +3% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 3 | 5222 Shop supervisors (Level 4) | €40,836 | 13K | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 4 | 8211 Mechanical machinery assemblers (Level 4) | €36,960 | 12K | +3% | Upper sec | This machine operation occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 5 | 5221 Shop keepers (Level 4) | €46,200 | 8K | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 6 | 5244 Contact centre salespersons (Level 4) | €32,040 | 6K | +3% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 7 | 0110 Commissioned armed forces officers (Level 4) | €66,408 | 5K | -5% | Bachelor's+ | This armed forces occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 8 | 5411 Fire-fighters (Level 4) | €47,544 | 4K | +3% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 9 | 5412 Police officers (Level 4) | ? | 4K | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 10 | 0210 Non-commissioned armed forces officers (Level 4) | €51,036 | 3K | -5% | Bachelor's+ | This armed forces occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 11 | 5413 Prison guards (Level 4) | €41,796 | 2K | +3% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 12 | 8311 Locomotive engine drivers (Level 4) | ? | 1K | +3% | Upper sec | This machine operation occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 13 | 5245 Service station attendants (Level 4) | €31,344 | 1K | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 14 | 5242 Sales demonstrators (Level 4) | €40,236 | 1K | +3% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 15 | 5112 Transport conductors (Level 4) | ? | 857 | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 16 | 5165 Driving instructors (Level 4) | €39,144 | 838 | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 17 | 5152 Domestic housekeepers (Level 4) | ? | 675 | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 18 | 5211 Stall and market salespersons (Level 4) | ? | 612 | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 19 | 5163 Undertakers and embalmers (Level 4) | €35,340 | 602 | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 20 | 5243 Door to door salespersons (Level 4) | ? | 204 | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 21 | 8321 Motorcycle drivers (Level 4) | ? | 4 | +3% | Upper sec | This machine operation occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 22 | 521.  (Not more specifically classified) Street and market salespersons (Level 4) | ? | 0 | +2% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |
| 23 | 5212 Street food salespersons (Level 4) | ? | 0 | +3% | Upper sec | This service occupation has moderate AI exposure. While some tasks (particularly administrative and routine aspects) are susceptible to automation, the role requires physical presence, manual skills, or interpersonal interaction that provides a buffer against full automation. |

### Exposure 3/10 (15 occupations, 70K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 7111 House builders (Level 4) | €39,384 | 37K | +4% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 2 | 5153 Building caretakers (Level 4) | €35,124 | 26K | +3% | Upper sec | This service occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 3 | 7322 Printers (Level 4) | €37,848 | 2K | +4% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 4 | 7543 Product graders and testers (excluding foods and beverages) (Level 4) | €40,176 | 1K | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 5 | 7531 Tailors, dressmakers, furriers and hatters (Level 4) | €33,768 | 991 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 6 | 7521 Wood treaters (Level 4) | €36,672 | 632 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 7 | 7321 Pre-press technicians (Level 4) | €36,084 | 579 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 8 | 7123 Plasterers (Level 4) | €42,672 | 552 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 9 | 0310 Armed forces occupations, other ranks (Level 4) | €32,616 | 176 | -5% | Upper sec | This armed forces occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 10 | 7542 Shotfirers and blasters (Level 4) | €48,816 | 169 | +4% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 11 | 7535 Pelt dressers, tanners and fellmongers (Level 4) | ? | 104 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 12 | 7513 Dairy-products makers (Level 4) | €48,696 | 91 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 13 | 7215 Riggers and cable splicers (Level 4) | €29,844 | 26 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 14 | 7541 Underwater divers (Level 4) | ? | 26 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 15 | 732.  (Not more specifically classified) Printing trades workers (Level 4) | ? | 0 | +3% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |

### Exposure 2/10 (10 occupations, 25K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 6111 Field crop and vegetable growers (Level 4) | €29,136 | 12K | +3% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 2 | 5141 Hairdressers (Level 4) | €28,164 | 11K | +3% | Upper sec | This service occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 3 | 6129 Animal producers not elsewhere classified (Level 4) | ? | 1K | +2% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 4 | 6122 Poultry producers (Level 4) | €30,696 | 702 | +2% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 5 | 6221 Aquaculture workers (Level 4) | €36,612 | 352 | +2% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 6 | 6224 Hunters and trappers (Level 4) | ? | 81 | +3% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 7 | 7316 Sign writers, decorative painters, engravers and etchers (Level 4) | €36,624 | 29 | +4% | Upper sec | This craft occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 8 | 6112 Tree and shrub crop growers (Level 4) | ? | 13 | +2% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 9 | 6114 Mixed crop growers (Level 4) | ? | 10 | +2% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |
| 10 | 6123 Apiarists and sericulturists (Level 4) | ? | 7 | +3% | Upper sec | This agricultural occupation has low AI exposure. The work is primarily physical and hands-on, requiring manual dexterity, real-time physical coordination, or outdoor work in unpredictable environments. AI's impact is limited to peripheral support functions. |

### Exposure 1/10 (20 occupations, 41K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 9412 Kitchen helpers (Level 4) | €28,788 | 18K | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 2 | 9411 Fast food preparers (Level 4) | €27,792 | 7K | -6% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 3 | 6113 Gardeners, horticultural and nursery growers (Level 4) | €29,916 | 6K | +3% | Upper sec | This agricultural occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 4 | 9621 Messengers, package deliverers and luggage porters (Level 4) | €32,400 | 3K | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 5 | 9329 Manufacturing labourers not elsewhere classified (Level 4) | €39,864 | 2K | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 6 | 9629 Elementary workers not elsewhere classified (Level 4) | €31,428 | 2K | -6% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 7 | 9612 Refuse sorters (Level 4) | €34,380 | 1K | -6% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 8 | 9334 Shelf fillers (Level 4) | €30,708 | 803 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 9 | 9211 Crop farm labourers (Level 4) | €23,880 | 571 | -6% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 10 | 9215 Forestry labourers (Level 4) | €31,968 | 314 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 11 | 9214 Garden and horticultural labourers (Level 4) | €25,308 | 265 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 12 | 9622 Odd job persons (Level 4) | €27,504 | 264 | -6% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 13 | 9129 Other cleaning workers (Level 4) | ? | 148 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 14 | 7319 Handicraft workers not elsewhere classified (Level 4) | €29,844 | 53 | +3% | Upper sec | This craft occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 15 | 9212 Livestock farm labourers (Level 4) | ? | 22 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 16 | 9520 Street vendors (excluding food) (Level 4) | ? | 20 | -6% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 17 | 9213 Mixed crop and livestock farm labourers (Level 4) | €25,920 | 11 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 18 | 731.  (Not more specifically classified) Handicraft workers (Level 4) | ? | 0 | +3% | Upper sec | This craft occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 19 | 932.  (Not more specifically classified) Manufacturing labourers (Level 4) | ? | 0 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 20 | 961.  (Not more specifically classified) Refuse workers (Level 4) | ? | 0 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |

### Exposure 0/10 (6 occupations, 40K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | 9333 Freight handlers (Level 4) | €34,872 | 39K | -6% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 2 | 9321 Hand packers (Level 4) | €31,836 | 439 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 3 | 9122 Vehicle cleaners (Level 4) | €30,552 | 397 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 4 | 9123 Window cleaners (Level 4) | ? | 40 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 5 | 9216 Fishery and aquaculture labourers (Level 4) | ? | 4 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
| 6 | 921.  (Not more specifically classified) Agricultural, forestry and fishery labourers (Level 4) | ? | 0 | -5% | Basic | This elementary occupation has minimal AI exposure. The work is almost entirely physical, requiring hands-on skills, manual labor, or real-time physical interaction with the environment. These tasks cannot be meaningfully automated by current or near-term AI technologies. |
