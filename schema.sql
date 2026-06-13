-- Enable uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the decisions table
CREATE TABLE IF NOT EXISTS public.decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    problem_description TEXT NOT NULL,
    context TEXT,
    options_considered TEXT,
    decision_taken TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    outcome TEXT,
    status VARCHAR(50) DEFAULT 'logged',
    vector_id VARCHAR(255)
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.decisions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for authenticated and anon users (MVP Hackathon Setup)
-- In a production environment, this should be restricted to authenticated users with specific roles.
DROP POLICY IF EXISTS "Allow public read access" ON public.decisions;
CREATE POLICY "Allow public read access" ON public.decisions FOR SELECT USING (true);
DROP POLICY IF EXISTS "Allow public insert access" ON public.decisions;
CREATE POLICY "Allow public insert access" ON public.decisions FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Allow public update access" ON public.decisions;
CREATE POLICY "Allow public update access" ON public.decisions FOR UPDATE USING (true);
DROP POLICY IF EXISTS "Allow public delete access" ON public.decisions;
CREATE POLICY "Allow public delete access" ON public.decisions FOR DELETE USING (true);
