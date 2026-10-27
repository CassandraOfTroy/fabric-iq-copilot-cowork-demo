Source: https://learn.microsoft.com/power-bi/create-reports/copilot-ask-data-question
Fetched: 2026-10-13

# Ask data questions with Copilot and Fabric IQ

Table of contents 

Exit editor mode

---

Note

Access to this page requires authorization. You can try [signing in](#) or changing directories.

Access to this page requires authorization. You can try changing directories.

# Ask data questions with Copilot and Fabric IQ

**Applies to:** â Power BI service

[Copilot for Power BI](copilot-introduction) lets you ask natural-language questions about your data and summarize report content. This article explains the Fabric IQ experience in the Copilot pane when you view a report in the Power BI service, including supported questions, ad hoc DAX calculations, and result verification.

[![Screenshot of Fabric IQ answer from the Copilot report pane (viewing mode) to the question 'Show monthly sales trends for each chain in a line chart.'](media/copilot-ask-data-questions/fabric-iq-line-chart-answer.png)](media/copilot-ask-data-questions/fabric-iq-line-chart-answer.png#lightbox)

## Prerequisites

Before you can use this feature, make sure you satisfy the [requirements for the use of Copilot](copilot-introduction#copilot-requirements).

Note

Keep the following requirements in mind:

- Your administrator needs to [enable Copilot in Microsoft Fabric](/en-us/fabric/get-started/copilot-fabric-overview#enable-copilot).
- Your Fabric capacity needs to be in one of the regions listed in this article, [Fabric region availability](/en-us/fabric/admin/region-availability). If it isn't, you can't use Copilot.
- Your administrator needs to enable the tenant switch before you start using Copilot. See the article [Copilot tenant settings](/en-us/fabric/admin/service-admin-portal-copilot) for details.
- If your tenant or capacity is outside the United States or EU data boundary, Copilot is disabled by default. The one exception is if your Fabric tenant admin enables the [Data sent to Azure OpenAI can be processed outside your tenant's geographic region, compliance boundary, or national cloud instance](/en-us/fabric/admin/service-admin-portal-copilot) tenant setting. You can find this setting in the Fabric admin portal.
- Copilot in Microsoft Fabric isn't supported on trial SKUs. Only paid SKUs are supported.
- To see the standalone Copilot experience in Power BI, your tenant admin needs to enable the tenant switch.

You need to enable Q&A for your model because Copilot uses the same underlying engine to build queries from your inputs. For most data sources, Q&A is enabled by default.

For some sources, such as DirectQuery or Direct Lake models, you might need to enable Q&A manually, either in your semantic model settings in the Power BI service or in your Data Load settings in Power BI Desktop. To learn more about the types of data sources Q&A supports, see [Data sources for natural language Q&A](../natural-language/q-and-a-data-sources).

Note

You can also configure these settings in the [semantic model settings pane](../connect-data/service-semantic-model-settings-pane), a side pane that opens on the right side of the page. **The settings pane is currently in preview** and features or behavior might change before general availability.

## Feature availability

You can use Copilot data questions in both view and edit modes in the Power BI service. Both report authors and report viewers can ask Copilot data questions related to their semantic model or report.

## Enhanced data question answering with Fabric IQ

When you view a Power BI report, you can turn on Fabric IQ from the Copilot pane to get better answers to questions about your data. This enhancement brings existing [Fabric IQ](/en-us/fabric/iq/connectors/microsoft-365-copilot-overview) capabilities into Power BI Copilot report viewing mode, so Copilot can use a multistep approach to evaluate data in the semantic model and refine its approach when generating a response.

[![Screenshot of Fabric IQ teaching popover from the Copilot report pane (viewing mode).](media/copilot-ask-data-questions/fabric-iq-toggle-teaching-popover.png)](media/copilot-ask-data-questions/fabric-iq-toggle-teaching-popover.png#lightbox)

With Fabric IQ enabled, Copilot can:

- Provide better answers to questions about your data based on detailed reasoning capabilities directly into the report viewing experience.
- Show reasoning steps so you can understand how Copilot arrived at an answer and inspect the conversation in more detail. You can verify the calculations and filters used and confirm that the explanation aligns with the returned data.
- Generate Fabric visuals to help you further analyze your data. Answers can include column, bar, stacked bar/column, line, area, pie, donut, scatter visuals.
- Provide the underlying DAX query and data table used to generate a response.

[![Screenshot of Fabric IQ enabled in the Copilot pane showing an operating expenses response and stacked bar chart.](media/copilot-ask-data-questions/fabric-iq-report-pane-example.png)](media/copilot-ask-data-questions/fabric-iq-report-pane-example.png#lightbox)

Expand each reasoning step to understand how Copilot arrived at its answer, including the sequence of analysis steps, the generated DAX query, and the query results used to produce the response.

[![Screenshot of Fabric IQ reasoning steps.'](media/copilot-ask-data-questions/fabric-iq-reasoning-steps.png)](media/copilot-ask-data-questions/fabric-iq-reasoning-steps.png#lightbox)

Use the display options picker to switch between viewing the results as a visual, table, or DAX query.

[![Screenshot of the Fabric IQ display options picker.](media/copilot-ask-data-questions/fabric-iq-display-options.png)](media/copilot-ask-data-questions/fabric-iq-display-options.png#lightbox)

Note

Fabric IQ is currently available only when viewing reports in the Power BI service. It doesn't apply to report editing experiences. When Fabric IQ is enabled, Copilot doesn't return [verified answers](copilot-prepare-data-ai-verified-answers).

## Prepare the semantic model for Fabric IQ

Fabric IQ uses the measures, relationships, and business definitions in your semantic model to answer questions. Review your semantic model and test the questions that are most important to your organization. Define business meaning in the semantic model, add context with [Prep data for AI](copilot-prepare-data-ai), and compare responses with validated results.

- Identify a representative set of business questions to test.
- Define the expected measure, grouping, date context, filters, and result for each question.
- Compare the responses with known, validated results.
- If your model contains organization-specific terminology, preferred analytical defaults, or potential ambiguities, use [Prep data for AI](copilot-prepare-data-ai) to provide more context.

For model structure, measures, names, data quality, security, and metadata, see [Optimize your semantic model for Copilot in Power BI](copilot-evaluate-data). For AI data schemas, AI instructions, testing, and approval, see [Prepare your data for AI](copilot-prepare-data-ai).

## Supported question types

Copilot can answer questions by using existing measures and columns in your semantic model. It can also generate DAX queries for ad hoc calculations, as described in the following section. Questions might include existing measures filtered to a different region or time period than what appears on the report, a metric split into categories, or how a measure changes over time.

Although the exact questions that Copilot can answer depend on the specifics of your model, here are some examples:

- **"Can you show me sales amount by region?"**

  Both sales amount and region are already columns in the data.
- **"What were the top 5 selling products in North America last month?"**

  Product, region, and date are already columns in the data. Copilot helps with top N filtering to produce the visual.
- **"Tell me the average price of gasoline per gallon over the last 30 days."**

  Price per gallon is a measure already contained in the model. Copilot takes the average and filters by relative date to produce the visual.
- **"Which customers bought cheese and wine?"**

  Cheese and wine are multiple instances from the same Product entity in the model.

Copilot also responds to follow-up requests based on what you already asked in your current session.

[![Screenshot of a follow-up question in the Copilot pane.](media/copilot-ask-data-questions/data-question-follow-up-02.png)](media/copilot-ask-data-questions/data-question-follow-up-02.png#lightbox)

## Ad hoc calculations for data questions

Copilot can also generate DAX queries to answer questions that require ad hoc calculations, such as creating new measures that aren't contained in the model. Examples of questions that Copilot can answer by creating a DAX query include the following:

- What was the year-over-year growth for sales?
- How many employees were hired before 2020?
- Calculate the ratio of cosmetic product orders to all products.
- Which customers didn't buy any products?

You can also verify the DAX query directly from the expanded view or launch the DAX query view for further inspection.

![Screenshot of Copilot answering a question by creating a DAX query.](media/copilot-ask-data-questions/data-question-answers-01.png)

## Unsupported question types

Copilot can't currently answer questions that require generating new insights, such as anomaly detection, forecasting, or finding key influencers. The specific questions it can handle depend on your model and report visuals. However, here are some examples of unsupported questions:

- **"Why do our sales go down every July?"**

  This question involves generating deeper insights from the provided data.
- **"How many books do you think we will sell next year?"**

  This question asks for forecasting, which isn't currently supported.

## Read the Copilot answer

If Fabric IQ isn't enabled, expand **How Copilot arrived at this** to review how Copilot interpreted your question and verify the fields, measures, and filters it selected from the semantic model.

[![Screenshot of the show reasoning section of a visual answer.](media/copilot-ask-data-questions/data-question-show-reasoning-02.png)](media/copilot-ask-data-questions/data-question-show-reasoning-02.png#lightbox)

Select the link beside a **Data used** element to see more detail, as shown in the following image.

[![Screenshot of the data details for a visual answer.](media/copilot-ask-data-questions/data-question-show-reasoning-details.png)](media/copilot-ask-data-questions/data-question-show-reasoning-details.png#lightbox)

You can also expand the visual to see it in more detail. As a report author, you can add these visuals directly to your report page by selecting **Add to page** below the visual.

[![Screenshot of the expand and add to page buttons of a visual answer.](media/copilot-ask-data-questions/data-question-expand-02.png)](media/copilot-ask-data-questions/data-question-expand-02.png#lightbox)

## Improve answer quality with linguistic modeling

When Copilot builds visuals from data in your semantic model, it references field names to determine which data might answer your question. Power BI authors can use linguistic modeling to improve Copilot's understanding of the questions report viewers might ask.

Authors can guide Copilot in the following ways:

- Use unique and descriptive column and measure names so Copilot understands the data.
- Structure the model according to Power BI best practices.
- Add synonyms to data field names to clarify business-specific terms for Copilot.

To learn more about linguistic modeling, see [Intro to Q&A tooling to train Power BI Q&A](/en-us/power-bi/natural-language/q-and-a-tooling-intro).

## Limitations and considerations

Consider the following factors when you use Copilot data questions:

- Copilot data questions are only available in the Power BI service. Support for Power BI Desktop is coming soon.
- The only supported language is English.
- Copilot data questions don't apply filters or slicers currently affecting visuals on the report page to the answers generated in the Copilot pane.
- The requirement to enable Q&A is unique to Copilot data questions. You can still use Copilot for other tasks, like [asking questions about content present in your report](../explore-reports/copilot-pane-summarize-content#answer-questions-about-your-report-content-in-the-copilot-pane).
- When a question is related to data in the semantic model, Copilot uses the semantic model to answer the question. Otherwise, it might answer from the [large language model's (LLM's) general knowledge](https://go.microsoft.com/fwlink/p/?linkid=2325401).
- Percentage values might be formatted differently between Copilot-generated text responses and Copilot-generated data tables. Table values use the formatting defined in the semantic model.
- For additional limitations on data sources, see [Limitations of Power BI Q&A](../natural-language/q-and-a-limitations).

## Next steps

- [Overview of Copilot for Power BI](copilot-introduction)
- [Create reports with Copilot](copilot-create-reports)
- [Summarize and ask questions about report content](../explore-reports/copilot-pane-summarize-content)
- [Intro to Q&A tooling to train Power BI Q&A](../natural-language/q-and-a-tooling-intro)
- [Limitations of Power BI Q&A](../natural-language/q-and-a-limitations)

---

- Last updated on 
  2026-09-29
