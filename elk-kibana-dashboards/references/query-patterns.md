# Query Patterns

## Choose the Query Surface

- Use `KQL` for filtering in Discover, dashboards, and controls.
- Use `Lucene` only for query-string features such as regex or fuzzy matching.
- Use Elasticsearch `DSL` when aggregations, pipeline math, scripted logic, or
  reproducibility matter more than convenience.

## Common KQL Patterns

### Error Logs

```text
service.name: "api" and log.level: ("ERROR" or "FATAL")
```

### Failed Login Attempts

```text
event.action: "login" and event.outcome: "failure"
```

### Requests Above a Latency Threshold

`event.duration` is often stored in nanoseconds. Adjust the threshold to the
actual unit in the index.

```text
service.name: "checkout" and event.duration >= 1000000000
```

### Exact vs Full-Text Fields

- Use `user.email.keyword: "a@b.com"` for exact match and aggregations.
- Use `message: "timeout"` for text search when analyzed matching is acceptable.

## Common DSL Patterns

### Log Volume by Level Over Time

```json
{
  "size": 0,
  "query": {
    "bool": {
      "filter": [
        { "range": { "@timestamp": { "gte": "now-24h" } } },
        { "term": { "service.name.keyword": "api" } }
      ]
    }
  },
  "aggs": {
    "per_minute": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "1m"
      },
      "aggs": {
        "by_level": {
          "terms": {
            "field": "log.level.keyword",
            "size": 10
          }
        }
      }
    }
  }
}
```

### Error Rate Ratio

Use filters aggregation when the numerator and denominator differ only by
conditions.

```json
{
  "size": 0,
  "query": {
    "range": { "@timestamp": { "gte": "now-1h" } }
  },
  "aggs": {
    "requests": {
      "filters": {
        "filters": {
          "all": { "match_all": {} },
          "errors": { "terms": { "http.response.status_code": [500, 502, 503, 504] } }
        }
      }
    }
  }
}
```

Turn the result into a ratio in Lens Formula, TSVB, or application code.

### Top Endpoints by P95 Latency

```json
{
  "size": 0,
  "query": {
    "bool": {
      "filter": [
        { "range": { "@timestamp": { "gte": "now-24h" } } },
        { "term": { "service.name.keyword": "api" } }
      ]
    }
  },
  "aggs": {
    "endpoints": {
      "terms": {
        "field": "url.path.keyword",
        "size": 20
      },
      "aggs": {
        "p95_latency": {
          "percentiles": {
            "field": "event.duration",
            "percents": [95]
          }
        }
      }
    }
  }
}
```

## Dashboard Design Templates

### Service Health Dashboard

- Total request volume over time.
- Error rate over time.
- P95 or P99 latency by endpoint.
- Top failing routes or exception classes.
- Recent error documents in a table with drilldown to Discover.

### Authentication Dashboard

- Successful vs failed login trend.
- Top usernames or clients by failures.
- Geo or source IP breakdown.
- Spike detector panel for anomaly windows.
- Raw events table filtered to failures.

### ETL or Batch Dashboard

- Job run count by status.
- Processing duration percentile trend.
- Lag between event creation and ingestion.
- Top failing pipelines or stages.
- Latest failed runs with error payload excerpts.

## Troubleshooting Checklist

When a panel is empty, wrong, or inconsistent:

1. Confirm the selected data view points to the intended index or data stream.
2. Confirm the time picker matches the document timestamps and timezone.
3. Inspect one raw document in Discover and note exact field names and types.
4. Check whether the field is `text`, `keyword`, numeric, date, object, or
   nested.
5. Compare dashboard-level filters, control filters, and panel filters.
6. Reduce the query to the smallest time window and simplest filter that still
   reproduces the issue.
7. Re-run the logic in Dev Tools as DSL if Lens behavior is ambiguous.
8. State whether approximation, sampling, or missing data can explain the gap.
