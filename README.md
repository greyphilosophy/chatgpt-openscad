# chatgpt-openscad

ChatGPT-facing packaging and deployment for a mature OpenSCAD MCP backend.

## Pivot

This repository intentionally does **not** implement another OpenSCAD engine or duplicate mature MCP CAD tooling.

The initial backend is [`openscad-mcp-server`](https://pypi.org/project/openscad-mcp-server/), which owns OpenSCAD authoring, compilation, rendering, inspection, measurement, and library workflows.

This repository owns the integration layer needed to make that capability safe and convenient for ChatGPT:

- expose the upstream stdio MCP server through current Streamable HTTP
- package the service for private testing and eventual ChatGPT publication
- add authentication, rate/resource limits, and per-user/session isolation before public use
- maintain black-box regression tests against the upstream server
- document deployment and operational security
- add ChatGPT-specific UI/Apps SDK work only where it improves the collaborative CAD experience

## Target architecture

```text
ChatGPT / Plugin
      |
      | Streamable HTTP
      v
Gateway / auth / isolation
      |
      v
stdio<->HTTP MCP bridge
      |
      v
openscad-mcp-server
      |
      v
OpenSCAD container workers
```

## First milestone

Prove the upstream MCP server can be launched unchanged, bridged to Streamable HTTP, and exercised through a black-box MCP client. Do not add CAD behavior to this repository to make that test pass.

## Upstream policy

Prefer configuration, adapters, and upstream contributions over local forks. Pin tested upstream versions for reproducibility, and keep compatibility tests so upstream upgrades are deliberate.
