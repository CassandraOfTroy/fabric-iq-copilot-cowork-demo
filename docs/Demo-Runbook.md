# Demo runbook: "Should we hold Annterra payments?" (25 minutes)

| | |
|---|---|
| **Date** | 27 October 2026 |
| **Input** | Semantic model and report *Supplier Invoice Assurance* (synthetic invoice data to Fri 23 Oct 2026, numbers validated with DAX), the seed file in [seed-content](../seed-content) |
| **Scope** | Everything you need to run the demo: the setup, the Prep data for AI and seeding steps, the rehearsal, the 25-minute script with exact prompts, and the clean-up |

## The story in 30 seconds

Caldova (fictional) is a pharma company that makes its medicine **Allerveo** (tablets) in its own plant. **Annterra Pharma packs the tablets for Caldova Germany**: blister strips, box and patient leaflet, ready for pharmacies. Caldova pays Annterra **per finished pack**.

On 18 September, **Charlotte**, Director of Pricing & Contracting, signed Amendment No. 1 with Annterra: **$4.45 instead of $3.95 per pack from 5 October**, in return for packing slots reserved for Allerveo every week. She told Colin and sent the price update to the team mailbox that maintains the contract data. That mailbox had just closed, so the contract data still says $3.95. Since 5 October all 15 Annterra invoices in Germany are flagged as "price above contract", and Isaac is about to tell Accounts Payable (AP) to hold them: **$147K** of correct payments, due from 4 November.

1. **Isaac**, Region Manager Europe, sees in the Power BI report and in Copilot Chat that Germany is red, all Annterra. He asks Colin: should we block Annterra?
2. **Colin**, Country Manager Germany, asks Copilot. It **investigates** (the report, only Germany, plus Colin's emails and files: Annterra is right, the data is wrong). Cowork **does the work**: the request to Laurence, a decision deck, one email to Isaac, and a 15-minute meeting with Isaac and Laurence tomorrow. Copilot **keeps watching** with a Monday briefing on all suppliers.
3. **Isaac** opens Outlook: the decision and the evidence are there. Don't block Annterra; pay on time.

**The message:** Fabric IQ shows *what*, Work IQ finds *why*, Cowork does the work, and everyone sees only the data they're allowed to see.

## Who is who

| Person (sign-in) | Role in the story | Sees in the data | In the demo |
|---|---|---|---|
| **Isaac Fielder** (IsaacF) | Region Manager Europe | All 6 countries | Power BI report and Copilot Chat; gets Colin's email with the decision and the meeting invite |
| **Colin Ballinger** (ColinB) | Country Manager Germany | **Only Germany** (row-level security) | Copilot Chat and Copilot Cowork |
| **Charlotte Waltson** (CharlotteW) | Director, Pricing & Contracting; signed the amendment | Not used | Sends one seed email (S2); cc on Colin's email to Laurence |
| **Laurence Gilbertson** (LaurenceG) | Data Analyst, registers contract prices | All countries | Gets Colin's email and the meeting invite |

Every sign-in is `<alias>@<your-tenant>.onmicrosoft.com`.

## Words you'll hear

| Word | What it means in this demo |
|---|---|
| **Allerveo** | Caldova's medicine (tablets), made in Caldova's own plant. |
| **Annterra Pharma** | The company that packs Allerveo tablets into finished packs for Caldova Germany. Caldova pays per pack. |
| **Finished pack, $4.45** | One box ready for pharmacies: blister strips with the tablets, patient leaflet, label. $4.45 is Annterra's price for packing one box (was $3.95). |
| **Amendment No. 1** | The signed price change: $4.45 per pack from 5 Oct, in return for packing slots reserved for Allerveo every week. The amendment calls them "production slots". |
| **Contract data** | Caldova's database of agreed supplier prices. Every invoice is checked against it. Laurence keeps it up to date. |
| **Accounts Payable (AP)** | The team that pays supplier invoices. It holds invoices that don't match the contract data. |
| **Flagged, held** | Flagged: the invoice price doesn't match the contract data. Held (blocked): AP doesn't pay it until it's cleared. |

**What the data knows, and what it doesn't.** The semantic model has no product column. For Annterra it shows only the supplier category ("Contract Manufacturing (OSD)"), the line description ("Finished packs, oral solid dose"), the unit ("pack") and the prices. That these are Allerveo packs, and why the price changed, is only in the signed amendment in Colin's OneDrive, which Copilot reads in prompt 4. That's the point of the demo: the report shows *what*, Colin's documents explain *why*.

## Part 1: Set up once

You need a Microsoft 365 tenant with Microsoft 365 Copilot licenses for Isaac and Colin, Copilot Cowork for Colin, and a Fabric capacity. The four personas are user accounts in that tenant.

1. Copy `config/tenant.example.json` to `config/tenant.json` (git-ignored) and fill in your tenant ID, domain, subscription, capacity and the user aliases.
2. Sign in to your tenant with a repo-local Azure CLI profile: `pwsh -File scripts/Connect-Caldova.ps1`. Check the isolation with `pwsh -File scripts/Test-TenantIsolation.ps1`.
3. Deploy: `pwsh -File scripts/Deploy-CaldovaFinance.ps1`. It creates the workspaces *Caldova Finance* (lakehouse, data, semantic model) and *Caldova Finance Insights* (report), loads the synthetic data, deploys the model and report, sets the permissions and runs the DAX checks.
4. Add **ColinB** to the **Business User** role of the model in the Power BI service (model > **Security**). Scripts never add role members.

The result:

- Colin is a Viewer on *Caldova Finance Insights* and in the *Business User* role, so he sees only Germany.
- Isaac is an Admin on both finance workspaces, so he sees every country: "RLS only restricts data access for users with **Viewer** permissions." ([Row-level security](https://learn.microsoft.com/fabric/security/service-admin-row-level-security))
- Laurence is a Contributor on *Caldova Finance*.

## Part 2: The day before (about 1 hour)

**First, start the capacity.** Copilot can't read the report while the Fabric capacity is paused. In the Azure portal, search for *Microsoft Fabric*, select your capacity, then **Resume** and **Yes**: "Content assigned to this capacity becomes available once the capacity is resumed." Resuming also restarts billing, so when you're done, select **Pause** and **Yes**. ([Pause and resume your Fabric capacity](https://learn.microsoft.com/fabric/enterprise/pause-resume)) Check it before every rehearsal.

### Step 1: Prep the model for Copilot (once, 15 minutes)

Follow [Prep-Data-for-AI.md](Prep-Data-for-AI.md): paste the AI instructions, clear four fields in the AI data schema, skip verified answers and tick *Approved for Copilot*. Without it, Copilot can mix up the $16.5K flagged with the $147K AP will block.

### Step 2: Seed Colin's OneDrive and mailbox (20 minutes)

Copilot can only find the *why* if it's in Colin's emails and files. Seed one file and two emails at least a day before the demo, so Copilot can index them, but no more than two weeks before, because the Monday briefing looks back two weeks.

- Send each email from Outlook on the web, signed in as the sender (one browser profile per person). If you can't sign in as Charlotte, send her email from an admin account; the signature still names her.
- Paste the email texts as plain text (**Ctrl+Shift+V**).

**S1. The signed amendment (file).** Sign in as ColinB. In OneDrive, open **My files**, create a folder named **Contracts** and upload `seed-content/Annterra Pharma - Caldova Germany - Contract Amendment No 1.docx`.

**S2. Charlotte to Colin, with the amendment attached.** From CharlotteW to ColinB. Attach the same amendment file.

Subject: **FW: Annterra Amendment No. 1 - please register the new price in the contract database**

```text
Hi Colin,

As discussed, here is the fully signed Amendment No. 1 with Annterra for your files. My registration request from September is below.

Best regards,
Charlotte

From: Charlotte Waltson
Sent: Monday, 21 September 2026 09:40
To: contract-admin@<your-tenant>.onmicrosoft.com
Cc: Colin Ballinger
Subject: Annterra Amendment No. 1 - please register the new price in the contract database

Hello Contract Admin team,

Please register Amendment No. 1 to the Annterra Pharma supply agreement for Caldova Germany (contract CTR-ANN-DE) in the contract database. The amended pack price applies to all deliveries from 5 October 2026, so it needs to be in the database before the first October invoices arrive. The signed amendment is attached.

Thank you,
Charlotte Waltson
Director, Pricing & Contracting
```

**S3. Finance Shared Services to Colin and Charlotte.** From an admin account to ColinB and CharlotteW.

Subject: **Reminder: contract-admin mailbox closed on 15 September - send contract price changes to Laurence Gilbertson**

```text
Dear colleagues,

A reminder: contract administration for the European affiliates moved to the Europe finance shared-service center in September. As part of this move, the contract-admin mailbox was closed on 15 September 2026. Messages sent to it after that date were not forwarded and were not processed.

From now on, send contract price changes directly to Laurence Gilbertson, Data Analyst, with the signed contract document attached. Laurence registers the price in the contract data and refreshes the Supplier Invoice Assurance model, so every report and Copilot answer uses it.

If you sent a contract change to the contract-admin mailbox after 15 September, please send it again to Laurence.

Kind regards,
Finance Shared Services Europe
```

### Step 3: Check the seed and Cowork (a few hours later, 10 minutes)

Sign in as Colin, open Copilot at copilot.cloud.microsoft (**Chat**) and ask this question. If Copilot finds nothing, wait a few hours and ask again.

- *What do my emails and files say about Annterra's contract price for Caldova Germany, and who registers contract prices now?* Expect the amendment ($4.45 from 5 Oct, signed 18 Sep), Charlotte's request to the contract-admin mailbox (21 Sep), and the reminder that the mailbox closed on 15 Sep and that Laurence now registers prices.

Then, still as Colin, select **Cowork** in the top toggle and, in the left navigation, select **Customize**. The page has three tabs: **Preferences**, **Plugins** and **Skills**. ([Customize Cowork](https://learn.microsoft.com/microsoft-365/copilot/cowork/cowork-customize))

- **Plugins** tab: **Fabric IQ** is listed under **Installed**. It's the plugin that reads Power BI reports and is "installed by default in Cowork". Open it and check that it's turned on.
- **Skills** tab: the **Built-in** list includes **PowerPoint**, **Email** and **Scheduling**, the skills prompt 5 needs.

### Which Copilot features the demo uses

A *skill* is one of Cowork's built-in capabilities, such as PowerPoint or Email. Cowork picks the skills itself. While it works it shows messages such as "Preparing to compose emails", and the **Skills** section of the panel on the right of the Cowork screen lists the skills it used. ([Use Cowork](https://learn.microsoft.com/microsoft-365/copilot/cowork/use-cowork#cowork-skills))

| Prompt | What Copilot uses | Where you see it |
|---|---|---|
| 1–3 · Isaac asks | Copilot Chat with Fabric IQ (the report, as Isaac) | Answers with numbers and charts; a draft email |
| 4 · Colin investigates | Copilot with Fabric IQ (the report, as Colin) and a search of his emails and files (Work IQ) | Short updates such as *Searching OneDrive* |
| 5 · Do the work | Cowork skills: **PowerPoint** (the deck), **Email** (both emails and the attachments), **Scheduling** (the meeting) | The deck under **Output folder**; the drafts in the approval cards |
| 6 · Keep watching | A **scheduled prompt** in Copilot Chat: every Monday it runs the same check | **... Settings and more** > **Scheduled prompts** |

### Step 4: Rehearse once (30 minutes)

Run the whole script in Part 3 once, then tidy up:

- In Colin's Copilot Chat, open **... Settings and more** > **Scheduled prompts** and delete the Monday briefing you just created. Keep the Cowork task itself: it's your backup.
- On the demo morning, delete the rehearsal email and cancel the rehearsal meeting in Isaac's and Laurence's calendars, so only the live ones show.

## Part 3: The demo (25 minutes)

**15 minutes before:**

- **Capacity:** running (Part 2, first paragraph).
- **Isaac's browser profile:** the *Supplier Invoice Assurance* report, Copilot at copilot.cloud.microsoft (**Chat**) and Outlook.
- **Colin's browser profile:** the report, Copilot at copilot.cloud.microsoft, then select **Cowork** "in the top toggle next to Chat" ([Get started with Cowork](https://learn.microsoft.com/microsoft-365/copilot/cowork/get-started)). Also open the rehearsal task as a backup.
- **Laurence's browser profile:** Outlook.
- Keep the report link at hand (open the report in *Caldova Finance Insights* and copy the URL).

#### 1 · Isaac · Power BI report, then Copilot Chat (3 minutes)

Show the report first, then ask Copilot Chat:

```text
Give me a brief executive summary of the Supplier Invoice Assurance Power BI report with visuals. How did supplier invoice accuracy and overbilling develop in the last 4 weeks compared with the 4 weeks before? Flag anything out of step.
```

- **You'll see:** Europe 94.0% (was 99.7%), $22.2K flagged; the drop starts in the week of 5 Oct.
- **Say:** "Isaac runs six countries. One question, and Copilot reads the governed Power BI report for him."

#### 2 · Isaac · Copilot Chat (2 minutes)

```text
Break it down by country and by week, and tell me which supplier drives it and what AP will block.
```

- **You'll see:** Germany $16.5K, all Annterra: $4.45 billed against $3.95 in the contract data since 5 Oct. AP will block $147K.
- **Say:** "Annterra packs our tablets, and we pay per finished pack. Since 5 Oct the data says they charge 50 cents too much per pack. Do we block them?"

Prompts 1 and 2 also work as one prompt: add "Break it down by supplier, country and by week" to prompt 1.

#### 3 · Isaac · Copilot Chat (2 minutes)

```text
Draft an Outlook email to Colin Ballinger: Annterra's German invoices have been flagged as above the contract price since 5 Oct and AP will block $147K of Annterra payments. Ask him whether we should block Annterra and to come back with his findings.
```

- **You'll see:** a draft email to Colin. Isaac reviews it and sends it.
- **Say:** "He asks the person who owns Germany."

#### 4 · Colin · Copilot: investigate (6 minutes)

```text
Isaac asks whether we should block Annterra. Check the Supplier Invoice Assurance report for Germany and my emails and files about Annterra's contract price. Is Annterra overbilling us, or is our contract data wrong? Show me the evidence.
```

Follow-up:

```text
Why didn't we register the correct price? What happened and how can we fix this?
```

- **You'll see:** Germany only: 71.7%, 15 Annterra invoices, $16.5K flagged, $147K to block. Then the evidence: the signed amendment, Charlotte's request to the closed mailbox, and the reminder that Laurence now registers prices.
- **Show:** switch to Colin's report: he sees only Germany.
- **Say:** "Same report, but Colin sees only Germany. Then Copilot finds what the data can't show: Charlotte signed the higher price to reserve Annterra's packing slots for Allerveo every week, and her request to update the data went to a closed mailbox. Annterra is right; our data is wrong."

#### 5 · Colin · Cowork: do the work (6 minutes)

```text
Prepare the Annterra decision for Isaac.
1) Create and send an Outlook email to Laurence Gilbertson now: Please register $4.45 per pack from 5 Oct 2026 for contract CTR-ANN-DE and refresh the Supplier Invoice Assurance model; attach Amendment No. 1 from my OneDrive. Add Charlotte Waltson to CC of the mail.
2) Create a 3-slide PowerPoint: what the Supplier Invoice Assurance report shows for Germany (invoice accuracy by week and the $147K AP will block), why (Amendment No. 1, signed 18 Sep: $4.45 per pack from 5 Oct; the update request went to the closed contract-admin mailbox) and the decision (don't block Annterra; Laurence registers the price).
3) Email the deck to Isaac Fielder: we should not block Annterra; the invoices match Amendment No. 1 and Laurence is registering the price today.
4) Find the available 15-minute slot tomorrow with Isaac Fielder and Laurence Gilbertson to clarify what happened.
```

- **You'll see:** Cowork drafts the email to Laurence (cc Charlotte), the deck, the email to Isaac with the deck and the meeting, and asks for approval. Before you approve, show the deck: in the panel on the right of the Cowork screen, under **Output folder**, select **Preview** (if the panel is closed, select the side panel toggle). Then check the drafts and select **Approve All**.
- **Say:** "Cowork doesn't tell Colin what to do. It does it, and he approves every action."

#### 6 · Colin · Copilot Chat: keep watching (3 minutes)

Go back to Copilot Chat (**Work IQ** tab) and send:

```text
Prepare a supplier briefing for Caldova Germany. From the Supplier Invoice Assurance report: invoice accuracy by week and any supplier with flagged invoices. From my emails and files of the last two weeks about suppliers: contract changes, price changes, open questions. Tell me what needs action.
```

Check the answer, then hover over the prompt and select **Schedule this prompt**: every Monday at 8:00, with an email notification. "Scheduled Prompts is available only in the Work IQ tab in Microsoft Copilot." ([Scheduled prompts](https://learn.microsoft.com/microsoft-365/copilot/scheduled-prompts)) If the option doesn't show, refresh the chat.

- **You'll see:** Germany at 61.5% last week, and Annterra explained, with the fix requested from Laurence.
- **Say:** "And it keeps watching. Every Monday Copilot checks the report and Colin's supplier emails for all suppliers, so the next problem like this shows up before anyone talks about blocking a supplier."

In Cowork you can schedule the same check by putting the timing into the message: "Every Monday at 8:00, send me a supplier briefing for Caldova Germany. [...] Run the first one now." The schedules are under **Automations** > **Manage schedules** ([Use Cowork](https://learn.microsoft.com/microsoft-365/copilot/cowork/use-cowork)).

#### 7 · Isaac and Laurence · Outlook (3 minutes)

Open Isaac's inbox, then Colin's email and the deck. Then show the invite for tomorrow's 15-minute meeting, in Isaac's and Laurence's calendars.

- **You'll see:** Colin's email with the deck (what, why, decision) and the meeting invite.
- **Say:** "Isaac gets the decision and the evidence. Don't block Annterra: pay the $147K on time. Fabric IQ showed *what*, Work IQ found *why*, and Cowork did the work, each person only with the data they may see."

### If something goes wrong

| Problem | Do this |
|---|---|
| Copilot can't open the report, or nothing loads | The capacity is paused: resume it (Part 2, first paragraph). |
| Copilot doesn't find the report | Paste the report link into the prompt: "paste a direct report link, attach the report, or name it in the prompt." ([Fabric IQ in Microsoft 365 Copilot](https://learn.microsoft.com/fabric/iq/connectors/microsoft-365-copilot-overview)) |
| Copilot calls Annterra a "contract manufacturer" | That's the supplier category label in the data; packing counts as contract manufacturing. Optional: in **Prep data for AI** > **Simplify data schema**, also clear *Suppliers* > *Supplier Category*. |
| Copilot says AP will block $16.5K, or uses the wrong period | Prep data for AI isn't applied: check Part 2, Step 1, then start a new chat. |
| Colin sees all countries | Colin has a role on the *Caldova Finance* workspace, or he isn't in the *Business User* role. |
| Copilot finds no amendment or emails | The seed isn't indexed yet: wait and ask again (Part 2, Step 3). |
| Cowork doesn't use the Power BI report | Check that the **Fabric IQ** plugin is on (Part 2, Step 3), or paste the report link into the prompt. |
| Cowork is slow | Switch to the rehearsal task and walk through its results. |
| The email to Isaac has no deck attached | In the same task, ask: *Attach the deck you created to the email to Isaac.* |
| The briefing doesn't mention Annterra | Ask: *Which suppliers have flagged invoices, and what's still open on Annterra?* |
| Copilot Chat shows only draft text for Isaac's email | Copy it into a new Outlook email to Colin and send it. |

## Part 4: After the demo

- In Colin's Copilot Chat, delete the Monday briefing under **... Settings and more** > **Scheduled prompts**. Otherwise Colin gets one every Monday.
- Pause the capacity in the Azure portal (**Pause**, **Yes**) to stop billing.
- Optional, if someone asks to see Germany back to 100%: run `pwsh -File scripts/Update-CaldovaContractPrice.ps1 -Contract CTR-ANN-DE -UnitPrice 4.45 -ValidFrom 2026-10-05`. It takes about 2 minutes and stands in for Laurence's fix. Before the next rehearsal, run `pwsh -File scripts/Update-CaldovaContractPrice.ps1 -Reset`.

## The numbers on screen (last 4 weeks = 28 Sep – 23 Oct 2026)

| | Isaac (all of Europe) | Colin (Germany only) |
|---|---|---|
| Invoice accuracy | 94.0% (99.7% in the 4 weeks before) | **71.7%** (100% before): 15 of 53 invoices flagged |
| By week | 98–100%, then 93%, 94%, 91% | 100%, then **64%, 62%, 62%** (weeks of 5, 12 and 19 Oct) |
| Flagged as overbilled | $22,155 (Germany $16.5K, Switzerland $2.9K, Italy $1.7K, France $0.8K, Spain $0.2K) | **$16,525**, all Annterra |
| Payments AP will block | $167,893 (19 invoices) | **$147,073** (15 Annterra invoices; the first is due on 4 Nov) |

**Where $147,073 comes from.** It's the measure *Payments to Block*: the full invoiced amount of every invoice whose next step is "Block payment". For Germany that's the 15 Annterra invoices from 5 to 23 Oct: 33,050 packs × $4.45 = $147,073, which is $130,548 at the old contract price plus $16,525 difference. None is paid yet; they're due from 4 to 22 Nov.

## Why each person sees what they see

Both Copilots query Power BI as the signed-in user. Copilot Chat: "Copilot uses the user's existing permissions, including row-level security (RLS) and object-level security (OLS), to access the data." ([Fabric IQ in Microsoft 365 Copilot](https://learn.microsoft.com/fabric/iq/connectors/microsoft-365-copilot-overview)) Cowork: "Queries run against Power BI as you, so existing item permissions and row-level security (RLS) continue to apply." ([Fabric IQ plugin in Copilot Cowork](https://learn.microsoft.com/fabric/iq/connectors/cowork-overview))

Cowork's Fabric IQ plugin "is installed by default in Cowork" and works with reports: "It doesn't currently ground on Power BI dashboards." That's why every Cowork prompt names the *report*. ([Fabric IQ plugin in Copilot Cowork](https://learn.microsoft.com/fabric/iq/connectors/cowork-overview))

## Sources

- https://learn.microsoft.com/fabric/iq/connectors/microsoft-365-copilot-overview
- https://learn.microsoft.com/fabric/iq/connectors/cowork-overview
- https://learn.microsoft.com/fabric/security/service-admin-row-level-security
- https://learn.microsoft.com/microsoft-365/copilot/cowork/get-started
- https://learn.microsoft.com/microsoft-365/copilot/cowork/use-cowork
- https://learn.microsoft.com/microsoft-365/copilot/cowork/cowork-customize
- https://learn.microsoft.com/microsoft-365/copilot/scheduled-prompts
- https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai
- https://learn.microsoft.com/fabric/enterprise/pause-resume
