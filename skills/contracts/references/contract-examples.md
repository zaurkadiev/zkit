# Spec skeletons and the extensions the checker reads

Put one file per boundary in `contracts/`, named `x-<n>-<slug>.yaml` (or `.md` for a card). Extensions at the top level of every spec:
`x-boundary: X-1` · `x-direction: published|consumed` · `x-serves: [FR-1, NFR-4]` · `x-limits: [L-1]` (resource-math ids; empty only when truly none) · `x-status: draft` (optional) · consumed only: `x-verified: {status: verified|unverified, source: "R-1 or URL", date: 2026-10-16}`. Every non-GET operation: `x-idempotency: key|natural|none` with a one-line reason in its description.

## Published HTTP (OpenAPI 3.1)
```yaml
openapi: 3.1.0
info: {title: Owner API, version: "0.1.0"}
x-boundary: X-1
x-direction: published
x-serves: [FR-1]
x-limits: [L-1]
security: [{bearer: []}]
components:
  securitySchemes: {bearer: {type: http, scheme: bearer}}
  schemas:
    Goal:
      type: object
      required: [title]
      properties: {title: {type: string, maxLength: 200}, budgetUsd: {type: number, minimum: 0}}
    Error:
      type: object
      required: [code, message]
      properties: {code: {type: string}, message: {type: string}}
paths:
  /goals:
    post:
      operationId: createGoal
      x-idempotency: key        # Idempotency-Key header; a retry returns the first result
      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: "#/components/schemas/Goal"}
            example: {title: "Find 20 leads", budgetUsd: 15}
      responses:
        "201": {description: created}
        "422": {description: invalid, content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
        "429": {description: rate limited, retry after the Retry-After header}
```

## Consumed events or messages (AsyncAPI 3)
```yaml
asyncapi: 3.0.0
info: {title: Provider usage events, version: "1.0"}
x-boundary: X-2
x-direction: consumed
x-verified: {status: verified, source: "R-1", date: 2026-10-16}
x-serves: [FR-5]
x-limits: [L-2]
channels:
  usage:
    address: usage
    messages:
      usageReported:
        payload:
          type: object
          required: [promptTokens, completionTokens]
          properties: {promptTokens: {type: integer}, completionTokens: {type: integer}}
        examples:
          - payload: {promptTokens: 1200, completionTokens: 340}
```

## Card for registers, bus frames, binary layouts (`contracts/x-3-midi-uart.md`)
Markdown with sections matching `layout`, `timing and limits`, `errors`; first lines carry `x-boundary`, direction, serves, limits as `key: value`. Layout is a table of byte/bit ranges, names, units, ranges; timing gives rates, deadlines, windows with the resource-math `L-n`; errors say what the receiver does with a malformed or missing frame.
