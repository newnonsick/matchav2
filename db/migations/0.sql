CREATE TABLE public.attendance (
  created_at timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'Asia/Bangkok'::text),
  author_id text NOT NULL,
  content text NOT NULL,
  absent_date date NOT NULL,
  leave_type text NOT NULL,
  message_id text NOT NULL,
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  partial_leave text,
  channel_id text NOT NULL,
  CONSTRAINT attendance_pkey PRIMARY KEY (absent_date, message_id, id)
);
CREATE TABLE public.team (
  timestamp timestamp with time zone,
  channel_id text NOT NULL,
  team_name text NOT NULL,
  server_id text NOT NULL,
  server_name text NOT NULL,
  CONSTRAINT team_pkey PRIMARY KEY (channel_id)
);
CREATE TABLE public.member_team (
  channel_id text NOT NULL,
  author_id text NOT NULL,
  server_name text NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT member_team_pkey PRIMARY KEY (channel_id, author_id),
  CONSTRAINT member_team_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.team(channel_id)
);
CREATE TABLE public.message (
  timestamp timestamp with time zone NOT NULL,
  message_id text NOT NULL,
  author_id text NOT NULL,
  username text NOT NULL,
  servername text NOT NULL,
  channel_id text NOT NULL,
  content text NOT NULL,
  CONSTRAINT message_pkey PRIMARY KEY (message_id, author_id),
  CONSTRAINT message_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.team(channel_id)
);