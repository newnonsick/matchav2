CREATE TYPE user_role AS ENUM ('admin', 'user');

ALTER TABLE public.member_team
ADD COLUMN role user_role NOT NULL DEFAULT 'user';