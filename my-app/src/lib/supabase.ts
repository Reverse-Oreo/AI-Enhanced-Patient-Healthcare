import { createClient } from '@supabase/supabase-js';

const supabaseUrl  = "https://qtvzucfovwaxxagyknjd.supabase.co";
const supabaseAnon = process.env.REACT_APP_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnon, {
  auth: { persistSession: true, autoRefreshToken: true },
});
