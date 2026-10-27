Source: https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-instructions
Fetched: 2026-10-13

# Prepare your data for AI: AI instructions

Table of contents 

Exit editor mode

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Prepare your data for AI: AI instructions

AI instructions allow semantic model authors to provide context, business logic, and specific guidance directly on a semantic model. Copilot uses these instructions to better interpret user questions by incorporating organizational language, terminology, and analytical priorities. This article walks you through the steps to set up and test AI instructions to prepare your data for AI-powered analysis.

AI instructions help clarify business terms, guide analysis approaches, and reduce ambiguity. They improve the quality and relevance of Copilot responses, leading to more meaningful insights and a smoother experience across reports that use the same model.

## Prerequisites

- A Power BI semantic model in Power BI Desktop or the Power BI service.
- [Copilot enabled](copilot-introduction) for your organization.
- Power BI Q&A enabled for the model. You can enable Q&A during setup if it isn't already on.

## Set up AI instructions

Note

You can author **Prep data for AI** features in both Power BI Desktop and the Power BI service. Users can consume these features anywhere Copilot in Power BI is available.

1. Select the **Prep data for AI** button located on the **Home** ribbon in Power BI Desktop, or on the ribbon on the selected semantic model in the Power BI service.

   [![Screenshot that shows the Prep Data for AI feature in Power BI Desktop.](media/copilot-prep-data/copilot-prep-data-ai.png)](media/copilot-prep-data/copilot-prep-data-ai.png#lightbox)

   If the tabs in **Prep data for AI** are disabled, enable Power BI Q&A for your model.

   [![Screenshot that shows how to enable Q&A for the model in Power BI Desktop.](media/copilot-prep-data/copilot-turn-on-qa.png)](media/copilot-prep-data/copilot-turn-on-qa.png#lightbox)
2. In the dialog, go to the **Add AI instructions** tab.
3. Provide instructions about the semantic model that help Copilot understand your business, terminology, and how to prioritize the data in the model.

   [![Screenshot that shows a dialog that features the AI instructions tab in Power BI Desktop.](media/copilot-prep-data/copilot-ai-instructions.png)](media/copilot-prep-data/copilot-ai-instructions.png#lightbox)
4. Select **Apply**.

After you close the dialog, your changes are saved to your model. Copilot now uses the AI instructions.

## Test AI instructions in Power BI Desktop

1. Open the **Copilot** pane in Power BI Desktop.
2. Use the **skill picker** to select the specific Copilot capability you want to test. For best results, choose **Answers questions about the data**.
3. Use one of the instructions that you set, and interact with Copilot.
4. Ensure that Copilot responds accurately.
5. If you need to change the instructions, reopen the **Prep data for AI** dialog and adjust them.
6. When you're satisfied with the AI instructions, publish your report to the Power BI service or save it in Power BI Desktop.

Note

Each time you edit an instruction in the **Prep data for AI** dialog, you need to refresh the Copilot pane by closing and reopening it.

## AI instructions after publishing

After your report is published to the Power BI service, or changes are saved in the service, users benefit from the AI instructions in every Copilot experience that uses the semantic model.

Note

End users can't see the AI instructions set on the model.

## Common use cases for AI instructions

AI instructions offer a flexible way to enhance how Copilot interprets and responds to user prompts. Two common use cases are general business context and data interpretation, and analysis rules.

### General business context and data interpretation

Instructions can help Copilot frame responses within the context of your business, tailoring answers based on your industry, strategic goals, terminology, or operational logic. When you use instructions, you can help ensure that users get more accurate and relevant insights. Some examples include:

- Busy season is October to February.
- Frame insights with a focus on risk assessment and market trends.
- When a user mentions *ABCD*, they're referring to the **total invoice** field.
- A lower attrition percent is more positive.

### Analysis rules

You can guide Copilot on how to approach certain types of analysis by providing rules and preferences for how data should be sliced or prioritized. Some examples include:

- Always analyze sales on a quarterly basis.
- When showcasing revenue, break it down by quarter and compare it to the `industry` field.
- For retail insights, prioritize the `customsegmentationtable` and `saleschannel` tables.
- Use the `sales_fact` table as the primary source for all sales-related questions.
- When a user asks about product sales, always ask for clarification on location.

## Write effective prompts for AI instructions

AI instructions are prompt-based, so prompt engineering best practices apply when you write them for a semantic model. Prompt construction directly affects Copilot outputs. The following tips help you get the most out of AI instructions.

### Be explicit and specific

Assume Copilot has no understanding of how to use the data model or business context for your data. For example, instead of writing "You're a seasoned BI Analyst who is detail-oriented," consider: "You're a seasoned BI Analyst who works for a big food distributor. Responses should be detail-oriented and focused on revenue and profitability."

### Use analogies and descriptive language

Analogies, descriptive language, and examples help Copilot understand your desired outcome and intended meaning. For example, for product-specific sales, use the measure `Total_Sales_Product` (example of product: Word, PowerPoint, Excel, SharePoint, Teams).

### Avoid ambiguity

Be clear about anything that you want Copilot to emphasize or avoid. The more details and supporting content you can provide Copilot, the better. For example, for `Total Active Partners`, use the measure `Monthly Active Partner Count`. (Don't filter on the **Customers** table.)

### Group related instructions

To help Copilot better understand your intent, organize instructions by theme or purpose (such as date logic, key metrics, and industry terms). Include structural elements, such as sections, hierarchies, and headers. For an example of how to group related instructions in the full set of instructions, see the [example scenario](#example-ai-instructions-for-a-sales-model).

### Instruction order

The order in which you author instructions can affect the output. You can boost your chances of getting correct outputs by testing different variations, orders, examples, and wording.

### Break down complex instructions into simpler steps

Break down instructions into simple steps to improve clarity and reduce errors. For example, define *top customers* by first looking at the revenue table and then returning only the customers with the highest order values.

### Keep instructions focused

Depending on the semantic model, fewer focused instructions can be more effective than many broad ones. Conflicts and complexity can cause confusion for large language models (LLMs).

## Example AI instructions for a sales model

The following example shows a set of AI instructions for a sales semantic model. Replace the object names and business rules with definitions that your semantic model implements.

```
Metrics
- When a user asks about "sales" or "revenue" without another qualifier,
  use [Net Sales].
- [Net Sales] is in USD, after discounts and returns, and excludes
  canceled orders.
- For margin percentage, use [Gross Margin %], not an average of
  transaction-level margin percentages.

Dates
- Use 'Date'[Date], related to order date, for sales analysis unless
  the user explicitly requests another date basis.
- The fiscal year starts on July 1 and is named for the year it ends.
  FY2027 means July 1, 2026 through June 30, 2027.

Ambiguity
- If "performance" could mean sales, growth, or margin and the question
  doesn't identify the metric, ask which measure the user wants.

Terminology
- "Top sellers" means the three partners with the highest [Net Sales].
  Don't show customers unless the user explicitly asks.

Customer identification
- 'Revenue'[accountid] identifies customers.
- 'Partners'[earningsid] identifies partners.
- 'Orders'[customid] doesn't identify customers.

Product metrics
- Filter 'Geography'[State] to "Washington" or "California" unless the
  user explicitly requests another state or asks for all states.
- For "Total Active Partners," use [Monthly Active Partner Count_ID].
  Don't filter on the 'Customers' table.
```

Note

You often need to iterate to get the most benefit from AI instructions. As you experiment and observe how Copilot responds, you develop a better understanding of what types of instructions drive the best outcomes for your model and your users.

## Considerations and limitations

- Because AI instructions are unstructured guidance to Copilot, the LLM only interprets them. There's no guarantee that the LLM will exactly follow instructions.
- AI instructions affect Copilot capabilities but don't extend to general conversations with Copilot.
- AI instructions are saved at the semantic model level. Instructions can't currently be stored at the report level.
- AI instructions aren't expected to be persona-specific or modify non-data-related outputs for the end user.
- AI instructions can't disable other Copilot in Power BI features or prevent/prioritize certain features from being called.
- Instructions aren't intended to work with visual modifications or theming in your report.
- Currently, you can't upload instructions to the dialog in Power BI Desktop.
- To test instructions in Power BI Desktop, you need to close and reopen your Copilot pane to see new instructions applied.
- Users can't set instructions by category or by mode (view or edit) in Copilot in Power BI.
- Consumers can't see what instructions an author applied to the model in the UI.
- End users can't disable instructions on a semantic model.
- AI instructions might not be respected in Power BI Desktop when you're trying to create a page, get suggested report page topics, or a semantic model summary with Copilot. To work around this issue, use the skill picker and select only **Create new report pages** to have instructions successfully apply.
- AI instructions are limited to 10,000 characters.

For a comprehensive list of considerations and limitations, see [Prepare your data for AI](copilot-prepare-data-ai#considerations-and-limitations).

## Related content

- [Prep data for AI](copilot-prepare-data-ai)
- [AI data schemas](copilot-prepare-data-ai-data-schema)
- [Verified answers](copilot-prepare-data-ai-verified-answers)
- [Prep data for AI FAQ](copilot-prepare-data-ai-faq)

---

- Last updated on 
  2026-09-29
