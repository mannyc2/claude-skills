# neon vpc

Manage VPC endpoints and project VPC restrictions for Private Networking.

## Subcommands

### vpc endpoint

Manage VPC endpoints at the organization level.

| Subcommand | Description |
|------------|-------------|
| `list` | List VPC endpoints |
| `assign` | Add/update VPC endpoint (aliases: `add`, `update`) |
| `remove` | Delete VPC endpoint |
| `status` | Check endpoint status |

**Required options:**
- `--org-id` - Organization ID (if multiple orgs)
- `--region-id` - AWS or Azure region

**Supported regions:**
- AWS: `aws-us-west-2`, `aws-us-east-1`, `aws-us-east-2`, `aws-eu-central-1`, `aws-ap-southeast-1`, `aws-ap-southeast-2`
- Azure: `azure-eastus2`

**Examples:**
```bash
# List endpoints
neon vpc endpoint list --org-id org-xxx --region-id aws-us-east-1

# Assign endpoint
neon vpc endpoint assign vpce-1234567890abcdef0 --org-id org-xxx --region-id aws-us-east-1

# Check status
neon vpc endpoint status vpce-1234567890abcdef0 --org-id org-xxx --region-id aws-us-east-1

# Remove endpoint
neon vpc endpoint remove vpce-1234567890abcdef0 --org-id org-xxx --region-id aws-us-east-1
```

### vpc project

Manage VPC endpoint restrictions at the project level.

| Subcommand | Description |
|------------|-------------|
| `list` | List restrictions |
| `restrict` | Add/update restriction (alias: `update`) |
| `remove` | Remove restriction |

**Required options:**
- `--project-id` - Project ID

**Examples:**
```bash
# List restrictions
neon vpc project list --project-id orange-credit-12345678

# Add restriction
neon vpc project restrict vpce-1234567890abcdef0 --project-id orange-credit-12345678

# Remove restriction
neon vpc project remove vpce-1234567890abcdef0 --project-id orange-credit-12345678
```
