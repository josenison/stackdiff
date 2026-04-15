# stackdiff

> CLI tool to compare deployed cloud infrastructure states across environments using provider APIs

## Installation

```bash
pip install stackdiff
```

## Usage

Compare infrastructure states between two environments:

```bash
stackdiff compare --source production --target staging --provider aws
```

**Example output:**

```
[+] aws_s3_bucket.assets       present in production / missing in staging
[~] aws_rds_instance.db        instance_type: db.t3.large → db.t3.medium
[-] aws_lambda_function.worker present in staging / missing in production
```

### Common Options

| Flag | Description |
|------|-------------|
| `--provider` | Cloud provider (`aws`, `gcp`, `azure`) |
| `--source` | Source environment to compare from |
| `--target` | Target environment to compare against |
| `--output` | Output format: `table` (default), `json`, `yaml` |
| `--filter` | Filter by resource type (e.g. `aws_s3_bucket`) |

### More Examples

```bash
# Compare specific resource types
stackdiff compare --source prod --target dev --filter aws_lambda_function

# Output as JSON
stackdiff compare --source prod --target staging --output json > diff.json

# List available environments
stackdiff envs --provider aws
```

## Requirements

- Python 3.9+
- Configured cloud provider credentials (e.g. AWS CLI, GCP ADC)

## License

MIT © 2024 stackdiff contributors