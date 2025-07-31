create or replace function get_daily_office_entries(target_date date)
returns table (
  author_id text,
  server_name text,
  team_name text
)
language sql
as $$
  select
    oe.author_id,
    mt.server_name,
    t.team_name
  from public.office_entries oe
  join public.member_team mt on oe.author_id = mt.author_id
  join public.team t on mt.channel_id = t.channel_id
  where oe.date = target_date
  order by t.team_name asc, mt.server_name asc;
$$;