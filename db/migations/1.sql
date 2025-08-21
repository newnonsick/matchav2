CREATE TABLE public.team (
  channel_id text NOT NULL PRIMARY KEY,
  team_name text NOT NULL,
  timestamp timestamp with time zone NOT NULL DEFAULT now(),
  server_id text NOT NULL,
  server_name text NOT NULL
);

CREATE TYPE leave_type_enum AS ENUM (
  'annual_leave',
  'sick_leave',
  'personal_leave',
  'birthday_leave'
);

CREATE TYPE partial_leave_enum AS ENUM (
  'morning',
  'afternoon'
);

CREATE TABLE public.attendance (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  absent_date date NOT NULL,
  message_id text NOT NULL,
  channel_id text NOT NULL,
  content text NOT NULL,
  leave_type leave_type_enum NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  partial_leave partial_leave_enum,
  author_id text NOT NULL,
  CONSTRAINT attendance_pkey PRIMARY KEY (absent_date, message_id, id)
);

CREATE TYPE user_role AS ENUM ('admin', 'user');

CREATE TABLE public.member_team (
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  role user_role NOT NULL DEFAULT 'user'::user_role,
  channel_id text NOT NULL,
  author_id text NOT NULL,
  server_name text NOT NULL,
  CONSTRAINT member_team_pkey PRIMARY KEY (channel_id, author_id),
  FOREIGN KEY (channel_id) REFERENCES public.team(channel_id)
);

CREATE TABLE public.message (
  timestamp timestamp with time zone NOT NULL DEFAULT now(),
  message_id text NOT NULL,
  author_id text NOT NULL,
  username text,
  servername text,
  channel_id text NOT NULL,
  content text NOT NULL,
  CONSTRAINT message_pkey PRIMARY KEY (message_id, author_id),
  FOREIGN KEY (channel_id) REFERENCES public.team(channel_id)
);

CREATE TABLE public.office_entries (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  author_id text NOT NULL,
  message_id text,
  date date NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  UNIQUE (author_id, date),
  FOREIGN KEY (message_id, author_id) REFERENCES public.message (message_id, author_id) ON DELETE CASCADE
);

CREATE TABLE public.company_holidays (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  holiday_date date UNIQUE NOT NULL,
  description text NOT NULL
);

CREATE TABLE public.attendance_activity (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
  author_id TEXT NOT NULL, 
  event_time TIMESTAMP WITH TIME ZONE NOT NULL, 
  event_type VARCHAR(5) CHECK (
    event_type IN ('join', 'leave')
  ), 
  date DATE NOT NULL
);

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE standup_task_status AS ENUM ('todo', 'in_progress', 'done');

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  message_id TEXT NOT NULL,
  author_id TEXT NOT NULL,
  task TEXT NOT NULL,
  status standup_task_status NOT NULL DEFAULT 'todo',
  FOREIGN KEY (message_id, author_id) REFERENCES public.message (message_id, author_id) ON DELETE CASCADE
);

-- ALTER TABLE public.team ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.member_team ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.message ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.attendance ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.office_entry ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.company_holidays ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.attendance_activity ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
