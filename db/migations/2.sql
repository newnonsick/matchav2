CREATE TABLE public.attendance_activity (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
  author_id TEXT NOT NULL, 
  event_time TIMESTAMPTZ NOT NULL, 
  event_type VARCHAR(5) CHECK (
    event_type IN ('join', 'leave')
  ), 
  date DATE NOT NULL
);

-- ALTER TABLE public.attendance_activity ENABLE ROW LEVEL SECURITY;