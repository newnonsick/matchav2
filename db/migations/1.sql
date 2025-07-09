CREATE OR REPLACE FUNCTION get_attendance_by_date_channel(_date date, _channel_id text)
RETURNS TABLE(
    author_id text,
    leave_type text,
    partial_leave text,
    content text
) AS $$
BEGIN
    RETURN QUERY
    SELECT a.author_id, a.leave_type, a.partial_leave, a.content
    FROM attendance a
    JOIN member_team m ON a.author_id = m.author_id
    WHERE a.absent_date = _date AND m.channel_id = _channel_id;
END;
$$ LANGUAGE plpgsql STABLE;
