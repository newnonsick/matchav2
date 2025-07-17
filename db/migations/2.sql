create or replace function get_attendance_by_date(target_date date)
returns table (
  author_id text,
  leave_type text,
  partial_leave text,
  team_name text
)
language sql
as $$
  select
    a.author_id,
    a.leave_type,
    a.partial_leave,
    t.team_name
  from public.attendance a
  join public.member_team mt on a.author_id = mt.author_id 
  join public.team t on mt.channel_id = t.channel_id
  where a.absent_date = target_date
  order by t.team_name asc, mt.server_name asc;
$$;