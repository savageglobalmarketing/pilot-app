# Supabase Setup (Day 1 — run when the project exists)

The canonical schema is `~/apps/sgm-agent-sprint/infra/schema.sql`. It is not
copied into this repo to avoid drift — run it from there.

## Steps
1. Create a new Supabase project at supabase.com (SGM account). Region: closest
   to the team.
2. Open **SQL Editor** → paste the full contents of `infra/schema.sql` → Run.
   Creates: `pods, agents, tasks, approvals, events, cost_log`, the
   `pod_spend_today` view, the `touch_updated_at` trigger, and RLS policies
   (read for authenticated, writes service-role only).
3. **Enable Realtime** on `agents`, `tasks`, `approvals`
   (Database → Replication → supabase_realtime → add those tables).
4. Seed pod row (SQL Editor):
   ```sql
   insert into pods (name, repo, daily_cap_usd, hard_cap_usd)
   values ('pilot-app', 'savageglobalmarketing/pilot-app', 50, 100);
   ```

## Credentials — where they go (never commit)
| Value | Used by | Store as |
|---|---|---|
| `SUPABASE_URL` | dashboard, n8n | env var / n8n credential |
| Supabase **service role** key | n8n writes, decision API | n8n credential store only |
| Supabase **anon** key | dashboard (read via RLS) | Netlify env var |

Do not paste the service key into chat or any committed file. Set it in the
runner shell env and n8n's credential store.
