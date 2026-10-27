# Prep data for AI on the Supplier Invoice Assurance model (manual, about 15 minutes)

| | |
|---|---|
| **Date** | 23 October 2026 |
| **Input** | Semantic model *Supplier Invoice Assurance* (workspace *Caldova Finance*), demo prompts from [Demo-Runbook.md](Demo-Runbook.md) |
| **Scope** | What you set by hand in the Power BI service so Copilot Chat and Cowork read the model the way the demo needs: AI instructions, AI data schema, Approved for Copilot. Prep data for AI is in **preview**. |

**Why.** "Fabric IQ uses the measures, relationships, and business definitions in your semantic model to answer questions." When a model has "organization-specific terminology, preferred analytical defaults, or potential ambiguities, use Prep data for AI to provide more context." ([Ask data questions with Copilot and Fabric IQ](https://learn.microsoft.com/power-bi/create-reports/copilot-ask-data-question)) This model has three:

- **"Last 4 weeks"** must mean 28 Sep – 23 Oct 2026 (the data ends on Friday 23 Oct), not the calendar month.
- **"What AP will block"** must be *Payments to Block* (Germany $147K), not *Overbilled Not Yet Paid* or *Amount at Risk* (both Germany $16.5K).
- **"Why"** questions must show prices and dates, not guesses. The real reason is in Colin's emails (Work IQ), not in the data.

## Before you start

- Sign in to Power BI as an Admin of the *Caldova Finance* workspace, for example the account that ran the deploy script.
- Your Fabric capacity must be running.
- Q&A is already on for this model. If the tabs in **Prep data for AI** are greyed out, select **Turn on Q&A**.
- Do this the day before the demo, together with the seeding. "If **Prep data for AI** features don't take effect immediately, wait a few minutes and try again." ([Prep data for AI](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai))

## Step 1: Add AI instructions

1. Open the workspace **Caldova Finance** and select the semantic model **Supplier Invoice Assurance**.
2. On the ribbon, select **Prep data for AI**, then the **Add AI instructions** tab.
3. Paste the text below (about 3,200 characters; the limit is 10,000) and select **Apply**.

```text
Business context
Caldova Pharma checks every supplier invoice line against the unit price in the contract data and the goods receipt, for six European affiliates: Germany, France, Italy, Spain, United Kingdom and Switzerland. This model answers: are we paying suppliers what the contracts say, where and since when are invoices flagged, which suppliers and invoices are affected, and what Accounts Payable will block.

Time
- Invoice data runs to Friday 23 October 2026. Later weeks in the Date table have no invoices; ignore them.
- "Recently", "lately", "the last few weeks" and "the last 4 weeks" mean 28 Sep to 23 Oct 2026, which is Date[Weeks Ago] 0 to 3.
- "The 4 weeks before" means 31 Aug to 27 Sep 2026 (Date[Weeks Ago] 4 to 7). For the comparison use [Invoice Accuracy % Previous 4 Weeks].
- Show trends by Date[Week] (each week is labelled by its Monday, for example "05 Oct") for the last 8 weeks (Date[Weeks Ago] 0 to 7) or 16 weeks (0 to 15). Use months or quarters only when the user asks for them.

Terminology and metric routing
- Overbilled, overcharged, leakage or flagged amount = [Overbilled Amount]. As a share of the invoiced amount = [Overbilling %].
- Invoice accuracy = [Invoice Accuracy %]: the share of invoices with no error, counted by invoice, not by value.
- Flagged or wrong invoices = [Invoices with Errors]. Invoices checked = [Invoices].
- What Accounts Payable (AP) will block, payments on hold or payments at risk = [Payments to Block] (full value of unpaid invoices with an error) and [Invoices to Block]. Use only these two measures for this question.
- Contract price = 'Invoice Lines'[Contract Unit Price], the price in the contract data. Billed price = 'Invoice Lines'[Billed Unit Price]. When the contract price was last updated = Contracts[Price Last Updated].
- Error types are in 'Error Types'[Error Type]: Price above contract, Duplicate invoice, Billed more than delivered. "No error" means the invoice line is correct.
- Country = market = affiliate = Countries[Country]. All six countries are in Countries[Region] "Europe". Supplier = Suppliers[Supplier Name].

How to answer
- Lead with one sentence, then a compact table or visual. Always state the period (for example "last 4 weeks, 28 Sep - 23 Oct 2026") and show amounts in USD.
- "Which supplier drives it": [Overbilled Amount] by Suppliers[Supplier Name] and 'Error Types'[Error Type]. For price above contract, also show the billed price, the contract price and Contracts[Price Last Updated].
- "Which invoices": Invoice Number, Invoice Date, Country, Supplier Name, Error Type, Billed Unit Price, Contract Unit Price, Overbilled Amount and Next Step, sorted by Invoice Date.
- Higher invoice accuracy is better; 95% is the gate, and weeks below it need attention. Lower overbilling is better.
- The model shows whether invoices match the contract data, not why a price differs. If asked why, show the billed price, the contract price and when the contract price was last updated, and don't guess reasons.
- Answers follow each user's row-level security. If fewer countries appear than the user expects, say that the results reflect their data access, and never guess other countries.
```

## Step 2: Simplify the data schema

1. In **Prep data for AI**, open the **Simplify data schema** tab. Hidden fields (IDs, the security table, line amounts) are already cleared: "Fields that are hidden in the semantic model are automatically excluded in the initial AI data schema when you set it up for the first time." ([AI data schemas](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-data-schema))
2. Keep everything else selected, but clear these four fields. None of them is used in the report.

| Table | Clear | Why |
|---|---|---|
| Invoice Lines | Overbilled Not Yet Paid | Sounds like "what AP will block", but it's only the overbilled part (Germany $16.5K), not what AP holds back (Germany $147K) |
| Invoice Lines | Amount at Risk | Same risk: also $16.5K for Germany |
| Invoice Lines | Recovered Amount | Credit notes already received; not part of this story |
| Date | Month Start | Duplicates *Year Month* |

3. Select **Apply**.

## Step 3: Skip verified answers for this demo

Verified answers are the third tab in **Prep data for AI**. Don't set them up for this model ([Verified answers](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-verified-answers)):

- **They aren't built for RLS.** "Row-level security (RLS) and object-level security (OLS) aren't fully supported as security features for verified answers." Colin's view depends entirely on RLS.
- **They replace the answer.** "If a match is found, Copilot returns the verified answer instead of generating a new response." The demo prompts each ask for several things; one fixed chart would cut the answer short.

## Step 4: Approve the model for Copilot and keep Copilot on for viewers

1. In the workspace **Caldova Finance**, on the semantic model **Supplier Invoice Assurance**, select **...** > **Settings**.
2. Expand **Approved for Copilot**, select the **Approved for Copilot** box, then select **Apply**. Otherwise: "Models that aren't approved for Copilot appear with warnings that the answer quality could be low." ([Standalone Copilot](https://learn.microsoft.com/power-bi/explore-reports/copilot-chat-with-data-standalone))
3. In the **Copilot** section (on the full settings page: **Explore and AI access**), leave "Allow any person with only read permissions to use AI (for example, Copilot, Microsoft's MCP tools) on this model and its related reports" **on**. It's on by default and covers "M365 Copilot Chat and Cowork". If it's off, Colin can't use Copilot on this model, and the model drops out of Copilot search for everyone, Isaac included. ([Copilot with semantic models](https://learn.microsoft.com/power-bi/create-reports/copilot-semantic-models))

## Step 5: Test (10 minutes after Step 4)

Learn's method: "Define the expected measure, grouping, date context, filters, and result for each question. Compare the responses with known, validated results." ([Ask data questions with Copilot and Fabric IQ](https://learn.microsoft.com/power-bi/create-reports/copilot-ask-data-question))

| Who · where | Ask | Copilot should use | Expect |
|---|---|---|---|
| IsaacF · Copilot Chat | Prompt 1 | Invoice Accuracy %, Invoice Accuracy % Previous 4 Weeks, Overbilled Amount; last 4 weeks | Europe 94.0% (was 99.7%), $22,155 flagged; the drop starts in the week of 5 Oct |
| IsaacF · Copilot Chat | Prompt 2 | Overbilled Amount by country, week and supplier; Payments to Block | Germany $16,525, all Annterra, $4.45 billed vs $3.95 in the contract data; AP will block $147,073 |
| ColinB · Cowork | *Summarize the Supplier Invoice Assurance report for Germany: invoice accuracy by week and the flagged invoices in the last 4 weeks.* | The same measures; RLS limits him to Germany | 71.7%; 15 Annterra invoices since 5 Oct; $16,525 flagged; $147,073 to block |
| ColinB · Cowork | *Show invoice accuracy by country for the last 4 weeks.* | RLS | Germany only, with a note that the results reflect his data access |

If an answer uses the wrong number or period, add one sentence to the AI instructions that names the exact measure or period, select **Apply**, start a new chat and ask again.

## After this

- Don't run `Deploy-CaldovaFinance.ps1 -Step model -UpdateModel` again. It stops on purpose ("service-side parts not in the repo"), so it can't overwrite these settings. `-Step load,refresh,validate` is fine.

## Sources

- https://learn.microsoft.com/power-bi/create-reports/copilot-ask-data-question
- https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai
- https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-instructions
- https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-data-schema
- https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-verified-answers
- https://learn.microsoft.com/power-bi/create-reports/copilot-semantic-models
- https://learn.microsoft.com/power-bi/explore-reports/copilot-chat-with-data-standalone
