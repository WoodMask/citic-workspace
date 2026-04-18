---
name: serpapi-search
description: |
  Search the web using SerpAPI (Google search). Use this skill when the user wants to search the web, find information, look up news, or needs current information from the internet. Returns Google search results with titles, links, snippets, and metadata.
allowed-tools: Bash
---

# SerpAPI Search

Web search via SerpAPI returning Google search results.

## Configuration

API key is stored in `~/.claude/settings.json` under `SERPAPI_KEY`.

## Usage

```bash
# Basic search
$query = [uri]::EscapeDataString("your search query")
Invoke-RestMethod -Uri "https://serpapi.com/search.json?q=$query&engine=google&api_key=$env:SERPAPI_KEY"
```

## Quick Start

```powershell
# Set API key
$env:SERPAPI_KEY = "your-api-key"

# Search
$query = [uri]::EscapeDataString("AI news")
$results = Invoke-RestMethod -Uri "https://serpapi.com/search.json?q=$query&engine=google&api_key=$env:SERPAPI_KEY"

# Get organic results
$results.organic_results | ForEach-Object { Write-Host "$($_.title): $($_.link)" }
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL encoded) |
| `engine` | Search engine (default: `google`) |
| `api_key` | Your SerpAPI key |
| `num` | Number of results (default: 10) |
| `start` | Result offset for pagination |

## Response Fields

- `organic_results` - Main search results
  - `position` - Result ranking
  - `title` - Page title
  - `link` - URL
  - `snippet` - Text preview
  - `displayed_link` - Display URL
- `knowledge_graph` - Google Knowledge Graph info
- `related_questions` - "People also ask" questions
- `local_results` - Local business results

## Examples

### Search for news
```powershell
$query = [uri]::EscapeDataString("latest AI developments")
Invoke-RestMethod -Uri "https://serpapi.com/search.json?q=$query&engine=google&api_key=$env:SERPAPI_KEY"
```

### Search with more results
```powershell
$query = [uri]::EscapeDataString("python tutorial")
Invoke-RestMethod -Uri "https://serpapi.com/search.json?q=$query&engine=google&api_key=$env:SERPAPI_KEY&num=20"
```
