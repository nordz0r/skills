---
name: elk-kibana-dashboards
description: Work with Elasticsearch and Kibana for log analysis, observability triage, and dashboard design. Use when Codex needs to build or troubleshoot Kibana dashboards, Discover searches, Lens or TSVB visualizations, KQL or Lucene filters, Elasticsearch DSL aggregations, index templates, mappings, runtime fields, data views, alerts, or ELK-based investigations.
---

# ELK & Kibana Dashboards

Use this skill to turn monitoring or analytics questions into concrete Kibana
or Elasticsearch actions. Start from the data shape and the question, then use
the smallest Kibana surface that proves the answer.

## Core Workflow

1. Frame the question.
- Identify the metric or event, time window, filters, grouping dimensions, and
  audience.
- Convert vague requests into `measure + breakdown + filter + time`.

2. Validate the source data.
- Confirm the data view, index alias, or data stream.
- Inspect sample documents in Discover or Dev Tools before building charts.
- Verify the time field, timezone, field types, and missing-value behavior.

3. Choose the right surface.
- Use Discover to validate raw documents and filters.
- Use Lens for standard charts, tables, formulas, and quick dashboard panels.
- Use TSVB for time-series math, ratios, moving averages, and pipeline
  aggregations.
- Use Dev Tools when mappings, runtime fields, or DSL behavior must be explicit.
- Use Dashboard only after individual panels are already correct.

4. Build the query.
- Prefer KQL for dashboard and Discover filters.
- Use Lucene only when its query-string features are genuinely needed.
- Use Elasticsearch DSL for repeatable aggregation logic or debugging.

5. Verify and harden the result.
- Check `keyword` vs `text`, nested vs object semantics, auto interval, top-N
  bias, panel filters, and control interactions.
- Validate on a narrow time range first, then widen it.
- State assumptions and call out missing fields or mapping gaps.

## Decision Rules

- Prefer existing data views over ad hoc wildcard patterns.
- Prefer `field.keyword` for exact filters and terms aggregations.
- Avoid aggregating on high-cardinality runtime fields unless slower panels are
  acceptable.
- If a panel looks wrong, inspect mappings, filters, and the time picker before
  redesigning the visualization.
- If the user asks for a dashboard, propose the panel list, filters, and
  drilldowns before implementation details.

## Deliverables

Return only the artifacts needed for the task:

- A KQL or Lucene query for Discover or dashboard filters.
- An Elasticsearch DSL query for reproducible aggregation logic.
- A panel-by-panel dashboard plan with chart type, metric, split, and filters.
- A root-cause checklist when the issue is missing or incorrect data.
- Follow-up questions only when a field, index, or time dimension is truly
  unknown.

## Common Failure Modes

- Using `text` instead of `keyword` in exact filters or terms aggregations.
- Mixing query bar filters, filter pills, and panel-level filters.
- Forgetting timezone differences between ingestion and Kibana display.
- Treating arrays, objects, and nested fields as interchangeable.
- Relying on approximate cardinality without saying so.
- Comparing time windows without aligning interval and offset logic.

## References

Load [query-patterns.md](references/query-patterns.md) when ready-made
KQL/DSL patterns, dashboard templates, or troubleshooting checklists are useful.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: elasticsearch kibana elk kql lucene dsl lens tsvb dashboard logs index pattern filters aggregations time window visualization
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
