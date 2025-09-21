import { createClient } from '@supabase/supabase-js';

// Read env vars (CRA requires REACT_APP_ prefix)
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnon = process.env.REACT_APP_SUPABASE_ANON_KEY;

// Runtime validation + diagnostic logging (will run once on import)
if (!supabaseUrl || !supabaseAnon) {
  // Detailed diagnostics to help during Docker build
  // (Do NOT print full anon key in case logs are stored)
  console.error(
    '❌ Supabase env vars missing.',
    {
      hasUrl: !!supabaseUrl,
      hasAnonKey: !!supabaseAnon,
      urlSample: supabaseUrl ? supabaseUrl.slice(0, 24) + '...' : null,
    }
  );
  throw new Error('Supabase environment variables are not set. Check .env / Docker build args.');
} else {
  console.log(
    '🔐 Supabase env vars loaded.',
    {
      urlHost: (() => { try { return new URL(supabaseUrl).host; } catch { return 'invalid-url'; } })(),
      anonKeyPrefix: supabaseAnon.substring(0, 8) + '…',
      anonKeyLength: supabaseAnon.length
    }
  );
}

// TypeScript: after the guard these are narrowed to string
export const supabase = createClient(supabaseUrl, supabaseAnon, {
  auth: { persistSession: true, autoRefreshToken: true },
});