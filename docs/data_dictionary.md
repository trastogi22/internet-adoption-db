# Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| firm_name_raw | str | Name exactly as in source |
| firm_name_clean | str | Standardized name |
| network | str | Specific network (JvNCnet, BITNET, etc.) |
| network_category | str | Grouping (regional IP, UUCP mail, academic) |
| connection_date | str | YYYY-MM |
| date_precision | str | month / quarter / year |
| event_type | str | new member / operational / allocation / upgrade |
| location_raw | str | Location as in source |
| city | str | Parsed city |
| state | str | Parsed state/region |
| country | str | Parsed country |
| source | str | Short source ID |
| source_url | str | Link |
| source_quote | str | Verbatim text from source |
| confidence | str | high / medium / low |
| notes | str | Free text |